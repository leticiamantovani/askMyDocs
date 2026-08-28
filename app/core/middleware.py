import logging

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

# Multipart framing adds boundary and header bytes on top of the file itself,
# so the body allowance sits above the file limit to keep a legal upload legal.
MULTIPART_OVERHEAD = 1024 * 1024


class UploadSizeLimit:
    """Turn away oversized uploads before the multipart parser buffers them.

    Raw ASGI rather than BaseHTTPMiddleware on purpose: BaseHTTPMiddleware wraps
    every response in an extra task and memory stream, which the token-by-token
    chat stream would pay for on every request to guard a single route.

    Content-Length is client-supplied, so this only spares honest clients a
    pointless spool to disk. The authoritative check is in upload_pdf_service,
    which measures the body that actually arrived.
    """

    def __init__(
        self,
        app: ASGIApp,
        path: str,
        max_bytes: int,
        overhead: int = MULTIPART_OVERHEAD,
    ) -> None:
        self.app = app
        self.path = path
        self.max_bytes = max_bytes
        self.body_allowance = max_bytes + overhead

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] != self.path:
            await self.app(scope, receive, send)
            return

        declared = _declared_length(scope)
        if declared is not None and declared > self.body_allowance:
            limit_mb = self.max_bytes // (1024 * 1024)
            logger.warning("upload rejected before buffering declared=%d", declared)
            response = JSONResponse(
                status_code=413,
                content={"detail": f"PDF is larger than the {limit_mb}MB limit."},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


def _declared_length(scope: Scope) -> int | None:
    for name, value in scope.get("headers", []):
        if name == b"content-length":
            try:
                return int(value)
            except ValueError:
                return None
    return None

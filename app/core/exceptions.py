class DomainError(Exception):
    """Base for business rule errors"""
    status_code: int = 400

    def __init__(self, message: str = "", status_code: int | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(DomainError):
    """Entity not found."""
    status_code = 404


class ValidationError(DomainError):
    """Invalid input or business rule violation."""
    status_code = 400


class PayloadTooLargeError(DomainError):
    """Request body or uploaded file exceeds the allowed size."""
    status_code = 413


class ConflictError(DomainError):
    """Resource conflict (e.g. duplicate)."""
    status_code = 409


class PermissionDeniedError(DomainError):
    """Caller is not allowed to perform this action."""
    status_code = 403


class ConversationNotFoundError(NotFoundError):
    pass

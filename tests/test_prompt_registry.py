from app.services.prompt_registry import PromptRegistry


def test_resolve_flag_no_experiment_returns_none():
    result = PromptRegistry._resolve_flag("any-user-id")
    assert result is None


def test_resolve_flag_zero_rollout_returns_none(monkeypatch):
    monkeypatch.setenv("PROMPT_EXPERIMENT_VERSION", "v2")
    monkeypatch.setenv("PROMPT_EXPERIMENT_ROLLOUT", "0")
    assert PromptRegistry._resolve_flag("any-user-id") is None


def test_resolve_flag_full_rollout_returns_version(monkeypatch):
    monkeypatch.setenv("PROMPT_EXPERIMENT_VERSION", "v2")
    monkeypatch.setenv("PROMPT_EXPERIMENT_ROLLOUT", "100")
    assert PromptRegistry._resolve_flag("any-user-id") == "v2"


def test_resolve_flag_is_deterministic(monkeypatch):
    monkeypatch.setenv("PROMPT_EXPERIMENT_VERSION", "v2")
    monkeypatch.setenv("PROMPT_EXPERIMENT_ROLLOUT", "50")
    result_a = PromptRegistry._resolve_flag("stable-user-id")
    result_b = PromptRegistry._resolve_flag("stable-user-id")
    assert result_a == result_b

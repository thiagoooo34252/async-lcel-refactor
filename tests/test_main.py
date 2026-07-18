import importlib
from unittest.mock import Mock

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage


def _runtime_module():
    try:
        return importlib.import_module("async_lcel_question_chain.__main__")
    except ModuleNotFoundError as error:
        pytest.fail(f"Runtime configuration behavior is not implemented: {error}")


def test_runtime_constructs_chat_openai_after_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _runtime_module()
    fake_model = GenericFakeChatModel(messages=iter([AIMessage(content="unused")]))
    constructor = Mock(return_value=fake_model)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(runtime, "load_dotenv", lambda: None)
    monkeypatch.setattr(runtime, "ChatOpenAI", constructor)

    runtime.build_runtime_chain()

    constructor.assert_called_once_with(model="gpt-4o-mini")


def test_missing_key_blocks_model_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = _runtime_module()
    constructor = Mock(side_effect=AssertionError("must not construct a model"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(runtime, "load_dotenv", lambda: None)
    monkeypatch.setattr(runtime, "ChatOpenAI", constructor)

    with pytest.raises(runtime.RuntimeConfigurationError):
        runtime.build_runtime_chain()

    assert constructor.call_count == 0

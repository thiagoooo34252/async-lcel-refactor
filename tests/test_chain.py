from typing import Any

import pytest
from langchain_core.callbacks.manager import AsyncCallbackManagerForLLMRun
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult
from pydantic import Field


class RecordingFakeChatModel(GenericFakeChatModel):
    received_messages: list[BaseMessage] = Field(default_factory=list)

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.received_messages = messages
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


def _build_question_chain(model: GenericFakeChatModel):
    try:
        from async_lcel_question_chain import build_question_chain
    except ImportError as error:
        pytest.fail(f"Question-chain behavior is not implemented: {error}")
    return build_question_chain(model)


@pytest.mark.asyncio
@pytest.mark.parametrize("question", ["¿Qué es LCEL?", "¿Cómo compongo runnables?"])
async def test_question_is_formatted_into_human_message(question: str) -> None:
    model = RecordingFakeChatModel(
        messages=iter([AIMessage(content="Respuesta clara.")])
    )

    result = await _build_question_chain(model).ainvoke({"pregunta": question})

    assert result == "Respuesta clara."
    assert len(model.received_messages) == 2
    assert isinstance(model.received_messages[0], SystemMessage)
    assert model.received_messages[0].content == (
        "You answer questions about LangChain clearly and concisely."
    )
    assert isinstance(model.received_messages[1], HumanMessage)
    assert model.received_messages[1].content == question


@pytest.mark.asyncio
async def test_missing_question_raises_no_fallback() -> None:
    model = GenericFakeChatModel(messages=iter([AIMessage(content="fallback")]))

    chain = _build_question_chain(model)

    with pytest.raises(KeyError):
        await chain.ainvoke({})


@pytest.mark.asyncio
async def test_ainvoke_parses_exact_text() -> None:
    model = GenericFakeChatModel(
        messages=iter([AIMessage(content="LCEL composes runnables.")])
    )

    result = await _build_question_chain(model).ainvoke({"pregunta": "¿Qué es LCEL?"})

    assert result == "LCEL composes runnables."
    assert isinstance(result, str)
    assert not isinstance(result, BaseMessage)


@pytest.mark.asyncio
async def test_ainvoke_parses_a_second_text_response() -> None:
    model = GenericFakeChatModel(
        messages=iter([AIMessage(content="LCEL supports composition.")])
    )

    result = await _build_question_chain(model).ainvoke(
        {"pregunta": "¿Para qué sirve LCEL?"}
    )

    assert result == "LCEL supports composition."
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_ainvoke_does_not_return_ai_message() -> None:
    model = GenericFakeChatModel(messages=iter([AIMessage(content="Plain text only.")]))

    result = await _build_question_chain(model).ainvoke({"pregunta": "Resume LCEL"})

    assert result == "Plain text only."
    assert not isinstance(result, AIMessage)
    assert not isinstance(result, BaseMessage)


@pytest.mark.asyncio
async def test_fake_chain_runs_without_openai_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    model = GenericFakeChatModel(messages=iter([AIMessage(content="No key required.")]))

    result = await _build_question_chain(model).ainvoke(
        {"pregunta": "¿Necesito una clave?"}
    )

    assert result == "No key required."


@pytest.mark.asyncio
async def test_fresh_fake_responses_are_isolated() -> None:
    first_model = GenericFakeChatModel(
        messages=iter([AIMessage(content="First response.")])
    )
    second_model = GenericFakeChatModel(
        messages=iter([AIMessage(content="Second response.")])
    )

    first_result = await _build_question_chain(first_model).ainvoke(
        {"pregunta": "Primera"}
    )
    second_result = await _build_question_chain(second_model).ainvoke(
        {"pregunta": "Segunda"}
    )

    assert first_result == "First response."
    assert second_result == "Second response."

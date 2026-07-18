# Async LCEL Question Chain

A minimal Python 3.12 example of an asynchronous LangChain LCEL question chain.

[Implementation plan and verification evidence](IMPLEMENTATION_PLAN.md)

## Setup

Install the project and development tools with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-groups
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. Optionally set `OPENAI_MODEL`; the default is
`gpt-4o-mini`.

## Run

```bash
uv run python -m async_lcel_question_chain
```

The runtime builds `prompt | model | StrOutputParser()` and invokes it with
`await chain.ainvoke({"pregunta": ...})`.

## Verification

Automated tests use fresh `GenericFakeChatModel` instances. They do not read
real credentials and never call an LLM provider or network service.

```bash
uv run python -m pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run python -m build
```

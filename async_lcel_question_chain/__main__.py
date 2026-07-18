import asyncio
import os

from dotenv import load_dotenv
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from async_lcel_question_chain.chain import build_question_chain


class RuntimeConfigurationError(RuntimeError):
    """Raised when the runtime cannot create a configured OpenAI model."""


def build_runtime_chain() -> Runnable[dict[str, str], str]:
    """Create the production chain after validating local environment configuration."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeConfigurationError(
            "OPENAI_API_KEY must be configured before running."
        )

    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return build_question_chain(model)


async def main() -> None:
    """Read one question and print its asynchronous plain-text answer."""
    chain = build_runtime_chain()
    question = input("Pregunta: ")
    answer = await chain.ainvoke({"pregunta": question})
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())

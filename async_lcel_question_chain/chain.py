from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable


def build_question_chain(model: BaseChatModel) -> Runnable[dict[str, str], str]:
    """Build a role-based chain that returns plain-text answers."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You answer questions about LangChain clearly and concisely."),
            ("human", "{pregunta}"),
        ]
    )
    return prompt | model | StrOutputParser()

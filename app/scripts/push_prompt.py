from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

load_dotenv()

hub = Client()

prompt = ChatPromptTemplate.from_template(
    "Use the context below and the prior conversation to answer the question.\n\n"
    "Context:\n{context}\n\n"
    "Conversation so far:\n{history}\n\n"
    "Question: {question}"
)

hub.push_prompt("rag-prompt", object=prompt)
print("Prompt pushed. Check LangSmith Hub to tag as 'stable'.")

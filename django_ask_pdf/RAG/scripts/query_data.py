import os
import sys
from pathlib import Path

# Set up Django environment
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_ask_pdf.settings")

import django
django.setup()

import argparse
# from langchain.vectorstores.chroma import Chroma
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_groq import ChatGroq
# import os
from dotenv import load_dotenv
from RAG.scripts.get_embedding_function import get_embedding_function
import re

from django.conf import settings


CHROMA_PATH = str(settings.BASE_DIR / 'chroma')

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Load environment variables from .env file.
    load_dotenv()

    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    # model = Ollama(model="phi3")
    groq_api_key = os.getenv("OPENAI_API_KEY")
    model = ChatGroq(model="mixtral-8x7b-32768", api_key=groq_api_key)
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text.content

def extract_content(response_text):
    # Regular expression to extract the content
    content_match = re.search(r"content='(.*?)' response_metadata=", response_text, re.DOTALL)
    return content_match


if __name__ == "__main__":
    main()

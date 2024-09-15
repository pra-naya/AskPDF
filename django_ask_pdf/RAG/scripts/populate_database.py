import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
# from langchain.vectorstores import Chroma
from langchain_chroma import Chroma
import django
from django.conf import settings

import sys
import os
from pathlib import Path

# Set up Django environment
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_ask_pdf.settings")

import django
django.setup()


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_chatbot.settings')
# django.setup()

CHROMA_PATH = str(settings.BASE_DIR / 'chroma')
DATA_PATH = str(settings.MEDIA_ROOT / 'pdfs')
owner = ""

def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--filename", type=str, required=True, help="Name of the file.")
    parser.add_argument("--owner", type=str, help="Owner of the file")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # print(args.filename)

    # Add the file name to DATA_PATH
    global DATA_PATH 
    DATA_PATH = str(Path(DATA_PATH) / args.filename)

    if args.owner:
        global owner
        owner = args.owner

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

# Using DirectoryLoader
# def load_documents():
#     print("Loading Documents")
#     document_loader = PyPDFDirectoryLoader(DATA_PATH)
#     return document_loader.load()

def load_documents():
    print("Loading Documents")
    document_loader = PyPDFLoader(DATA_PATH)
    return document_loader.load()

# # Verifying the fucntion is actually returning documents
# def load_documents():
#     print("Loading Documents")
#     print(f"Processing file: {DATA_PATH}")
#     document_loader = PyPDFLoader(DATA_PATH)
#     documents = document_loader.load()
#     print(f"Loaded {len(documents)} documents")
#     for doc in documents:
#         print(f"Document Metadata: {doc.metadata}, Content Length: {len(doc.page_content)}")
#     return documents

def split_documents(documents: list[Document]):
    print("Splitting Documents")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")
    for chunk in chunks:
        print(f"Chunk Metadata: {chunk.metadata}, Chunk Content Length: {len(chunk.page_content)}")

    return chunks


def add_to_chroma(chunks: list[Document]):
    print("Loading Existing Database")
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    print("Calculating Page IDs")
    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    chunks_with_ids = add_owner_to_metadata(chunks_with_ids)

    print("Adding/Updating Documents")
    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        # new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        # db.add_documents(new_chunks, ids=new_chunk_ids)
        # # db.persist()

        # debug code
        try:
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            db.add_documents(new_chunks, ids=new_chunk_ids)
            print("Documents added successfully.")
        except Exception as e:
            print(f"Error while adding documents: {e}")
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    print("Calculating Chunk IDs")

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id


    return chunks

def add_owner_to_metadata(chunks):
    for chunk in chunks:
        chunk.metadata["owner"] = owner
        print(f"owner: {chunk.metadata['owner']}")
        print(f"id: {chunk.metadata['id']}")
    
    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()

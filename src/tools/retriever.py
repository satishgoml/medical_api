import os
import glob
from langchain.document_loaders import PyPDFLoader  # Loader for local PDFs
from langchain.tools.retriever import create_retriever_tool
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Define the directory containing the PDF files use cwd
directory_path = os.path.join(os.getcwd(), "data")

# Use glob to get all PDF file paths from the directory
pdf_paths = glob.glob(os.path.join(directory_path, "*.pdf"))

# Load documents from each PDF
docs = []
for path in pdf_paths:
    loader = PyPDFLoader(path)
    docs.extend(loader.load())


if not docs:
    raise ValueError("No documents loaded. Please check the PDF files in the directory.")

# Split the documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100,
    chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs)

# Create a vector database using Chroma
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="rag-chroma",
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever()

# Create a retriever tool to search the PDF contents
retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_pdf_content",
    "Search and return information from local PDF documents.",
)


# in main clause test the tool
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Test the retriever tool
    query = "What is the patients history?"
    result = retriever_tool(query)
    print(result)

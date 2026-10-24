print("RUNNING NEW OCT29 VERSION")

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pathlib import Path
from langchain_core.documents import Document

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0
)

policy_folder = Path("hr_policies")

documents = []

for file_path in policy_folder.glob("*.txt"):
    text = file_path.read_text(encoding="utf-8")

    document = Document(
        page_content=text,
        metadata={"source": file_path.name}
    )

    documents.append(document)

print(f"Loaded {len(documents)} documents")

for document in documents:
    print(document.metadata)
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

for chunk in chunks:
    print(chunk.metadata)  
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully") 
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings)

vector_store.add_documents(chunks)

print(f"Stored {len(chunks)} chunks in the vector store")
question = "How many days of maternity leave does Lemon Silk Technologies provide?"

results = vector_store.similarity_search(
    question,
    k=2
)

context = "\n\n".join(
    result.page_content for result in results
)
prompt = f"""
You are the HR Policy Assistant for Lemon Silk Technologies.

Answer the employee's question using only the HR policy information provided below.
Do not invent, assume, or add company policies that are not supported by the provided information.
If the provided information is insufficient to answer the question, clearly say that you do not have enough information.
Answer clearly, concisely, professionally, and in employee-friendly language.

HR POLICY INFORMATION:
{context}

EMPLOYEE QUESTION:
{question}

ANSWER:
"""
print("ABOUT TO CALL LLM")
response = llm.invoke(prompt)
print("LLM CALL FINISHED")
print("\nFINAL ANSWER")
print(response.content)
print("\nSOURCES")

for result in results:
    print(result.metadata["source"])

print("\nRETRIEVAL TEST")

for result in results:
    print("\nSource:", result.metadata["source"])
    print("Content:", result.page_content)
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
@st.cache_resource
def setup_rag():
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

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(chunks)

    return llm, vector_store


llm, vector_store = setup_rag()

st.title("Lemon Silk Technologies")
st.subheader("HR Policy Assistant")

st.write("Ask questions about approved company HR policies.")

with st.form("question_form"):
    question = st.text_input("Ask your HR policy question:")
    submitted = st.form_submit_button("Ask HR Assistant")

if submitted and question:
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
    If the provided information is insufficient to answer the question, respond only with:
    "I do not have enough information in the available HR policies to answer this question."
    Do not mention unrelated policies or retrieved documents.
    Answer clearly, concisely, professionally, and in employee-friendly language.

    HR POLICY INFORMATION:
    {context}

    EMPLOYEE QUESTION:
    {question}

    ANSWER:
    """

    with st.spinner("Searching approved HR policies and preparing your answer..."):
        response = llm.invoke(prompt)

    st.subheader("Answer")
    st.write(response.text)
    if "do not have enough information" not in response.text.lower():
        sources = list({
            result.metadata["source"]
            for result in results
    })

        st.caption("Source: " + ", ".join(sources))
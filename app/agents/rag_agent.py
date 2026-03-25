from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter 
from app.agents.llm import get_llm

# 🔥 Load embedding model
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 🔥 Global vector store
vector_store = None

# 🔥 LLM
llm = get_llm()


# =========================================================
# ✅ LOAD PDF → CREATE VECTOR DB
# =========================================================
def load_pdf(path: str):
    global vector_store

    loader = PyPDFLoader(path)
    documents = loader.load()

    # 🔥 IMPORTANT: split into chunks
    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.split_documents(documents)

    vector_store = FAISS.from_documents(docs, embedding)

    print("✅ PDF loaded and indexed")


# =========================================================
# ✅ GET CONTEXT FROM VECTOR DB
# =========================================================
def get_rag_context(question: str):
    global vector_store

    if vector_store is None:
        return None

    docs = vector_store.similarity_search(question, k=3)

    context = "\n".join([doc.page_content for doc in docs])

    return context


# =========================================================
# ✅ FULL RAG ANSWER (OPTIONAL USE)
# =========================================================
def rag_answer(question: str):
    context = get_rag_context(question)

    if not context:
        return None

    prompt = f"""
    Answer the question based only on the context below:

    {context}

    Question: {question}
    """

    return llm.invoke(prompt).content
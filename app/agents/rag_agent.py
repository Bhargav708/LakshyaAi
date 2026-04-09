from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from app.agents.llm import get_llm

# 🔥 Load embedding model
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 🔥 Store multiple users' vector DBs (IMPORTANT)
vector_stores = {}

# 🔥 LLM
llm = get_llm()


# =========================================================
# ✅ LOAD PDF → CREATE VECTOR DB (PER USER)
# =========================================================
def load_pdf(user_id: str, path: str):
    loader = PyPDFLoader(path)
    documents = loader.load()

    splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    docs = splitter.split_documents(documents)

    # Store vector DB per user
    vector_stores[user_id] = FAISS.from_documents(docs, embedding)

    print(f"✅ PDF loaded for user: {user_id}")


# =========================================================
# ✅ GET CONTEXT FROM VECTOR DB
# =========================================================
def get_rag_context(user_id: str, question: str):
    vector_store = vector_stores.get(user_id)

    if vector_store is None:
        return None

    docs = vector_store.similarity_search(
        question,
        k=10   # 🔥 increase from 5 → 10
    )

    context = "\n\n".join([doc.page_content for doc in docs])

    return context
# =========================================================
# ✅ MAIN FUNCTION: ASK QUESTION FROM PDF
# =========================================================
def ask_pdf(user_id: str, question: str):
    context = get_rag_context(user_id, question)

    if not context:
        return "⚠️ No document found. Please upload a PDF first."

    prompt = f"""
You are an AI assistant.

Use the context to answer the question.

If the question is general (like summary, overview),
provide a summary based on available context.

DO NOT say "Not found" unless context is completely empty.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content
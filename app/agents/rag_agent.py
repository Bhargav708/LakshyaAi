from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from app.agents.llm import get_llm

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_store = None

llm = get_llm()

def load_pdf(path):
    global vector_store
    loader = PyPDFLoader(path)
    docs = loader.load()
    vector_store = FAISS.from_documents(docs, embedding)


def rag_agent(state):
    global vector_store

    if not vector_store:
        return {"response": "No PDF uploaded"}

    docs = vector_store.similarity_search(state["question"])
    context = docs[0].page_content if docs else ""

    prompt = f"Answer from context:\n{context}\nQ:{state['question']}"
    res = llm.invoke(prompt).content

    return {"response": res}
import asyncio

from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse

from langchain_core.output_parsers import StrOutputParser, SimpleJsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_anthropic import ChatAnthropic

from models import Query, DocumentListModel

from prompt_templates import template_1, template_2

from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")


# load the document and split it into chunks
################################################################
embeddings = OpenAIEmbeddings(
    model='text-embedding-3-small'
)

vector_store = PineconeVectorStore(embedding=embeddings, index_name='ragster')
chunks = None


async def create_vector_store(docs: DocumentListModel) -> None:
    global vector_store
    global chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    chunks = await asyncio.to_thread(text_splitter.split_documents, docs.documents)

    vector_store = await asyncio.to_thread(
        PineconeVectorStore.from_documents,
        chunks,
        embeddings,
        index_name='ragster'
    )

async def retrieve_docs(query: str, k:int) -> str:
    similar_docs = await asyncio.to_thread(vector_store.similarity_search, query=query, k=k)

    docs_joined = '\n\n'.join(
        f'Document {idx + 1}: {doc.page_content}' for idx, doc in enumerate(similar_docs)
    )
    return docs_joined

def get_first_pages(chunks: list) -> str:
    first_pages = '\n\n'.join(
        f'Page {idx + 1}: {page.page_content}' for idx, page in enumerate(chunks[:5])
    )
    return first_pages
################################################################

choose = 0
llm = None

if choose == 0:
    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.4,
        streaming=True,
    )
else:
    llm = ChatAnthropic(
        model='claude-3-5-sonnet-20240620',
        temperature=0.5,
        streaming=True,
    )


chat_prompt = PromptTemplate.from_template(template_1)
chain = chat_prompt | llm | StrOutputParser()

chat_prompt_2 = PromptTemplate.from_template(template_2)
chain_2 = chat_prompt_2 | llm | SimpleJsonOutputParser()


async def generate_chat_responses(message: str, docs: str):
    async for chunk in chain.astream({
        "user_question": message,
        "docs": docs
        }):
        yield f"{chunk}"


async def generate_recommended_questions():
    return await chain_2.ainvoke({
        'uploaded_document_first_pages': get_first_pages(chunks)
    })

    

app = FastAPI()

@app.get("/chat")
async def chat(
    query: Query = Body(...),
):
    docs = await retrieve_docs(query.text, 3)
    
    return StreamingResponse(generate_chat_responses(message=query.text, docs=docs), media_type="text/event-stream")

@app.post("/upload_document")
async def upload_document(
    documents: DocumentListModel = Body(...),
):
    
    await create_vector_store(documents)
    recommended_questions = await generate_recommended_questions()

    return recommended_questions


# clear the index at the end of the session
# vector_store.delete(namespace='ragster', delete_all=True)
# write a delete endpoint to clear the index
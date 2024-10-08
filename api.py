import asyncio

from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse

from langchain_core.output_parsers import StrOutputParser, SimpleJsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_anthropic import ChatAnthropic
from pinecone.core.openapi.shared.exceptions import NotFoundException

from models import Query, ChatHistory, ModelSelection, DocumentListModel

from prompt_templates import template_1, template_2

from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

# create the embeddings and vector store
embeddings = OpenAIEmbeddings(
    model='text-embedding-3-small'
)

vector_store = PineconeVectorStore(embedding=embeddings, index_name='ragster')
chunks = None

# define the chat models
gpt_model = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0.4,
    streaming=True,
)

claude_model = ChatAnthropic(
    model='claude-3-5-sonnet-20240620',
    temperature=0.4,
    streaming=True,
)

# create the vector store
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

# retrieve similar documents
async def retrieve_docs(query: str, k:int) -> str:
    similar_docs = await asyncio.to_thread(vector_store.similarity_search, query=query, k=k)

    docs_joined = '\n\n'.join(
        f'Document {idx + 1}: {doc.page_content}' for idx, doc in enumerate(similar_docs)
    )
    return docs_joined

# get the first pages of the documents
def get_first_pages(chunks: list) -> str:
    first_pages = '\n\n'.join(
        f'Page {idx + 1}: {page.page_content}' for idx, page in enumerate(chunks[:5])
    )
    return first_pages


# create the chat prompts
chat_prompt = PromptTemplate.from_template(template_1)
chat_prompt_2 = PromptTemplate.from_template(template_2)

# generate chat responses in streaming manner
async def generate_chat_responses(message: str, chat_history: list, model: int, docs: str):
    llm = gpt_model if model == 1 else claude_model
    chain = chat_prompt | llm | StrOutputParser()
    

    chat_history_str = "".join([f"User: {q_a[0]}\nAI: {q_a[1]}\n" for q_a in chat_history])
    for q_a in chat_history:
        chat_history_str += f"User: {q_a[0]}\nAI: {q_a[1]}\n"


    async for chunk in chain.astream({
        "user_question": message,
        "docs": docs,
        "chat_history": chat_history_str
        }):
        yield f"{chunk}"

# generate recommended questions
async def generate_recommended_questions(model: int):
    llm = gpt_model if model == 1 else claude_model
    chain_2 = chat_prompt_2 | llm | SimpleJsonOutputParser()
    
    return await chain_2.ainvoke({
        'uploaded_document_first_pages': get_first_pages(chunks)
    })

# send an error response if the message is empty
async def send_error_response():
    for word in ["Seems like you sent an empty message. Please type something to get a response."]:
        yield f"{word}"


app = FastAPI()

@app.get("/chat")
async def chat(
    query: Query,
    model_selection: ModelSelection,
    chat_history: ChatHistory,
):
    if query.text == "":
        return StreamingResponse(send_error_response(), media_type="text/event-stream")

    docs = await retrieve_docs(query.text, 3)
    
    return StreamingResponse(generate_chat_responses(
        message=query.text,
        chat_history=chat_history.history,
        model=model_selection.model, docs=docs), media_type="text/event-stream")

@app.post("/upload_document")
async def upload_document(
    documents: DocumentListModel,
    model_selection: ModelSelection,
):
    
    await create_vector_store(documents)
    recommended_questions = await generate_recommended_questions(model=model_selection.model)

    return recommended_questions

@app.delete("/clear_index")
async def clear_index():
    try:
        await asyncio.to_thread(vector_store.delete, namespace='', delete_all=True)
    except NotFoundException:
        return {"message": "Namespace does not exist"}
    return {"message": "Index cleared"}
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

class Query(BaseModel):
    text: str

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

template = """
    You are a helpful chatbot that can answer questions.\
    
    Question: {question}
"""

chat_prompt = PromptTemplate.from_template(template)

chain = chat_prompt | llm | StrOutputParser()

async def generate_chat_responses(message):
    async for chunk in chain.astream({"question": message}):
        yield f"{chunk}"


app = FastAPI()

@app.get("/chat")
async def chat(
    query: Query = Body(...),
):
    return StreamingResponse(generate_chat_responses(message=query.text), media_type="text/event-stream")
### This is a test file to test the pipeline of the LangChain library for a RAG app named RAGSTER. ###


from langchain_core.output_parsers import StrOutputParser, SimpleJsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_text_splitters import RecursiveCharacterTextSplitter

from prompt_templates import template_1, template_2

from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

loader = PyPDFLoader('./docs/Atomic Habits James Clear.pdf')
docs = loader.load_and_split()

embeddings = OpenAIEmbeddings(
    model='text-embedding-3-small'
)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)
# vector_store = PineconeVectorStore.from_documents(chunks, embeddings, index_name='ragster', )

# query = "What does 'implementation intention' mean?"

# similar_docs = vector_store.similarity_search(query=query, k=3)

# docs_joined = ''
# for idx, doc in enumerate(similar_docs):
#     docs_joined += 'Document ' + str(idx + 1) + ': ' + doc.page_content + '\n\n'
# print(docs_joined)

first_pages = ''
for idx, page in enumerate(chunks[:5]):
    first_pages += 'Page ' + str(idx + 1) + ': ' + page.page_content + '\n\n'
print(first_pages)

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
    )


# chat_prompt = PromptTemplate.from_template(template_1)

chat_prompt_2 = PromptTemplate.from_template(template_2)

# chain = chat_prompt | llm | StrOutputParser()

chain_2 = chat_prompt_2 | llm | SimpleJsonOutputParser()

output = chain_2.invoke({
    'uploaded_document_first_pages': first_pages
})

print(output['q1'], output['q2'], output['q3'], sep='\n')

# clear the index at the end of the session
# vector_store.delete(namespace='ragster', delete_all=True)
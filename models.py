from typing import List, Dict, Any
from pydantic import BaseModel

# define a pydantic model for a query
class Query(BaseModel):
    text: str

# define a pydantic model for the chat history
class ChatHistory(BaseModel):
    history: List[List[str]]

# define a pydantic model for a single document
class DocumentModel(BaseModel):
    page_content: str
    metadata: Dict[str, Any]

# define a pydantic model for a list of documents
class DocumentListModel(BaseModel):
    documents: List[DocumentModel]

# define a pydantic model for the model selection
class ModelSelection(BaseModel):
    model: int
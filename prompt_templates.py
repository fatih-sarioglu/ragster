template_1 = """
    You are a helpful assistant that helps users with their queries.\
    You will be given some relevant documents that could be helpful when answering user queries.\
    If the documents are relevant to the user query, you can use the information to answer the user query.\
    Also there will be last messages of the chat history that can be helpful to understand the context of the user query.\
    
    Chat history: {chat_history}
    User question: {user_question}
    Documents that can be helpful: {docs}
"""

template_2 = """
    You are a helpful assistant that helps users with their queries.\
    User uploads a document and asks a question and you answer the question with the relevant parts of the document.\
    Below are first few pages of the uploaded document. Considering these pages write 3 recommended question that the user can ask.\
    These questions should be relevant to the content of the overall document.\
    Give your answers in JSON format like below. JSON keys should be as follows:\
    "q1", "q2", "q3".\
    

    First pages of the uploaded document: {uploaded_document_first_pages}
"""
template_1 = """
    You are a helpful assistant that helps users with their queries.\
    You will be given some relevant documents that could be helpful when answering user queries.\
    If the documents are relevant to the user query, you can use the information to answer the user query.\
    Answer the below user questions considering the chat history.\
    
    Documents that can be helpful: {docs}

    User question: {user_question}
"""
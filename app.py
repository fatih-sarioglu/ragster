import gradio as gr

from langchain_community.document_loaders import PyPDFLoader

import requests

desired_model = None

# import custom css
with open("style.css", "r", encoding='utf-8') as f:
    css = f.read()

# upload_file callback function
def upload_file_fn(file: str) -> dict:
    # load the content of the uploaded PDF file
    loader = PyPDFLoader(file)
    docs = loader.load()
    docs_serialized = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]

    print(f"Model: {desired_model}")
    
    # send the content of the uploaded file to the backend to store it and get example questions
    res = requests.post(
        "http://localhost:8000/upload_document",
        json={
            "documents": {"documents": docs_serialized[:5]},
            "model_selection": {"model": desired_model},
        },
    )

    example_questions = res.json()

    # update the UI
    return {
        upload_file: gr.UploadButton(interactive=False),
        chat_input: gr.Textbox(interactive=True),
        send_button: gr.Button(interactive=True),
        chatbot: gr.Chatbot(height=440, placeholder="<h2>ASK YOUR QUESTIONS</h2>"),
        examples_title: gr.Markdown(visible=True),
        example_1: gr.Button(example_questions['q1'], visible=True),
        example_3: gr.Button(example_questions['q2'], visible=True),
        example_2: gr.Button(example_questions['q3'], visible=True),
    }


def select_model(model: str):
    global desired_model
    desired_model = 1 if model == "GPT-4o-mini" else 2
    print(f"Selected model: {model}")
    return {
        select_model_dropdown: gr.Dropdown(interactive=False),
        upload_file: gr.UploadButton(interactive=True),
    }


# 3 consecutive functions to handle sending and receiving messages
def put_message(history, message: str):
    history = [] if history is None else history

    print(f"Message: {message}")
    print(f"History: {history}")

    history.append((message, None))

    return {
        chatbot: history,
        chat_input: gr.Textbox(value=None, interactive=False),
        send_button: gr.Button(interactive=False),
    }

def get_and_put_response(history):

    print(f"History 2: {history}")
    
    history[-1][1] = ""

    s = requests.Session()
    with s.get(
        "http://localhost:8000/chat",
        stream=True,
        json={
            "query": {"text": history[-1][0]},
            "model_selection": {"model": desired_model},
        }
    ) as r:
        for line in r.iter_content(decode_unicode=True):
            history[-1][1] += line
            yield history

def after_response():
    return {
        chat_input: gr.Textbox(interactive=True),
        send_button: gr.Button(interactive=True),
    }


# new_chat_button callback function
def new_chat():
    return {
        chatbot: [],
        chat_input: gr.Textbox(interactive=False, value=None),
        send_button: gr.Button(interactive=False),
        upload_file: gr.UploadButton(interactive=True),
        examples_title: gr.Markdown(visible=False),
        example_1: gr.Button('', visible=False),
        example_3: gr.Button('', visible=False),
        example_2: gr.Button('', visible=False),
    }


with gr.Blocks(fill_height=False, fill_width=False, css=css, title='RAGSTER') as demo:
    with gr.Row():
        # sidebar
        with gr.Column(scale=0,variant='panel', min_width=250, elem_classes='sidebar') as sidebar_left:
            gr.Image(
                './img/document.png',
                height=110,
                width=220,
                show_label=False,
                show_download_button=False,
                show_fullscreen_button=False,
                show_share_button=False,
                interactive=False,
            )

            gr.Markdown(
                value="""

                # RAGSTER
                
                ### RAGSTER is a chatbot that can answer your questions based on a PDF file you upload.
                
                

                ### Select a model, then upload a PDF file and ask your questions.
                """,
                elem_classes='title',
            )

            
            select_model_dropdown = gr.Dropdown(
                choices=["GPT-4o-mini", "Claude 3.5 Sonnet"],
                label="Select AI Model",
                interactive=True
            )

            upload_file = gr.UploadButton(
                label="Upload a PDF file",
                variant='primary',
                interactive=False,
                elem_classes='upload_file_button',
                file_types=['.pdf'],
            )


            select_model_dropdown.select(
                fn=select_model,
                inputs=[select_model_dropdown],
                outputs=[select_model_dropdown, upload_file],
            )

            new_chat_button = gr.Button(
                value="New Chat",
                elem_classes='new_chat_button',
                variant='secondary',
                size='sm'
            )

        # main chat interface
        with gr.Column(scale=10,) as main:
            # chat messages will appear here
            chatbot = gr.Chatbot(
                show_label=False,
                placeholder="<h2><strong>SELECT AN AI MODEL AND UPLOAD A FILE</strong></h2><br><h3>THEN ASK YOUR QUESTIONS</h3></br>",
                height=530,
                elem_classes='chatbot',
                bubble_full_width=False
            )
            
            # textbox and send button
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Your message",
                    container=False,
                    show_label=False,
                    show_copy_button=True,
                    autofocus=True,
                    scale=10,
                    interactive=False,
                )
                
                send_button = gr.Button(
                    value="Send",
                    scale=0,
                    size='sm',
                    min_width=80,
                    variant='primary',
                    interactive=False
                )
            
            # sending and receiving messages
            # same functionality for send button and enter key
            gr.on(
                triggers=[send_button.click, chat_input.submit],
                fn=put_message,
                inputs=[chatbot, chat_input],
                outputs=[chatbot, chat_input, send_button],
            ).success(
                get_and_put_response,
                inputs=[chatbot],
                outputs=[chatbot],
            ).success(
                after_response,
                outputs=[chat_input, send_button],
            )

            # example questions that user can ask based on the content of the uploaded PDF file
            examples_title = gr.Markdown(
                "<h3><strong>Examples</strong></h3>",
                elem_classes='examples_title',
                visible=False,
            )
            with gr.Row():
                example_1 = gr.Button("", size='sm', variant='secondary', visible=False)
                example_2 = gr.Button("", size='sm', variant='secondary', visible=False)
                example_3 = gr.Button("", size='sm', variant='secondary', visible=False)

            
            # upload file event
            upload_file.upload(
                fn=upload_file_fn,
                inputs=[upload_file],
                outputs=[upload_file, chat_input, send_button, chatbot, examples_title, example_1, example_2, example_3],
            )

            # new chat event
            new_chat_button.click(
                new_chat,
                None,
                [chatbot, chatbot, chat_input, send_button, upload_file, examples_title, example_1, example_2, example_3]
            ).then(lambda: (
                {chatbot: gr.Chatbot(height=530, placeholder="<h2><strong>UPLOAD A FILE</strong></h2><br><h3>THEN ASK YOUR QUESTIONS</h3></br>")}
                    ),
                    None,
                    [chatbot]
                )


demo.launch()
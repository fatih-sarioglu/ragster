import gradio as gr

from langchain_community.document_loaders import PyPDFLoader

import requests

# import custom css
with open("style.css", "r", encoding='utf-8') as f:
    css = f.read()

theme = gr.themes.Default().set(
    button_cancel_background_fill="#0b750b",
    button_cancel_background_fill_dark=f"#0b750b",
    button_cancel_background_fill_hover=f"#0c8a0c",
    button_cancel_background_fill_hover_dark=f"#0c8a0c",
    button_cancel_border_color="#0b750b",
    button_cancel_border_color_dark="#0b750b",
)


def put_message(history, message: str):
    history = [] if history is None else history

    if message != '':
        history.append((message, None))
    
    return {
        chatbot: history,
        chat_input: gr.Textbox(value=None, interactive=True),
        send_button: gr.Button(interactive=True),
    }

def get_and_put_response(history):
    
    if len(history) != 0 and history[-1][1] is None:
        history[-1][1] = ""

        s = requests.Session()
        with s.get(
            "http://localhost:8000/chat",
            stream=True,
            json={"text": history[-1][0]}
        ) as r:
            for line in r.iter_content(decode_unicode=True):
                history[-1][1] += line
                yield history
    
    return {
        chatbot: history,
    }

def after_response():
    return {
        chat_input: gr.Textbox(interactive=True),
        send_button: gr.Button(interactive=True),
    }



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


with gr.Blocks(fill_height=False, fill_width=False, css=css, theme=theme, title='RAGSTER') as demo:
    with gr.Row():
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
                
                ### RAGSTER is a chatbot that can answer your questions based on the content of a PDF file you upload.
                
                

                ### Upload a PDF file and ask your questions.
                """,
                elem_classes='title',
            )
            

            upload_file = gr.UploadButton(
                label="Upload a PDF file",
                variant='primary',
                interactive=True,
                elem_classes='upload_file_button',
                file_types=['.pdf'],
            )

            new_chat_button = gr.Button(
                value="New Chat",
                elem_classes='new_chat_button',
                variant='secondary'
            )


        with gr.Column(scale=10,) as main:
            chatbot = gr.Chatbot(
                show_label=False,
                placeholder="<h2><strong>UPLOAD A FILE</strong></h2><br><h3>THEN ASK YOUR QUESTIONS</h3></br>",
                height=530,
                elem_classes='chatbot',
                bubble_full_width=False
            )
            

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
            send_button.click(put_message, [chatbot, chat_input], [chatbot, chat_input, send_button]).then(get_and_put_response, [chatbot], [chatbot]).then(after_response, None, [chat_input, send_button])
            chat_msg = chat_input.submit(put_message, [chatbot, chat_input], [chatbot, chat_input, send_button]).then(get_and_put_response, [chatbot], [chatbot]).then(after_response, None, [chat_input, send_button])

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

            

            def upload_file_fn(file: str) -> dict:
                """
                Function to handle the file upload event.It loads the content of the uploaded PDF file and sends it to the backend for processing.
                Gets the response from the backend and displays example questions that the user can ask based on the content of the uploaded PDF file.
                Disables the upload button and enables the main chat interface.

                Args: 
                    file (str): The path to the uploaded file.
                """

                print(f"File uploaded:\n{file}")

                # load the content of the uploaded PDF file
                # loader = PyPDFLoader(file)
                # docs = loader.load()
                # docs_serialized = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
                
                # # send the content of the uploaded file to the backend to store it and get example questions
                # res = requests.post(
                #     "http://localhost:8000/upload_document",
                #     json={"documents": docs_serialized[:5]},
                # )

                # example_questions = res.json()

                # update the UI
                return {
                    upload_file: gr.UploadButton(interactive=False),
                    chat_input: gr.Textbox(interactive=True),
                    send_button: gr.Button(interactive=True),
                    chatbot: gr.Chatbot(height=440, placeholder="<h2>ASK YOUR QUESTIONS</h2>"),
                    examples_title: gr.Markdown(visible=True),
                    # example_1: gr.Button(example_questions['q1'], visible=True),
                    # example_3: gr.Button(example_questions['q2'], visible=True),
                    # example_2: gr.Button(example_questions['q3'], visible=True),
                }

            # upload file event
            upload_file.upload(
                fn=upload_file_fn,
                inputs=[upload_file],
                outputs=[upload_file, chat_input, send_button, chatbot, examples_title, example_1, example_2, example_3],
            )

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
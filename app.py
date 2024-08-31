import gradio as gr

import time

def yes_man(message, history):
    if message.endswith("?"):
        return "Yes"
    else:
        return "Ask me anything!"
    

css = """
.prose.svelte-gq7qsu h1 {
    text-align: center;
    font-size: 35px
}

.gradio-container.gradio-container-4-42-0.svelte-wpkpf6.app {
    padding-top: 30px;
    padding-left: 50px;
    padding-right: 50px;
    padding-bottom: 10px;
    max-width: 80%;
    min-width: 850px;
}

.sidebar {
    padding: 15px;
}

.upload_file_button.svelte-cmf5ev {
    margin-top: 10px;
}

.new_chat_button.svelte-cmf5ev {
    margin-top: 25px;
}

"""

theme = gr.themes.Default().set(
    button_cancel_background_fill="#0b750b",
    button_cancel_background_fill_dark=f"#0b750b",
    button_cancel_background_fill_hover=f"#0c8a0c",
    button_cancel_background_fill_hover_dark=f"#0c8a0c",
    button_cancel_border_color="#0b750b",
    button_cancel_border_color_dark="#0b750b",
)


with gr.Blocks(fill_height=False, fill_width=False, css=css, theme=theme) as demo:
    with gr.Row():
        with gr.Column(visible=True, scale=0,variant='panel', min_width=250, elem_classes='sidebar') as sidebar_left:
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
            )

            new_chat = gr.Button(
                value="New Chat",
                elem_classes='new_chat_button',
                variant='secondary'
            )


        with gr.Column(visible=True, scale=10,) as main:
            chatbot = gr.Chatbot(
                show_label=False,
                placeholder="<h2><strong>UPLOAD A FILE</strong></h2><br><h3>THEN ASK YOUR QUESTIONS</h3></br>",
                height=530,
                elem_classes='chatbot',
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


            
            examples_title = gr.Markdown(
                "<h3><strong>Examples</strong></h3>",
                elem_classes='examples_title',
                visible=False,
            )
                
            with gr.Row():
                example_1 = gr.Button("", size='sm', variant='secondary', visible=False)
                example_2 = gr.Button("", size='sm', variant='secondary', visible=False)
                example_3 = gr.Button("", size='sm', variant='secondary', visible=False)

            
            def upload_file_fn():
                print("File uploaded")

                return {
                    upload_file: gr.UploadButton(interactive=False),
                    chat_input: gr.Textbox(interactive=True),
                    send_button: gr.Button(interactive=True),
                    chatbot: gr.Chatbot(height=440),
                    examples_title: gr.Markdown(visible=True),
                    example_1: gr.Button("What is implementation intention? Where does the idea come from?", visible=True),
                    example_3: gr.Button("How to build atomic habits?", visible=True),
                    example_2: gr.Button("What is a habit?", visible=True),
                }

            upload_file.upload(
                fn=upload_file_fn,
                outputs=[upload_file, chat_input, send_button, chatbot, examples_title, example_1, example_2, example_3],
            )

demo.launch()

def yes_man(message, history):
    return "Yes" if message.endswith("?") else "Ask me anything!"


# with gr.ChatInterface(
#     yes_man,
#     title="RAGSTER",
#     chatbot=gr.Chatbot(height=400, show_label=False, placeholder="<h3><strong>ASK ANYTHING</strong></h3>"),
#     textbox=gr.Textbox(placeholder="Ask me a yes or no question", container=False, scale=10),
#     theme="soft",
#     examples=["What is implementation intention?", "What is a habit?", "Are tomatoes vegetables?"],
#     #cache_examples=True,
#     retry_btn=None,
#     undo_btn=None,
#     clear_btn=None,
#     multimodal=False,
#     fill_width=False,
#     submit_btn=gr.Button("Send", scale=0, size='sm', min_width=80, variant='primary'),
#     css=css,
# ) as demo:
#     pass



demo.launch()
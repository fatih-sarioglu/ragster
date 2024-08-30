import gradio as gr

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
    padding-left: 50px;
    padding-right: 50px;
    max-width: 1000px;
}
"""

# with gr.Blocks(fill_height=False, fill_width=False, css=css) as demo:
#     # chatbot = gr.ChatInterface(
#     #     yes_man,
#     #     title="RAGSTER",
#     #     description="Ask questions about your document",
#     #     chatbot=gr.Chatbot(height=350, show_label=False, placeholder="<h3><strong>ASK ANYTHING</strong></h3>"),
#     #     textbox=gr.Textbox(placeholder="Ask me a yes or no question", container=False, scale=7),
#     #     theme="soft",
#     #     examples=["What is implementation intention?", "What is a habit?", "Are tomatoes vegetables?"],
#     #     cache_examples=True,
#     #     retry_btn=None,
#     #     undo_btn="Delete Previous",
#     #     clear_btn="Clear",
#     #     multimodal=True,
#     #     fill_width=False
#     # )

#     gr.Markdown("# RAGSTER", elem_classes='title')
    
#     chatbot = gr.Chatbot(height=400,
#                          show_label=False,
#                          placeholder="<h3><strong>ASK ANYTHING</strong></h3>")
    
#     with gr.Row():
#         chat = gr.Textbox(placeholder="Ask me a yes or no question",
#                           container=True,
#                           show_label=False,
#                           interactive=True,
#                           show_copy_button=True,
#                           autofocus=True,
#                           scale=10)
        
#         gr.Button("Send", scale=0, size='sm', min_width=80, variant='primary')

#     gr.TextArea("What is implementation intention?")

# demo.launch()

def yes_man(message, history):
    return "Yes" if message.endswith("?") else "Ask me anything!"


with gr.ChatInterface(
    yes_man,
    title="RAGSTER",
    chatbot=gr.Chatbot(height=400, show_label=False, placeholder="<h3><strong>ASK ANYTHING</strong></h3>"),
    textbox=gr.Textbox(placeholder="Ask me a yes or no question", container=False, scale=10),
    theme="soft",
    examples=["What is implementation intention?", "What is a habit?", "Are tomatoes vegetables?"],
    #cache_examples=True,
    retry_btn=None,
    undo_btn=None,
    clear_btn=None,
    multimodal=False,
    fill_width=False,
    submit_btn=gr.Button("Send", scale=0, size='sm', min_width=80, variant='primary'),
    css=css,
) as demo:
    pass



demo.launch()
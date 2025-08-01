import gradio as gr
from app.logic import summarize_text, extract_entities
from app.schemas import Entity

def build_interface():
    with gr.Blocks(css="""
        .textbox-style {
            background-color: #2a2b35 !important;
            color: #f0f0f0 !important;
            border: 1px solid #444 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 14px;
            font-family: inherit;
        }

        .checkbox-container {
            background-color: #2a2b35;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .checkbox-inner .gr-checkbox-group {
            display: flex !important;
            flex-direction: column !important;
            gap: 6px !important;
            max-height: 480px !important;
            overflow-y: auto !important;
        }

        .checkbox-inner .gr-checkbox-group label {
            display: block !important;
            width: 100% !important;
            padding: 4px 8px !important;
            background-color: #2a2b35 !important;
            border: 1px solid #555 !important;
            border-radius: 4px !important;
            color: #f0f0f0 !important;
        }

        .checkbox-inner input[type="checkbox"] {
            accent-color: #f0f0f0;
        }

        label {
            font-weight: 600 !important;
            color: #f0f0f0 !important;
            margin-bottom: 4px !important;
        }

        .equal-height-row {
            display: flex;
            align-items: stretch;
        }

        .equal-height-row > div {
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .gr-column {
            height: 100%;
        }
    """) as demo:

        gr.Markdown("## 📝 Vietnamese News Summary")

        with gr.Row(elem_classes="equal-height-row"):
            with gr.Column(scale=1):
                input_text = gr.Textbox(
                    label="Enter text to summarize",
                    placeholder="Paste or type your content...",
                    lines=20,
                    elem_classes="textbox-style"
                )
                extract_btn = gr.Button("📌 Extract Entities")

            with gr.Column(scale=1):
                entity_placeholder = gr.Textbox(
                    label="Select important entities",
                    placeholder="Waiting for extracted entities...",
                    lines=20,
                    interactive=False,
                    visible=True,
                    elem_classes="textbox-style"
                )

                with gr.Group(visible=False, elem_classes="checkbox-container checkbox-inner") as checkbox_wrapper:
                    entity_list = gr.CheckboxGroup(
                        choices=[],
                        label="Select important entities",
                        visible=True,
                        elem_classes="gr-checkbox-group"
                    )

        with gr.Group():
            summary_output = gr.TextArea(
                label="✂️ Summary Result",
                interactive=False,
                lines=10,
                elem_classes="textbox-style"
            )
            summarize_btn = gr.Button("✂️ Summarize")

        def on_extract_entities(text):
            entities: list[Entity] = extract_entities(text)
            entity_choices = [
                f"{entity.entity_name} ({entity.entity_type})"
                for entity in entities
            ]
            return (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(choices=entity_choices)
            )

        extract_btn.click(
            fn=on_extract_entities,
            inputs=[input_text],
            outputs=[entity_placeholder, checkbox_wrapper, entity_list]
        )

        summarize_btn.click(
            fn=summarize_text,
            inputs=[input_text, entity_list],
            outputs=summary_output
        )

    return demo
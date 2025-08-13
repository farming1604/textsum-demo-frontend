import gradio as gr
from app.logic import summarize_text, extract_entities, generate_questions
from app.schemas import Entity

def build_interface():
    with gr.Blocks(css="""
        .entity-scroll-wrapper {
            background-color: #2a2b35;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            height: 648px;
            overflow-y: auto;
        }
                   
        .textsum-wrapper {
            background-color: #2a2b35;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            height: 648px;
            overflow-y: auto;
        }
                
        .questions-outputs-wrapper {
            background-color: #2a2b35;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            height: 470px;
            overflow-y: auto;
        }
                   
        .gr-checkbox-group {
            display: flex !important;
            flex-direction: column !important;
            gap: 6px !important;
        }

        .gr-checkbox-group label {
            display: block !important;
            width: 100% !important;
            padding: 6px 10px !important;
            background-color: #2a2b35 !important;
            border: 1px solid #555 !important;
            border-radius: 6px !important;
            color: #f0f0f0 !important;
        }

        .textbox-style {
            background-color: #2a2b35 !important;
            color: #f0f0f0 !important;
            border: 1px solid #444 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 14px;
            font-family: inherit;
        }

        .clear-button {
            margin-top: 12px !important;
        }

        .equal-height-row {
            display: flex;
            align-items: stretch;
            gap: 20px;
        }

        .equal-height-row > div {
            display: flex;
            flex-direction: column;
            flex: 1;
            height: 100%;
        }

        .gr-column {
            height: 100%;
        }

        .input-with-button {
            display: flex;
            flex-direction: column;
        }

        .input-with-button .gr-button {
            margin-top: 12px;
            width: fit-content;
            height: 600px;
        }
    """) as demo:

        gr.Markdown("## 📝 Vietnamese News Summary")

        with gr.Row(elem_classes="equal-height-row"):
            with gr.Column(scale=1):
                with gr.Group(elem_classes="textsum-wrapper"):
                    input_text = gr.Textbox(
                        label="📝 Enter text to summarize",
                        placeholder="Paste or type your content...",
                        lines=28    ,
                    )
                extract_btn = gr.Button("📌 Extract Entities")

            with gr.Column(scale=1.0):
                with gr.Group(elem_classes="entity-scroll-wrapper"):
                    entity_list = gr.CheckboxGroup(
                        choices=[],
                        label="🏷️ Select important entities",
                        visible=True,
                        elem_classes="gr-checkbox-group"
                    )
                generate_btn = gr.Button("🧠 Generate Questions")

            with gr.Column(scale=1):
                with gr.Group(elem_classes="questions-outputs-wrapper"):
                    questions_output = gr.Textbox(
                        label="🧠 Generated Questions",
                        lines=19,
                    )
                model_selector = gr.Dropdown(
                    label="🤖 Choose a model for summarization",
                    choices=["BARTpho", "ViT5", "Gemma 3"],
                    value="BARTpho",
                )
                max_length_slider = gr.Slider(
                    minimum=4,
                    maximum=256,
                    value=256,
                    label="📏 Max output tokens",
                    scale=1,
                    interactive=True
                )
                summarize_btn = gr.Button("✂️ Summarize")

        with gr.Column():
            summary_output = gr.TextArea(
                label="✂️ Summary Result",
                interactive=False,
                lines=6,
                elem_classes="textbox-style"
            )
            clear_btn = gr.Button("🧹 Clear", variant="secondary", elem_classes="clear-button")

        def on_extract_entities(text):
            entities: list[Entity] = extract_entities(text)
            entity_choices = [
                f"{entity.entity_name} ({entity.entity_type})"
                for entity in entities
            ]
            return gr.update(choices=entity_choices, value=[])

        def on_generate_questions(text, selected_entities):
            questions: list[str] = generate_questions(text, selected_entities)
            if not questions:
                return ""
            return "\n\n".join([
                f"❓ {q}\n💬 {entity}"
                for q, entity in zip(questions, selected_entities)
            ])

        def on_clear():
            return "", gr.update(choices=[], value=[]), "", ""

        extract_btn.click(
            fn=on_extract_entities,
            inputs=[input_text],
            outputs=[entity_list]
        )

        summarize_btn.click(
            fn=summarize_text,
            inputs=[input_text, entity_list, questions_output, model_selector, max_length_slider],
            outputs=summary_output
        )

        generate_btn.click(
            fn=on_generate_questions,
            inputs=[input_text, entity_list],
            outputs=[questions_output]
        )

        clear_btn.click(
            fn=on_clear,
            inputs=[],
            outputs=[input_text, entity_list, summary_output, questions_output]
        )

    return demo

import gradio as gr
from generator import generate_response
from retrieve import embed_and_store

# Make sure embeddings are loaded on startup
embed_and_store()


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    result = generate_response(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="Asthma Knowledge Assistant") as demo:
    gr.Markdown("# 🫁 Asthma Knowledge Assistant")
    gr.Markdown(
        "Ask questions about asthma — causes, symptoms, treatments, and monitoring. "
        "Answers are grounded in Wikipedia medical articles."
    )

    with gr.Row():
        with gr.Column(scale=4):
            inp = gr.Textbox(
                label="Your question",
                placeholder="e.g. What is the difference between a rescue inhaler and a controller medication?",
                lines=2
            )
        with gr.Column(scale=1):
            btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=10)
        sources = gr.Textbox(label="Sources", lines=10)

    gr.Examples(
        examples=[
            "What physiological mechanism causes airway narrowing during an asthma attack?",
            "How does exercise-induced bronchoconstriction differ from classical asthma?",
            "What is the difference between a rescue inhaler and a controller medication?",
            "What occupational exposures are known to cause occupational asthma?",
            "How is a peak flow meter used to monitor asthma severity?"
        ],
        inputs=inp
    )

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
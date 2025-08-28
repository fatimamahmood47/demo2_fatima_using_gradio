import gradio as gr
import json
import os
import tempfile
from dotenv import load_dotenv

from app.services.order_normalizer import NormalizeCsvOrder
from app.services.order_converter import ConvertProduct
from app.schemas.detection import DetectionConfig

# Load environment variables
load_dotenv()

# --- Supplier presets ---
presets = {
    "Default Example": {
        "mixed": {"type": "concat", "cols": [0, 1], "sep": " "},
        "quantity_col": 2,
    },
    "DrugTops Supplier": {
        "mixed": {"type": "single", "cols": [0]},
        "quantity_col": 1,
    },
    "Cable Supplier": {
        "mixed": {"type": "concat", "cols": [1, 2, 3, 4], "sep": " "},  # 👈 fixed sep
        "quantity_col": 5,
    },
    "Clinic Supplier": {   # 👈 added new preset for your CSV
        "mixed": {"type": "single", "cols": [0]},
        "quantity_col": 1
    }
}

# --- CSV processing ---
def process_csv(csv_file, supplier_name):
    try:
        detection_dict = presets[supplier_name]
        detection_config = DetectionConfig(**detection_dict)

        if isinstance(csv_file, str):
            with open(csv_file, "rb") as f:
                contents = f.read()
        else:
            contents = csv_file.read()

        normalizer = NormalizeCsvOrder(contents, detection_config)
        normalized_order = normalizer.convert_to_component_list()

        converter = ConvertProduct(normalized_order)
        converted_products = converter.convert_single_order()

        # --- Save JSON to file ---
        json_data = json.dumps(
            [p.model_dump() for p in converted_products],
            indent=2,
            ensure_ascii=False
        )
        file_path = os.path.join(tempfile.gettempdir(), "converted_order.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        return json_data, file_path  # 👈 return both preview + file path

    except Exception as e:
        return f"❌ Error: {str(e)}", None


# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("# 🏗️ Order Normalization & Conversion (Gradio Version)")

    with gr.Tab("CSV Upload"):
        csv_file = gr.File(label="Upload CSV", file_types=[".csv"])
        supplier_dropdown = gr.Dropdown(
            choices=list(presets.keys()),
            value="Default Example",
            label="Choose Supplier Preset",
        )

        csv_output = gr.Textbox(label="Normalized & Converted Output", lines=20)
        csv_download = gr.File(label="Download Converted JSON")  # 👈 download option

        csv_btn = gr.Button("Process CSV")
        csv_btn.click(
            process_csv,
            inputs=[csv_file, supplier_dropdown],
            outputs=[csv_output, csv_download],
        )


# Run Gradio
if __name__ == "__main__":
    print("🚀 Starting Gradio app...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True, debug=True)

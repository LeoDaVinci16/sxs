import pandas as pd
import os
import sys
import base64
import time
from pyvis.network import Network
from pathlib import Path
from html2image import Html2Image

def normalize_id(id_val):
    """Ensures node IDs are compared consistently (e.g., '1.0' vs '1')."""
    try:
        f = float(id_val)
        if f == int(f):
            return str(int(f))
        return str(f)
    except (ValueError, TypeError):
        return str(id_val).strip()

def main(nodes_path, edges_path, output_folder, title="coordinate_network_pyvis", output_format="html", bg_image_path=None):
    # Load data
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    # Normalize IDs
    nodes_df["node"] = nodes_df["node"].apply(normalize_id)
    edges_df["source"] = edges_df["source"].apply(normalize_id)
    edges_df["target"] = edges_df["target"].apply(normalize_id)

    # Initialize Pyvis Network
    # directed=False removes arrows for a cleaner connection look
    net = Network(height="2716px", width="3840px", bgcolor="rgba(0,0,0,0)", font_color="black", directed=True)
    
    # Physics must be off to strictly follow fixed coordinates
    net.toggle_physics(False)

    # Add Nodes from coordinates
    for n_str, row in nodes_df.set_index("node").iterrows():
        n_name = str(row.get("nom", n_str))
        x, y = row["x"], row["y"]
        
        if pd.notna(x) and pd.notna(y):
            # Display name and coords in label
            label = f"{n_name}"
            
            # Pyvis nodes with shape "dot" are scaled circles.
            # We map normalized [0,1] coordinates to the [-half, +half] pixel space 
            # because Vis.js (0,0) is the center of the canvas.
            net.add_node(
                str(n_str), 
                label=label, 
                x=float(x) - 1920, 
                y=float(y) - 1358,
                fixed=True, 
                shape="dot", 
                size=8, 
                color="black",
                font={"size": 20, "face": "Arial"}
            )

    # Add Connections
    for _, row in edges_df.iterrows():
        e_name = str(row.get("DN", ""))
        #label=f"{e_name}"
        net.add_edge(str(row["source"]), str(row["target"]), label="", color="white", width=3, arrows={'to': {'enabled': True, 'scaleFactor': 0.8}})

    os.makedirs(output_folder, exist_ok=True)
    output_path = Path(output_folder) / f"{Path(title).stem}.html"
    
    net.write_html(str(output_path))
    print(f"Network diagram saved to: {output_path}")

    if bg_image_path and os.path.exists(bg_image_path):
        # Encode image to Base64 to bypass local file restrictions in headless browsers
        print(f"🖼️ Carregant imatge de fons: {bg_image_path}")
        with open(bg_image_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode('utf-8')
        
        ext = Path(bg_image_path).suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        data_uri = f"data:{mime};base64,{b64_string}"

        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        bg_style = f"""
    <style>
        html, body {{
            margin: 0 !important; 
            padding: 0 !important; 
            width: 3840px; 
            height: 2716px;
            background-color: transparent !important;
            overflow: hidden;
        }}
        #mynetwork {{
            width: 3840px !important; 
            height: 2716px !important;
            background-image: url('{data_uri}') !important;
            background-size: 100% 100% !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-color: transparent !important;
        }}
        canvas, .vis-network {{
            background-color: transparent !important;
        }}
    </style>"""
        html_content = html_content.replace("</head>", f"{bg_style}\n</head>")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    else:
        if bg_image_path:
            print(f"⚠️ Alerta: No s'ha trobat la imatge de fons a {bg_image_path}")

    if output_format.lower() == "png":
        png_filename = f"{Path(title).stem}.png"
        png_full_path = Path(output_folder) / png_filename
        
        # Instantiate Html2Image to take a screenshot of the generated HTML
        hti = Html2Image(output_path=str(output_folder), size=(3840, 2716)) 
        time.sleep(2)
        hti.screenshot(html_file=str(output_path), save_as=png_filename)
        print(f"Network PNG generat amb html2image a: {png_full_path}")
        return png_full_path

    return output_path

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[1]
    nodes = base_dir / "data" / "at_nodes.csv"
    edges = base_dir / "data" / "at_edges.csv"
    out = base_dir / "outputs" / "at" / "at_network_coord"
    # Si el mapa està a l'arrel del repo (un nivell per sobre de 'create'), usa parents[2]
    # Si està dins de 'create', manté parents[1]
    repo_root = Path(__file__).resolve().parents[1]
    img_path = repo_root / "outputs" / "at" / "at_network_coord" / "mapa_ma.png"
    main(str(nodes), str(edges), str(out), title="diagram_fixed_pyvis", output_format="png", bg_image_path=img_path)
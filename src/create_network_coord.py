import pandas as pd
import os
import sys
from pyvis.network import Network
from pathlib import Path

def normalize_id(id_val):
    """Ensures node IDs are compared consistently (e.g., '1.0' vs '1')."""
    try:
        f = float(id_val)
        if f == int(f):
            return str(int(f))
        return str(f)
    except (ValueError, TypeError):
        return str(id_val).strip()

def main(nodes_path, edges_path, output_folder, title="coordinate_network_pyvis", scaling_factor=1000):
    # Load data
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    # Normalize IDs
    nodes_df["node"] = nodes_df["node"].apply(normalize_id)
    edges_df["source"] = edges_df["source"].apply(normalize_id)
    edges_df["target"] = edges_df["target"].apply(normalize_id)

    # Initialize Pyvis Network
    # directed=False removes arrows for a cleaner connection look
    net = Network(height="100vh", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
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
            # x and y are multiplied by scaling_factor to map relative coords to pixel space.
            net.add_node(
                str(n_str), 
                label=label, 
                x=float(x) * 2 * scaling_factor, 
                y=float(y) * scaling_factor, 
                fixed=True, 
                shape="dot", 
                size=4, 
                color="black",
                font={"size": 10, "face": "Arial"}
            )

    # Add Connections
    for _, row in edges_df.iterrows():
        e_name = str(row.get("DN", ""))
        #label=f"{e_name}"
        net.add_edge(str(row["source"]), str(row["target"]), label="", color="gray", width=1, arrows={'to': {'enabled': True, 'scaleFactor': 0.4}})

    os.makedirs(output_folder, exist_ok=True)
    output_path = Path(output_folder) / f"{Path(title).stem}.html"
    
    net.write_html(str(output_path))
    print(f"Network diagram saved to: {output_path}")
    #net.show(str(output_path))
    return output_path

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[1]
    nodes = base_dir / "data" / "at_nodes.csv"
    edges = base_dir / "data" / "at_edges.csv"
    out = base_dir / "outputs" / "at" / "at_network_coord"
    main(str(nodes), str(edges), str(out), title="diagram_fixed_pyvis", scaling_factor=2000)
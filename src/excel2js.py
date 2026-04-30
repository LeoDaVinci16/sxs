# excel2js.py

import pandas as pd
from pathlib import Path
import json
from PIL import Image
from config import DATA_PUNTS, DATA_PLANOL, OUTPUT_MAPA_AT, OUTPUT_MAPA_STE

def generate_points_js(excel_input_path: Path, image_input_path: Path, output_js_folder: Path):
    """
    Llegeix un fitxer Excel amb dades de punts, calcula coordenades relatives,
    i genera un fitxer points.js per als mapes HTML a la carpeta de sortida especificada.
    """
    if not excel_input_path.exists():
        # Intentem buscar tant .xlsx com .xls
        alt_path = excel_input_path.with_suffix('.xls') if excel_input_path.suffix == '.xlsx' else excel_input_path.with_suffix('.xlsx')
        if alt_path.exists():
            excel_input_path = alt_path
        else:
            print(f"Error: Fitxer Excel no trobat a {excel_input_path}")
            return

    if not image_input_path.exists():
        print(f"Error: Fitxer d'imatge no trobat a {image_input_path}")
        return

    try:
        df = pd.read_excel(excel_input_path)
    except Exception as e:
        print(f"Error llegint el fitxer Excel {excel_input_path}: {e}")
        return

    # Assegura't que les columnes requerides existeixen
    required_cols = ["id", "x", "y"]
    if not all(col in df.columns for col in required_cols):
        print(f"Error: El fitxer Excel {excel_input_path} ha de contenir les columnes 'id', 'x' i 'y'.")
        return

    # Obté les dimensions de la imatge
    try:
        with Image.open(image_input_path) as img:
            img_width, img_height = img.size
    except Exception as e:
        print(f"Error llegint les dimensions de la imatge {image_input_path}: {e}")
        return

    points_data = []
    for _, row in df.iterrows():
        x_val = float(row["x"])
        y_val = float(row["y"])
        point = {
            "id": str(row["id"]),
            # Si ja està normalitzat (0 a 1), s'usa directament; si no, es normalitza dividint per la dimensió de la imatge
            "x_rel": x_val if 0 <= x_val <= 1 else x_val / img_width,
            "y_rel": y_val if 0 <= y_val <= 1 else y_val / img_height,
        }
        # Afegeix altres columnes dinàmicament, excloent 'id', 'x' i 'y'
        for col in df.columns:
            if col.lower() not in [c.lower() for c in required_cols]:
                # Gestiona valors buits (NaN) per a JS
                point[col] = row[col] if pd.notna(row[col]) else None
        points_data.append(point)

    # Formata com a array JavaScript
    # json.dumps gestiona la conversió de tipus Python a tipus JS (p.ex., None a null)
    js_content = f"const points = {json.dumps(points_data, indent=2, ensure_ascii=False)};"

    # Assegura't que el directori de sortida existeix
    output_js_folder.mkdir(parents=True, exist_ok=True)
    output_js_path = output_js_folder / "points.js"

    try:
        with open(output_js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        print(f"Generat amb èxit {output_js_path}")
    except Exception as e:
        print(f"Error escrivint points.js a {output_js_path}: {e}")

def main(map_type: str):
    """
    Funció principal per generar points.js per a un tipus de mapa específic (AT o STE).
    """
    if map_type == "AT":
        excel_path = DATA_PUNTS / "punts-mesura-at.xlsx"
        image_path = DATA_PLANOL / "planol-at.png"
        output_folder = OUTPUT_MAPA_AT
        print("📂 Generant points.js per a Aigua de Torres (AT)...")
    elif map_type == "STE":
        excel_path = DATA_PUNTS / "punts-mesura-ste.xlsx"
        image_path = DATA_PLANOL / "planol-ste.png"
        output_folder = OUTPUT_MAPA_STE
        print("📂 Generant points.js per a Vapor (STE)...")
    else:
        print(f"Error: Tipus de mapa desconegut '{map_type}'. Utilitza 'AT' o 'STE'.")
        return

    generate_points_js(excel_path, image_path, output_folder)
    print("✅ Generació de points.js completada.\n")

if __name__ == "__main__":
    # Exemple d'ús si s'executa directament
    main("AT")
    main("STE")
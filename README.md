# Projecte SuperSonic (sxs)

🌐 **Pàgina principal:** [Projecte SuperSònc (sxs)](https://leodavinci16.github.io/sxs/)

## Informe mesures de cabal Euromed

En aquest projecte s'han recollit els resultats del treball realitzat per mesurar cabals en diferents punts de la fàbrica d'Euromed. S'ha utilitzat el cabalímetre supersònic Flexim (Fluxus G608), d'aquí el nom **Projecte SuperSònic (sxs)**.

Posteriorment a la recollida de dades a camp, s'han automatitzat processos amb Python per generar informes, mapes i diagrames.

### Informes automatitzats

**[Informe aigua torres (AT)](https://leodavinci16.github.io/sxs/outputs/html/mapa/mapa-at/report_generated_html.html)**  
**[Informe vapor (STE)](https://leodavinci16.github.io/sxs/outputs/html/mapa/mapa-ste/report_generated_html.html)**

Sistema automatitzat que processa CSVs amb Python, genera gràfics Plotly interactius i informes Quarto (*exportables a format HTML/PDF).

### Mapes de punts de mesura

Els mapes mostren punts de mesura sobre el plànol de la fàbrica amb velocitats de cabal interactives.

**Mapa vapor** [Mapa de mesures de vapor](https://leodavinci16.github.io/sxs/outputs/html/mapa/mapa-ste/map.html)  
**Mapa aigua torres:** [Mapa de mesures aigua de torres](https://leodavinci16.github.io/sxs/outputs/html/mapa/mapa-at/map.html)

### Diagrama Sankey

Representació gràfica dels fluxos d'aigua i vapor: des del subministrament (torres de refrigeració/caldera) fins al consum final (intercanviadors/reactors).

**[Sankey AT](https://leodavinci16.github.io/sxs/outputs/html/sankey/sankey_sankey_nodes-at_20260416_1343.html)**  
**[Sankey STE](https://leodavinci16.github.io/sxs/outputs/html/sankey/sankey_sankey_nodes-ste_20260416_1347.html)**

## 📂 Estructura del repositori (actualitzada)

```bash
sxs/
│
├─ data/ 			# Dades d'usuari
│ ├─ planol/ 			# Planols fàbrica
│ ├─ punts/ 			# punts_mesura-*.xlsx
│ ├─ sankey/ 			# sankey_nodes-*.xlsx
│ └─ raw/ 			# CSVs bruts de campanyes
├─ src/ 			# Scripts Python
│ ├─ add_date.py
│ ├─ config.py
│ ├─ create_plots.py
│ ├─ create_report_html.py
│ ├─ create_report_pdf.py
│ ├─ create_sankey.py 		# Actualitzat
│ ├─ create_tkinter.py
│ ├─ excel2csv.py
│ ├─ gui.py
│ └─ points_dict.py
├─ outputs/ 			# Sortides automàtiques
│ ├─ html/
│ │ ├─ mapa/
│ │ │ ├─ mapa-at/ 		# Mapa aigua torres
│ │ │ └─ mapa-ste/ 		# Mapa vapor
│ │ └─ sankey/ 			# Diagrames Sankey HTML
│ └─ plots/ 			# PNGs de gràfics (opcional)
├─ requirements.txt
├─ .gitignore
├─ run_sxs.bat			 # Actualitzat
└─ README.md
```

**Canvis recents:**  
- `web-at/` i `web-ste/` movits a `outputs/html/mapa/mapa-at/` i `mapa-ste/`.  
- Eliminats PNGs innecessaris de `outputs/plots/`.  
- Actualitzats `data/punts/punts-mesura-ste.xlsx`, `data/sankey/sankey_nodes-ste.xlsx`, `src/create_sankey.py`, `run_sxs.bat`.

## ⚡ Característiques principals

1. **Processament CSV automàtic** (`add_date.py`): Agrupa per punts (STE‑01, AT‑E800, etc.) i extreu dates.
2. **Gràfics interactius** (`create_plots.py`): Crea imatges de cadascun dels csv amb les dades descarregades
3. **Informes dinàmics** (`create_report_html.py`/`create_report_pdf.py`): Quarto `.qmd` amb títols/dates automàtics.
4. **Mapes interactius** (`create_tkinter.py`): Visualitza velocitats sobre el plànol de la fabrica.
5. **Diagrama Sankey** (`create_sankey.py`): Balanços de cabal.
6. **GUI** (`gui.py`): Navegació per totes funcions.

## 🛠️ Flux de treball

Generar CSV → Gràfics → Informe → Excel: punts_mesura → Mapa → Excel: sankey_nodes → Diagrama


### Instal·lació

```bash
pip install -r requirements.txt
```

## ⚙️ Notes

- Noms CSV: Inclouen punt i data (ex: `20251202_095142_AT-EI906-RT.csv`).  
- Números amb zero inicial (STE‑01) per ordre correcte.  
- HTML interactiu per anàlisi; PDF per impressió.

## 👤 Autor

**Arnau Coronado Nadal**  
Estudi de cabals Euromed  
Barcelona, abril 2026
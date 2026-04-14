# supersonic-vapor

## Automated Steam Measurement Report

Aquest repositori conté un sistema completament automatitzat per generar informes de mesura per a les canonades de vapor d’Euromed. El flux de treball utilitza Python per processar dades CSV, Plotly per a gràfics interactius i Quarto per a la generació d’informes. El sistema admet tant informes HTML interactius per a l’anàlisi com informes estàtics preparats per a PDF per a la impressió.

## 📂 Estructura del repositori

```Bash
vapor/
│
├─ data                     # 
│  ├─ docs_csv              # Fitxers editables en Excel en format CSV
│  ├─ docs                  # Fitxers editables en Excel  
│  └─ raw                   # Fitxers CSV en brut de campanyes de mesura
├─ src/                     # Scripts de Python
│  ├─ add_date.py           # Funcions per afegir dates als noms dels fitxers en brut
│  ├─ create_map.py         # Funcions per crear el mapa d’Euromed
│  ├─ create_plots.py       # Funcions per carregar CSVs i generar gràfics interactius/estàtics
│  ├─ create_report_html.py # Funcions per crear l’informe en format HTML
│  ├─ create_report_pdf.py  # Funcions per crear l’informe en format PDF
│  ├─ create_sankey.py      # Funcions per crear el diagrama de Sankey
│  ├─ create_tkinter.py     # Funcions per crear el mapa d’Euromed (versió actualitzada)
│  ├─ excel2csv.py          # Funcions per carregar CSVs i generar gràfics interactius/estàtics
│  ├─ gui.py                # Codi que crea la interfície gràfica (GUI) que utilitza totes les funcions
│  └─ points_dict.py        # Diccionari amb els noms dels punts i el seu identificador
├─ outputs/                 # Carpeta opcional per a PNGs o figures exportades
├─ report_vapor.qmd         # Informe principal de Quarto (HTML + PDF opcional)
├─ report_generated.qmd     # QMD generat dinàmicament des de Python
└─ README.md                # Aquest fitxer
```

## ⚡ Característiques
1. Processament automàtic de CSV (add_date.py)
    - Detecta fitxers CSV a data/raw/
    - Agrupa fitxers per punts de mesura (STE-1, STE-2, …, E800, PEC)
    - Extreu automàticament la data de mesura dels noms dels fitxers
2. Generació de gràfics interactius (create_plots.py)
    - Té dues funcions:
    2.1. Batch plot
        - Per crear els gràfics de tots els arxius csv que hi ha a raw
    2.2. Previsualitza un gràfic
        - Utilitza Plotly per a gràfics HTML interactius
        - Les figures s’integren dins l’informe Quarto per a anàlisi immediata
        - La mida dels gràfics es pot ajustar dinàmicament (això potser es mentida)
3. Creació dinàmica d’informes (create_report_html.py/create_report_pdf.py)
    - A partir dels grafics generats es pot crear un informe que recull totes les dades.
    - Python create_report.py genera el fitxer Quarto markdown (.qmd)
    - Títols, dates i seccions s’afegeixen automàticament segons els CSV
    - Els blocs de codi es poden ocultar per a un informe més net
    - Els arxius de quarto estan preparats per exportar directament a html per visualitzar els gràfics interactivament o en pdf per imprimir.
4. Creació de planol amb els punts analitzats (create_map.py)
    - A partir de les dades es poden recopilar en un excel (punts_mesura) les velocitats en els diferents punts
    - El programa crea un mapa per visualitzar de forma interactiva aquestes dades recopilades sobre el terreny.
5. Creació de diagrama sankey (crate_sankey.py)
    - A partir de les dades es pot omplir l'excel de sankey_nodes
    - Amb aquestes dades es genera un diagrama amb els balanços de cabal tipus sankey
6. GUI per executar totes aquestes comandes.
    - Permet navegar per totes aquestes funcions.
    - A la GUI li falta implementar la creació dinamica d'informes.

## 🛠️ Flux de treball 
0. Instal·lar dependències

Millor instalar el "enviroment" `requirements.yml`

```bash
pip install pandas plotly kaleido quarto
```

`kaleido` is required for exporting Plotly figures to PNG.

`quarto` must be installed for rendering QMD files.

Disclaimer: No se si només kalideo i quarto son suficients!

Generar csv > generar grafiques > generar informe > editar excel punts_mesura > generar i visualitzar mapa > editar excel sankey_nodes > generar i visualitzar diagrama

## 🧩 Personaliotzació
- Variables to plot: Edit the variables_to_plot list in create_report.py
- Figure size: Adjust in create_plotly_plot() or write_image()
- Measurement point detection: Modify the regex in point_sort_key() for custom naming schemes

## ⚙️ Notes
- Mantén HTML interactiu per a l’anàlisi; utilitza PNG per a PDF/impressió
- Els noms dels CSV han d’incloure el punt de mesura (p. ex. STE-2) i la data (YYYYMMDD)
- Els números STE amb zero inicial (p. ex. STE-01) asseguren l’ordre correcte

## 👤 Autor

Arnau Coronado Nadal
Estudi de cabals Euromed

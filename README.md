# Projecte SuperSonic (sxs)

🌐 Pàgina principal: [Mapa de mesures de vapor](https://leodavinci16.github.io/sxs/)

## Informe mesures de cabal Euromed

En aquest projecte s'han recollit els resultats del treball realitzat per medir els cabals en diferents punts de la fabrica. Per fer aquesta feina s'ha fet servir el cabalímetre supersònic de Flexim (Fluxus G608), per això s'ha anomenat Projecte SuperSònic (sxs).

Posterior a la recollida de dades a camp s'han automatitzat els següents processos, emprant sobretot python:

### Informe automatitzat de mesures de cabal

[Veure informe aigua de torres](https://leodavinci16.github.io/sxs/web-at/report_generated_html.html)

[Veure informe vapor](https://leodavinci16.github.io/sxs/web-ste/report_generated_html.html)

Aquest repositori conté un sistema completament automatitzat per generar informes de mesura per a les canonades de vapor d’Euromed. El flux de treball utilitza Python per processar dades CSV, Plotly per a gràfics interactius i Quarto per a la generació d’informes. El sistema admet tant informes HTML interactius per a l’anàlisi com informes estàtics preparats per a PDF per a la impressió.

### Punts de mesura: Mapa d'Euromed

[Veure mapa de les mesures d'aigua de torres](https://leodavinci16.github.io/sxs/web-at/map.html)

[Veure mapa de les mesures vapor](https://leodavinci16.github.io/sxs/web-ste/map.html)

Per representar els resultats en cada punt de mesura s'ha fet un mapa que mostra els punts de mesura i mostra en pantalla el valor mesurat en aquest punt. S'ha fet 

### Diagrama sankey:

Finalment s'han fet els diagrames sankey dels fluxos d'aigua o vapor des del subministrament (torres de refrigeració o caldera) fins al consum (intercanviadors de calor o camises dels reactors)

## 📂 Estructura del repositori

```Bash
sxs/
│
├─ data                     # Dades de l'usuari 
│  ├─ planol                # Planol de la fabrica
│  ├─ punts                 # Punts de mesura 
│  ├─ sankey                # Nodes del diagrama de sankey  
│  └─ raw                   # Fitxers CSV en brut de campanyes de mesura
├─ src/                     # Scripts de Python
│  ├─ add_date.py           # Funcions per afegir dates als noms dels fitxers en brut
│  ├─ config.py             # Distribució de les carpetes de "data"
│  ├─ create_plots.py       # Funcions per carregar CSVs i generar gràfics interactius/estàtics
│  ├─ create_report_html.py # Funcions per crear l’informe en format HTML
│  ├─ create_report_pdf.py  # Funcions per crear l’informe en format PDF
│  ├─ create_sankey.py      # Funcions per crear el diagrama de Sankey
│  ├─ create_tkinter.py     # Funcions per crear el mapa d’Euromed (versió actualitzada)
│  ├─ excel2csv.py          # Funcions per carregar CSVs i generar gràfics interactius/estàtics
│  ├─ gui.py                # Codi que crea la interfície gràfica (GUI) que utilitza totes les funcions
│  └─ points_dict.py        # Diccionari amb els noms dels punts i el seu identificador
├─ outputs/                 # Carpeta opcional per a PNGs o figures exportades (es crea automaticament)
├─ requirements.txt         # Per crear un enviroment amb conda o descarregar les dependencies amb git
├─ .gitignore               # per git
├─ run_sxs.bat              # Per obrir la gui amb windows com una apicació
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
4. Creació de planol amb els punts analitzats (create_map.py (legacy), create_tkinter.py)
    - A partir de les dades es poden recopilar en un excel (punts_mesura) les velocitats en els diferents punts.
    - El programa crea un mapa per visualitzar de forma interactiva aquestes dades recopilades sobre el terreny.
5. Creació de diagrama sankey (crate_sankey.py)
    - A partir de les dades es pot omplir l'excel de sankey_nodes
    - Amb aquestes dades es genera un diagrama amb els balanços de cabal tipus sankey
6. GUI per executar totes aquestes comandes.
    - Permet navegar per totes aquestes funcions.
    - A la GUI li falta implementar la creació dinamica d'informes.

## 🛠️ Flux de treball 
0. Instal·lar dependències

Millor instalar el "enviroment" a través de l'arxiu `requirements.txt`

```bash
pip install pandas plotly kaleido quarto
```

`kaleido` is required for exporting Plotly figures to PNG.

`quarto` must be installed for rendering QMD files.

Disclaimer: No se si només kalideo i quarto son suficients!

Generar csv > generar grafiques > generar informe > editar excel punts_mesura > generar i visualitzar mapa > editar excel sankey_nodes > generar i visualitzar diagrama

## 🧩 Personalització
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

# Projecte de Visualització i Processament de Mesures SXS

Aquest projecte automatitza la gestió, processament i visualització de dades de mesurament de la fàbrica, generant gràfics, mapes, i diagrames Sankey de manera modular i flexible.  

---

## Estructura de Carpetes

```
sxs/
├─ data/
│ ├─ raw/ # Fitxers CSV originals amb mesures
│ ├─ configutrations.zip # Fitxers originals del programa de flexim
│ ├─ planol.png # Imatge de la planta d'Euromed
│ └─ csv/ # els excels convertits en csv
├─ docs/ # Els documents excel que s'editen amb les dades obtingudes de la fabrica
│ ├─ punts-mesura.xlsx # Le dades dels punts de mesura
│ └─ sankey_nodes.xlsx # Les dades per fer la representació de sankey els cabals
├─ notebooks/ # Prototips i anàlisi interactiva (opcional)
├─ outputs/
│ ├─ plots/ # Gràfics generats automàticament
│ ├─ images/ # Imatges generades
│ └─  # Altres carpetes que es puguin generar amb els outputs (manualment)
├─ src
│ ├─ add_date.py # Processament i afegit de dates a CSV/Excel
│ ├─ create_map.py # Visualització de punts sobre plànol
│ ├─ create_plots.py # Generació de gràfics de variables
│ ├─ create_sankey.py # Generació de diagrames Sankey
│ ├─ excel2csv.py # Conversió automàtica de fitxers Excel a CSV
│ └─ points_dict.py # Mapeig ID punts → noms humans
├─ requirements.txt
├─ .gitignore
├─ README_en.md
└─ README.md
```

---

## Flux de Treball

1. **Entrades de Dades**
   - Excel amb punts de mesura (`data/docs/`) – diàmetres i altres dades sobre cada punt.
   - CSV amb mesures recollides (`data/raw/`) – dades actuals dels cabals de la fàbrica.
   - Excel de referència/addicional (`data/raw/`) – informació complementària.

2. **Processament de Dades**
   - Validació de columnes numèriques.
   - Conversió de fitxers Excel a CSV si cal (`excel2csv.py`).
   - Afegir dates i metadades al nom dels fitxers (`add_date.py`).

3. **Generació de Gràfics i Mapes**
   - Gràfics de variables per punts de mesura (`create_plots.py`).
   - Mapes interactius amb punts sobre el plànol de la fàbrica (`create_map.py`).
     - Permet clicar sobre punts per veure dades.
     - Opció de mostrar/amagar tots els valors amb un botó.
     - Permet escollir quines dades mostra
   - Desar els gràfics a `outputs/plots/` i imatges a `outputs/images/`.

4. **Plantilles Excel**
   - Visualitzar les dades recapitulades a camp i expressades ls gràfics i als mapes interactius generats als punts anteriors.
   - Omplir plantilles d'Excel amb les dades processades a `docs/sankey_nodes.xlsx`..
   - Desa aquestes taules en format CSV a `data/csv/`.

5. **Diagrames Sankey**
   - Visualització de fluxos i cabals entre punts (`create_sankey.py`).
   - Utilitza els arxius en format CSV de `data/csv/` encara que accepta fitxers CSV o Excel.
   - Permet seleccionar la columna de magnitud (Diàmetre, cabal, etc.).



---

## Com Utilitzar el Projecte

1. Col·loca els nous fitxers Excel de mesurament a `data/raw/`.  
2. Assegura’t que les plantilles estan a `docs/`.  
3. Executa els scripts des de `src/` segons la funcionalitat:

   ```bash
   # Generar gràfics de variables
   python create_plots.py

   # Visualitzar punts sobre el plànol
   python create_map.py

   # Generar Sankey diagrams
   python create_sankey.py <fitxer_excel_o_csv>

Revisa outputs/ per als gràfics, imatges i diagrames generats.

Les plantilles Excel actualitzades es desaran a data/processed/.

## Notes

El flux de treball és modular: es poden afegir noves dades sense modificar el codi.

Les plantilles Excel han de seguir el format correcte per omplir-se automàticament.

Es recomana mantenir separades les entrades (`data/raw/`), plantilles (`docs/`) i sortides (`outputs/`) per claredat i reproducibilitat.

Git només fa seguiment dels scripts i plantilles i les dades en CSV; Excels i `outputs/` estan ignorats via .gitignore.

Es recomana usar create_map.py i create_sankey.py per a visualitzacions interactives i diagrames de flux respectivament.
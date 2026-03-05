# Projecte de Visualització i Processament de Mesures SXS

Aquest projecte automatitza la gestió, processament i visualització de dades de mesurament de la fàbrica, generant gràfics, mapes, i diagrames Sankey de manera modular i flexible.  

---

## Estructura de Carpetes

```
sxs/
├─ data/
│ ├─ raw/ # Fitxers Excel originals amb mesures
│ ├─ processed/ # Fitxers Excel processats o generats
│ └─ templates/ # Plantilles Excel per dibuixos i plots
├─ outputs/
│ ├─ plots/ # Gràfics generats automàticament
│ ├─ images/ # Visualitzacions de la fàbrica
│ └─ diagrams/ # Diagrames tipus SCADA i Sankey
├─ src/
│ ├─ create_map.py # Visualització de punts sobre plànol
│ ├─ create_sankey.py # Generació de diagrames Sankey
│ ├─ create_plots.py # Generació de gràfics de variables
│ ├─ add_date.py # Processament i afegit de dates a CSV/Excel
│ ├─ excel2csv.py # Conversió automàtica de fitxers Excel a CSV
│ ├─ paths.py # Rutes constants del projecte
│ ├─ points_dict.py # Mapeig ID punts → noms humans
│ └─ utils.py # Funcions auxiliars generals
├─ docs/ # Documentació, plànols, notes
├─ notebooks/ # Prototips i anàlisi interactiva (opcional)
└─ README.md
```

---

## Flux de Treball

1. **Entrades de Dades**
   - Excel amb punts de mesura (`data/templates/`) – plantilla per dibuixar els punts.
   - Excel amb mesures recollides (`data/raw/`) – dades actuals de la fàbrica.
   - Excel de referència/addicional (`data/raw/`) – informació complementària.

2. **Processament de Dades**
   - Normalització i neteja de les dades.
   - Validació de columnes numèriques.
   - Conversió de fitxers Excel a CSV si cal (`excel2csv.py`).
   - Afegir dates i metadades a fitxers (`add_date.py`).

3. **Generació de Gràfics i Mapes**
   - Gràfics de variables per punts de mesura (`create_plots.py`).
   - Mapes interactius amb punts sobre el plànol de la fàbrica (`create_map.py`).
     - Permet clicar sobre punts per veure dades.
     - Opció de mostrar/amagar tots els valors amb un botó.
   - Desar els gràfics a `outputs/plots/` i imatges a `outputs/images/`.

4. **Diagrames Sankey**
   - Visualització de fluxos i cabals entre punts (`create_sankey.py`).
   - Accepta fitxers CSV o Excel.
   - Permet seleccionar la columna de magnitud.

5. **Plantilles Excel**
   - Omplir plantilles amb les dades processades.
   - Desa resultats a `data/processed/`.

---

## Com Utilitzar el Projecte

1. Col·loca els nous fitxers Excel de mesurament a `data/raw/`.  
2. Assegura’t que les plantilles estan a `data/templates/`.  
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

Es recomana mantenir separades les entrades (data/raw/), plantilles (data/templates/) i sortides (outputs/) per claredat i reproducibilitat.

Git només fa seguiment dels scripts i plantilles; outputs/ i data/processed/ estan ignorats via .gitignore.

Es recomana usar create_map.py i create_sankey.py per a visualitzacions interactives i diagrames de flux respectivament.
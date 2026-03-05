# Projecte de Visualització de Mesures SXS

Aquest projecte està dissenyat per automatitzar i visualitzar dades de mesurament de la fàbrica, generar gràfics i omplir plantilles Excel amb les dades recollides. El flux de treball és modular i flexible, de manera que pot adaptar-se a noves dades i actualitzacions fàcilment.

## Estructura de Carpetes

L’estructura recomanada per al projecte:

```
sxs/
├─ data/
│ ├─ raw/ # Fitxers Excel originals (AT, STE, Impulsio)
│ ├─ processed/ # Fitxers Excel nets o generats
│ └─ templates/ # Plantilles Excel per dibuixos
├─ outputs/
│ ├─ plots/ # Gràfics generats automàticament
│ ├─ images/ # Visualitzacions de la fàbrica
│ └─ diagrams/ # Diagrames tipus SCADA
├─ src/
│ ├─ main.py # Script principal del flux de treball
│ ├─ utils.py # Funcions auxiliars
│ └─ plot_factory.py
├─ docs/ # Documentació i notes del projecte
├─ notebooks/ # Notebooks opcionals per prototips
└─ README.md
```

## Resum del Flux de Treball

El programa automatitza el processament de dades de mesura i la seva visualització:

### 1. Entrades de Dades

Excel per dibuixos (data/templates/) – plantilla per plotar punts de mesura

Excel amb mesures de cabal (data/raw/) – conté les dades recollides de la fàbrica

Excel “Aub Sauley” (data/raw/) – informació addicional de referència

Els fitxers Excel 1 i 3 són plantilles, mentre que Excel 2 és dinàmic i s’actualitza amb noves mesures.

### 2. Passos del Processament

Descarregar i normalitzar dades

Carregar les noves dades de mesura (Excel 2)

Netejar i validar els valors si cal

Generar gràfics

Visualitzar les mesures de cabal de cada punt

Desar els gràfics a outputs/plots/

### 3. Omplir Plantilles Excel

Utilitzar les mesures d’Excel 2 per omplir la plantilla de dibuixos (Excel 1)

Desar els fitxers actualitzats a data/processed/

### 4. Visualització de la Fàbrica

Generar diagrames tipus SCADA amb els punts de mesura

Desar les visualitzacions a outputs/images/ i outputs/diagrams/

### 5. Actualitzar Excel “Sanley”

Omplir Excel 3 amb la informació processada per a informes

### 6. Diagrames Sankey opcionals

Visualitzar els fluxos de manera flexible segons les dades processades

## Com Utilitzar-ho

Col·loca tots els nous fitxers Excel de mesurament a data/raw/

Assegura’t que les plantilles estiguin a data/templates/

Executa l’script principal:
```
cd src
python main.py
```
Revisa outputs/ per als gràfics, imatges i diagrames generats

Les plantilles Excel actualitzades es desaran a data/processed/

## Notes

El flux de treball és modular; es poden afegir noves dades en qualsevol moment sense modificar el codi

Les plantilles Excel han de seguir el format correcte per omplir-se automàticament

El programa separa les entrades de dades, el processament i les sortides per mantenir claredat i reproducibilitat

Git només fa seguiment dels scripts i plantilles; outputs/ i data/processed/ poden ignorar-se amb .gitignore
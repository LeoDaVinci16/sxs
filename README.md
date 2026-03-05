# SXS Measurement Visualization Project

This project is designed to automate and visualize measurement data from the factory, generate plots, and fill Excel templates with the collected data. The workflow is modular and flexible so it can accommodate updates and new data easily.

## Directory Structure

The recommended structure for the project:

sxs/
├─ data/
│ ├─ raw/ # Original Excel files (AT, STE, Impulsio)
│ ├─ processed/ # Cleaned or generated Excel files
│ └─ templates/ # Excel templates for drawings
├─ outputs/
│ ├─ plots/ # Automatically generated plots
│ ├─ images/ # Factory visualization snapshots
│ └─ diagrams/ # SCADA-style diagrams
├─ src/
│ ├─ main.py # Main workflow script
│ ├─ utils.py # Helper functions
│ └─ plot_factory.py
├─ docs/ # Documentation and workflow notes
├─ notebooks/ # Optional notebooks for prototyping
└─ README.md

## Workflow Overview

The program automates the processing of measurement data and visualization:

### 1. Data Inputs

Excel for drawings (data/templates/) – template to plot measurement points

Excel with flow measurements (data/raw/) – contains the measurement data collected from the factory

Excel “Aub Sauley” (data/raw/) – additional reference information

Excel 1 and 3 are templates, while Excel 2 is dynamic and updated from measurement sessions.

### 2. Processing Steps

Download and normalize data

Load new measurement data (Excel 2)

Clean and validate values if needed

Generate plots

Visualize flow measurements at each point

Save plots in outputs/plots/

### 3. Fill Excel templates

Use Excel 2 measurements to populate the drawing template (Excel 1)

Save updated templates in data/processed/

### 4. Factory visualization

Generate SCADA-style diagrams showing measurement points

Save visualizations in outputs/images/ and outputs/diagrams/

### 5. Update “Sanley” Excel

Populate Excel 3 with processed information for reporting

### 6. Optional Sankey diagrams

Visualize flows flexibly based on processed data

## How to Use

Place all new measurement Excel files in data/raw/.

Ensure template files are in data/templates/.

Run the main script:

cd src
python main.py

Check outputs/ for generated plots, images, and diagrams.

Updated Excel templates are saved in data/processed/.

## Notes

The workflow is modular; new data can be added anytime without modifying the code.

Excel templates must follow the correct format for automated filling.

The program separates data inputs, processing, and outputs for clarity and reproducibility.

Git tracks only scripts and templates; outputs/ and processed files can be ignored in .gitignore.
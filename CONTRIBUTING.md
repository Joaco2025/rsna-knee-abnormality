# Contribuir

## Flujo de git

- No se trabaja directo sobre `main`.
- Cada integrante trabaja en su rama `feature/...` y abre PR hacia `main`.
- Al menos un review antes de merge.

```
main
├── feature/dataset-audit
├── feature/dicom-loader
├── feature/label-analysis
└── feature/baseline
```

## Reparto propuesto (4 integrantes)

**1. Dataset / Data Engineering**
`train.csv`, `train_series.csv`, relaciones Study↔Series, estadísticas,
catálogo, auditoría → `notebooks/01_dataset_audit.ipynb`.

**2. DICOM / MRI**
Lectura DICOM, metadata, ordenamiento de slices, reconstrucción de series,
visualización, orientación, preprocessing inicial → `src/rsna_knee/data/dicom.py`,
`series.py`.

**3. Labels / NLP**
Análisis de los 12 targets, distribución, reportes, idiomas, extracción de
información, pseudo-labeling → `notebooks/03_label_analysis.ipynb`,
`04_report_analysis.ipynb`.

**4. ML**
Baseline, dataset PyTorch, entrenamiento, evaluación, métricas,
experimentación → `src/rsna_knee/training/`.

Todos deben conocer la estructura común: todo se conecta vía
`StudyInstanceUID`.

## Antes de empezar

1. Clonar el repo y crear entorno (`pip install -r requirements.txt`).
2. Confirmar acceso a los datos (`data/raw/`, ver `data/README.md`).
3. No commitear datos, pesos de modelos, ni `kaggle.json`.

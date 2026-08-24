# Notebooks

Notebooks de exploración y análisis. El código que se vuelve parte del
pipeline reutilizable pasa a `src/rsna_knee/`, no debe quedarse atrapado aquí.

Secuencia planeada:

- `01_dataset_audit.ipynb` — conteos, distribuciones, relaciones Study↔Series,
  mapa completo del dataset (train/test, labels, planos, fluid/fat-supp).
- `02_dicom_exploration.ipynb` — lectura de metadata sin pixels, catálogo
  DICOM, ordenamiento de slices, reconstrucción de una serie, visualización.
- `03_label_analysis.ipynb` — análisis de los 58 estudios etiquetados:
  positivos por clase, co-ocurrencias, imbalance, correlaciones.
- `04_report_analysis.ipynb` — idiomas, longitud, estructura de los reportes,
  factibilidad de extracción de labels (pseudo-labeling) para los 4,349
  estudios sin ground truth explícito.
- `05_baseline.ipynb` — primer modelo end-to-end (single slice/serie → CNN),
  con el único objetivo de tener una referencia reproducible.

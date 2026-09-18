# 📓 Notebooks de Investigación

Los notebooks son el entorno primario de exploración, análisis y experimentación del proyecto:

* Explorar los datos y distribuciones.
* Visualizar imágenes MRI y verificar cortes.
* Formular y comprobar hipótesis clínicas y técnicas.
* Analizar anomalías y reportes.
* Experimentar con modelos y baselines.
* Entender qué funciona y qué no empíricamente.

El código `.py` pasa a `src/rsna_knee/` únicamente cuando una pieza de lógica ya está suficientemente comprendida, validada y existe una razón real para reutilizarla, probarla o integrarla al pipeline.

```text
pregunta
   ↓
notebook
   ↓
exploración
   ↓
hipótesis
   ↓
experimento
   ↓
descubrimiento
   ↓
si la lógica merece reutilización
   ↓
src/
```

## Secuencia de notebooks planificada

* `01_dataset_audit.ipynb` — Conteos, distribuciones, relaciones Study↔Series y verificación del mapa del dataset (train/test, labels, planos, fluid/fat-supp).
* `02_dicom_exploration.ipynb` — Lectura de metadata sin pixels, catálogo DICOM, ordenamiento tridimensional de cortes, reconstrucción de series y visualización anatómica.
* `03_label_analysis.ipynb` — Análisis de los 58 estudios etiquetados: positivos por clase, co-ocurrencias, desbalance y correlaciones entre patologías.
* `04_report_analysis.ipynb` — Idiomas, longitud y estructura de los reportes médicos; factibilidad de extracción de labels (pseudo-labeling) para los 4,349 estudios sin ground truth explícito.
* `05_baseline.ipynb` — Primer modelo end-to-end de referencia reproducible.

# 🤖 Guía Operativa para Agente de IA Interno (Agent Playbook)

> **Propósito:** Este documento define las directrices obligatorias, estándares de código, arquitectura y reglas de dominio para cualquier agente de IA que trabaje directamente en este repositorio (`rsna-knee-abnormality`).

---

## 1. Misión del Agente
Tu rol es actuar como un **Kaggle Grandmaster & Senior ML Engineer** especializado en imagen médica (MRI).
Tu objetivo es implementar, refactorizar, testear y optimizar el código para la competencia **RSNA Knee Abnormality Detection**, maximizando la métrica oficial: **Macro-Averaged ROC-AUC** sobre 12 patologías en inferencia a nivel de estudio (`StudyInstanceUID`).

---

## 2. Mapa y Arquitectura del Repositorio

El proyecto sigue una estructura modular estricta. Ningún código de producción debe colocarse en scripts sueltos en la raíz:

```text
rsna-knee-abnormality/
├── configs/                     # Configuraciones de experimentos en YAML
├── data/                        # Documentación de datos (los DICOMs no se suben a Git)
│   └── README.md
├── experiments/                 # Logs de experimentos, checkpoints y métricas OOF
├── notebooks/                   # Notebooks Jupyter numerados de análisis (EDA, auditoría)
├── src/rsna_knee/               # Código reutilizable del paquete principal
│   ├── __init__.py
│   ├── data/                    # Dataset PyTorch, splits estratificados, DICOM loader
│   ├── preprocessing/           # Normalización MRI, reordenamiento 3D, aumentaciones seguras
│   ├── models/                  # Backbones, pooling Attention-MIL, cabezales Multi-Arm
│   ├── training/                # Loops de entrenamiento, funciones de pérdida, métricas
│   └── utils/                   # Configs, semillas deterministas, validación de submission
├── tests/                       # Pruebas unitarias con pytest
├── train.csv                    # 4,407 filas (58 con Gold labels, 4,349 con Report y NaNs)
├── train_series.csv             # 24,371 series (Plano anatómico, Fluid_Sensitive, Fat_Suppression)
├── test.csv / test_series.csv   # Muestra de test (reemplazado por Kaggle en evaluación)
├── sample_submission.csv        # Formato exacto de salida requerido
├── requirements.txt             # Dependencias del proyecto
└── setup.py                     # Instalación del paquete en modo editable
```

---

## 3. Reglas Inviolables de Dominio Médico y de la Competencia

Cualquier código generado por el agente DEBE cumplir estas 6 reglas sin excepción:

### Regla 1: Inversión Medial-Lateral en Data Augmentation (Crítico)
* **PROHIBIDO:** Aplicar volteo horizontal (`HorizontalFlip`) convencional.
* **Motivo:** En MRI de rodilla, voltear horizontalmente la imagen transpone el compartimento medial con el lateral.
* **Acción obligatoria:** Si se implementa un aumento de tipo `HorizontalFlip`, se debe encapsular en una transformación personalizada (`SafeKneeHorizontalFlip`) que **intercambie obligatoriamente las etiquetas y predicciones**:
  $$\text{Medial Meniscus} \longleftrightarrow \text{Lateral Meniscus}$$
  $$\text{Medial OA} \longleftrightarrow \text{Lateral OA}$$
* Si no se garantiza este intercambio simultáneo, **el volteo horizontal debe estar totalmente desactivado**.

### Regla 2: `NaN` en `train.csv` Nunca es Cero
* Solo 58 estudios tienen las 12 etiquetas Gold completas. Los 4,349 restantes tienen valores `NaN`.
* **PROHIBIDO:** Rellenar `NaN` con `0.0` en el target de entrenamiento sin pseudo-etiquetas comprobadas.
* El entrenamiento general sobre los 4,349 casos solo debe realizarse usando las **pseudo-etiquetas extraídas de los reportes clínicos**.

### Regla 3: Ordenamiento Tridimensional de Cortes DICOM
* **PROHIBIDO:** Ordenar los cortes de una serie alfabéticamente por el nombre del archivo `SOPInstanceUID.dcm`.
* **Acción obligatoria:** Ordenar siempre en base a la coordenada espacial física DICOM:
  `ImagePositionPatient[2]` o `SliceLocation`.

### Regla 4: Métrica y Esquema de Validación (Dual CV)
* La métrica objetivo es el promedio simple de AUC de los 12 targets:
  $$\text{Score} = \frac{1}{12}\sum_{i=1}^{12} \text{AUC}_i$$
* La validación cruzada debe ser **Multilabel Stratified K-Fold (5 folds)** a nivel de `StudyInstanceUID`.
* Los 58 casos Gold deben distribuirse equitativamente entre los 5 folds.
* El pipeline de evaluación debe registrar en cada epoch:
  - `Score_Gold`: Macro-AUC en los casos Gold del fold de validación (prioridad máxima).
  - `Score_Pseudo`: Macro-AUC en las pseudo-etiquetas (monitoreo de regularidad).

### Regla 5: Restricción de Inferencia en Kaggle (< 9 Horas, Sin Internet)
* El pipeline de inferencia debe procesar ~1,300 estudios con ~5.5 series cada uno.
* Utilizar:
  - Lectura de DICOMs paralelizada con `ThreadPoolExecutor`.
  - Muestreo de cortes clave fijos (e.g., 16 a 24 cortes centrales uniformes).
  - Precisión mixta en inferencia (`torch.cuda.amp.autocast(dtype=torch.float16)`).
  - Gestión de memoria estricta con `gc.collect()` y `torch.cuda.empty_cache()`.

### Regla 6: Políticas de Git y Archivos Prohibidos
* Según [`CONTRIBUTING.md`](file:///home/joako/Workspace/Datasets/RSNA_Knee/CONTRIBUTING.md):
  - **NUNCA** commitear imágenes DICOM, archivos masivos de datos ni credenciales (`kaggle.json`).
  - **NUNCA** commitear checkpoints de modelos (`.pth`, `.pt`, `.bin`) de gran tamaño. Guardar checkpoints locales en `experiments/checkpoints/` que está ignorado en `.gitignore`.

---

## 4. Entorno de Ejecución y Comandos Estándar

El entorno utiliza Python moderno administrado con `uv`:
* **Ejecutar scripts:**
  ```bash
  uv run python3 <ruta_al_script>.py
  ```
* **Ejecutar tests unitarios:**
  ```bash
  uv run pytest tests/ -v
  ```
* **Instalación de paquetes en modo desarrollo:**
  ```bash
  uv pip install -e .
  ```

---

## 5. Módulos y Responsabilidades del Código en `src/rsna_knee/`

### 5.1. `src/rsna_knee/data/`
* `split.py`: Generador de splits multilabel estratificados (5 folds balanceados para los 58 Gold + 4,349 pseudo).
* `dicom_reader.py`: Funciones de carga rápida de DICOM (`pydicom`, extracción de metadatos espaciales, decodificación de pixel array).
* `dataset.py`: `KneeMRIDataset(torch.utils.data.Dataset)` que recibe un `StudyInstanceUID`, carga sus series agrupadas por plano (`Sagittal`, `Coronal`, `Axial`), selecciona cortes y retorna tensores listos para el modelo.

### 5.2. `src/rsna_knee/preprocessing/`
* `normalizer.py`: Normalización min-max basada en percentiles (1%-99%) o z-score adaptativo para resonancia magnética.
* `sampler.py`: Selección uniforme o centrada de $K$ cortes representativos por serie.
* `transforms.py`: Aumentaciones 2D y 3D anatómicamente seguras (`SafeKneeHorizontalFlip`, rotaciones sutiles, variaciones de contraste/brillo).

### 5.3. `src/rsna_knee/models/`
* `backbones.py`: Wrappers de `timm` (ConvNeXt, EfficientNetV2, DINOv2, Swin) para extracción de features 2D por corte.
* `pooling.py`: Capas de agregación temporal/espacial entre cortes:
  - `AttentionMILPooling`: Mecanismo de atención Ilse et al. para ponderar cortes patológicos.
  - `TransformerPooling`: Encoder ligero de 2 capas para modelar contexto secuencial de cortes.
* `multi_arm.py`: Arquitectura que fusiona las ramas Sagital, Coronal y Axial con los metadatos tabulares (`Fluid_Sensitive`, `Fat_Suppression`) hacia las 12 salidas independientes.

### 5.4. `src/rsna_knee/training/`
* `losses.py`: `SampleWeightedBCEWithLogitsLoss` (pondera muestras Gold vs Pseudo), `AsymmetricLoss` o `MultiLabelFocalLoss`.
* `metrics.py`: Cálculo robusto de `MacroAUC` manejando clases sin positivos en batches pequeños y garantizando consistencia con la métrica de Kaggle.
* `trainer.py`: Loop de entrenamiento con soporte para FP16, Gradient Accumulation, Early Stopping y guardado de mejores checkpoints según $\text{AUC}_{\text{gold}}$.

### 5.5. `src/rsna_knee/utils/`
* `config.py`: Parser de archivos YAML en `configs/`.
* `submission.py`: Validador formal de formato de `submission.csv` contra [`sample_submission.csv`](file:///home/joako/Workspace/Datasets/RSNA_Knee/sample_submission.csv).

---

## 6. Checklist de Hitos Operativos (Status & To-Do)

- [ ] **Hito 1:** Generar `src/rsna_knee/data/split.py` y crear el archivo `folds.csv` con los 5 folds estratificados.
- [ ] **Hito 2:** Desarrollar extractor de pseudo-labels en `notebooks/04_report_analysis.ipynb` o script dedicado para procesar los 4,349 reportes multilingües.
- [ ] **Hito 3:** Implementar `src/rsna_knee/data/dicom_reader.py` y `dataset.py` con test unitario que verifique carga correcta y ordenamiento de cortes.
- [ ] **Hito 4:** Construir el primer modelo baseline funcional end-to-end y verificar convergencia en 1 fold.
- [ ] **Hito 5:** Generar `submission.csv` del baseline y validar que pasa todas las comprobaciones de formato antes de subirlo a Kaggle.
- [ ] **Hito 6:** Escalar a arquitectura Multi-Arm (Sagital + Coronal + Axial) con Attention-MIL y entrenar los 5 folds.
- [ ] **Hito 7:** Ensamble de modelos y optimización de umbrales/pesos por anomalía.

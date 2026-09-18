# 📁 Estructura del Proyecto: RSNA Knee Abnormality Detection

Este documento describe detalladamente la arquitectura, organización de directorios y el propósito de cada archivo del repositorio `rsna-knee-abnormality`.

---

## 🧭 Visión General

El proyecto está diseñado para competir en la competencia de Kaggle **RSNA Knee Abnormality Detection**. El objetivo es predecir la probabilidad de 12 anomalías de rodilla a nivel de **estudio completo (`StudyInstanceUID`)**, procesando múltiples adquisiciones y planos de Resonancia Magnética (MRI) en formato DICOM.

El código sigue una arquitectura modular en Python (`rsna_knee`), separando claramente datos, configuraciones, experimentos, notebooks y pruebas unitarias.

---

## 🌳 Árbol Completo de Archivos y Carpetas

```text
rsna-knee-abnormality/
├── .gitignore                     # Archivos y carpetas excluidos del control de versiones
├── requirements.txt               # Dependencias de Python del proyecto
├── setup.py                       # Instalador del paquete 'rsna_knee' en modo editable
├── README.md                      # Documentación general y setup del proyecto
├── CONTRIBUTING.md                # Guía de contribución y división de roles del equipo
├── AGENT_GUIDELINES.md            # Reglas operativas e invariantes médicas inviolables
├── AGENT_WORKFLOW.md              # Metodología de desarrollo y experimentación
├── Diccionario_RSNA_Knee.xlsx     # Diccionario de patologías y terminología médica
│
├── train.csv                      # Datos a nivel de estudio (Reportes y 12 labels)
├── train_series.csv               # Metadatos a nivel de serie para entrenamiento
├── test.csv                       # Lista de estudios de evaluación
├── test_series.csv                # Metadatos de series de evaluación
├── sample_submission.csv          # Formato esperado para la entrega en Kaggle
│
├── configs/                       # Configuraciones de experimentos (YAML)
│   └── baseline.yaml              # Configuración base del primer modelo de referencia
│
├── data/                          # Documentación y punto de anclaje de datos
│   └── README.md                  # Especificación de la estructura esperada en 'data/raw/'
│
├── experiments/                   # Registro y seguimiento de experimentos
│   └── README.md                  # Tabla comparativa de resultados y convención de carpetas
│
├── notebooks/                     # Exploración, análisis preliminar y prototipado
│   └── README.md                  # Plan de notebooks ordenados (01 a 05)
│
├── src/                           # Código fuente del paquete modular reutilizable
│   └── rsna_knee/
│       ├── __init__.py            # Inicializador del paquete 'rsna_knee'
│       ├── data/                  # Carga de datos, datasets y splits
│       │   ├── __init__.py
│       │   └── audit.py           # Módulo de auditoría de integridad de CSVs
│       ├── preprocessing/         # Pipeline de preprocesamiento y aumentaciones seguras
│       │   └── __init__.py
│       ├── models/                # Arquitecturas de red (Backbones, MIL, Multi-Arm)
│       │   └── __init__.py
│       ├── training/              # Loops de entrenamiento, funciones de pérdida y métricas
│       │   └── __init__.py
│       └── utils/                 # Utilidades comunes (seeds, configs, logging)
│           └── __init__.py
│
└── tests/                         # Suite de pruebas automatizadas con pytest
    ├── __init__.py
    ├── test_audit.py              # Tests unitarios para el módulo de auditoría 'audit.py'
    └── test_placeholder.py        # Test provisional de verificación del pipeline de testing
```

---

## 📂 Descripción Detallada por Carpeta

### 1. `configs/`
Almacena las configuraciones de los experimentos en formato YAML, permitiendo que el entrenamiento sea 100% reproducible sin alterar el código fuente.
* **`baseline.yaml`**: Archivo de configuración modelo para el primer benchmark. Define semillas deterministas (`seed: 42`), rutas a CSVs y carpetas DICOM, tamaño de imagen (`224x224`), arquitectura (`resnet18`), hiperparámetros de optimización (batch size, épocas, learning rate, AdamW) y estrategia de validación (`GroupKFold` agrupado por `StudyInstanceUID` en 5 splits).

### 2. `data/`
Carpeta destinada a la documentación de datos y el enlace con los archivos pesados descargados desde Kaggle.
* **`README.md`**: Explica cómo debe organizarse la carpeta `data/raw/` (que está en `.gitignore` para no subir los ~570 GB de DICOMs). Detalla la jerarquía `StudyInstanceUID → SeriesInstanceUID → SOPInstanceUID.dcm`, los formatos de compresión DICOM, la advertencia de `NaN != 0` y el comando oficial de descarga con la API de Kaggle.

### 3. `experiments/`
Espacio para llevar el control de versiones de los modelos entrenados y sus resultados.
* **`README.md`**: Define la convención de carpetas para cada corrida (`experiments/001_baseline/`, `experiments/002_2_5d/`, etc., conteniendo su `config.yaml`, `notes.md`, ignorando los pesos pesados) y mantiene una tabla comparativa con métricas de Validación Cruzada (CV) y puntajes en el Leaderboard público de Kaggle.

### 4. `notebooks/`
Contiene los cuadernos Jupyter dedicados a la exploración de datos (EDA), visualización y validación de hipótesis.
* **Política:** El código de producción reutilizable debe migrarse a `src/rsna_knee/` y no quedarse atrapado en notebooks.
* **`README.md`**: Define la hoja de ruta de los notebooks numerados:
  * `01_dataset_audit.ipynb`: Conteos, distribuciones y relaciones Estudio↔Serie.
  * `02_dicom_exploration.ipynb`: Inspección de tags DICOM, reconstrucción 3D y visualización.
  * `03_label_analysis.ipynb`: Estudio de los 58 casos Gold, correlación entre patologías y desbalance.
  * `04_report_analysis.ipynb`: Análisis de texto de los reportes médicos para pseudo-labeling.
  * `05_baseline.ipynb`: Primer modelo end-to-end de referencia.

### 5. `src/rsna_knee/`
Es el corazón del proyecto. Paquete de Python instalable y estructurado bajo buenas prácticas de ingeniería de software:
* **`__init__.py`**: Expone la versión del paquete y módulos principales.
* **`data/`**: Gestión de datos en memoria y disco.
  * `audit.py`: Script y módulo CLI que analiza y audita `train.csv` y `train_series.csv` sin decodificar imágenes DICOM, computando prevalencias, integridad referencial y distribuciones.
* **`preprocessing/`**: Transformaciones de imagen, normalización de ventanas Hounsfield/MRI, reordenamiento de cortes 3D por posición espacial y transformaciones seguras de aumento de datos.
* **`models/`**: Definición de arquitecturas de Deep Learning (Multiple Instance Learning - MIL, cabezales para predicción multi-etiqueta, integración multi-vista/multi-plano).
* **`training/`**: Scripts y clases para loops de entrenamiento, cálculo de pérdidas asimétricas o ponderadas, y computación de la métrica oficial: **Macro-Averaged ROC-AUC**.
* **`utils/`**: Helpers generales para fijar semillas deterministas, parseo de configuraciones YAML y validación de formato de archivos de submission.

### 6. `tests/`
Pruebas automatizadas ejecutables mediante `pytest` para garantizar que cambios futuros no rompan componentes críticos.
* **`test_audit.py`**: Pruebas unitarias completas para `src/rsna_knee/data/audit.py`, utilizando DataFrames sintéticos con casos borde (estudios con todas las etiquetas, casos con NaN parciales, duplicados, inconsistencias entre series y estudios).
* **`test_placeholder.py`**: Test inicial de humo para validar el correcto funcionamiento del comando `pytest` en el entorno.

---

## 📄 Descripción Detallada de Archivos en la Raíz

| Archivo | Rol y Contenido |
|---|---|
| **`train.csv`** | Conjunto de entrenamiento principal (4,407 filas). Cada fila es un estudio (`StudyInstanceUID`). Incluye el reporte radiológico en texto libre (`Report`) y 12 columnas binarias con las patologías de rodilla. **Nota clave:** Solo 58 estudios poseen etiquetas Gold; los otros 4,349 están en `NaN` (requieren pseudo-etiquetado vía NLP/LLM o semi-supervisión). |
| **`train_series.csv`** | Metadatos de las series de entrenamiento (24,371 filas). Relaciona cada `SeriesInstanceUID` con su `StudyInstanceUID` e indica el plano anatómico (`Sagittal`, `Coronal`, `Axial`), si es sensible a fluidos (`Fluid_Sensitive`) y si tiene supresión grasa (`Fat_Suppression`). |
| **`test.csv`** | Archivo con los `StudyInstanceUID` del conjunto de prueba. No contiene reportes ni etiquetas. |
| **`test_series.csv`** | Metadatos de las series del conjunto de prueba, con las mismas propiedades técnicas que `train_series.csv`. |
| **`sample_submission.csv`** | Plantilla de entrega con el formato exacto requerido por Kaggle: el identificador `StudyInstanceUID` seguido de las 12 probabilidades predichas (valores continuos de `0.0` a `1.0`). |
| **`README.md`** | Presentación principal del repositorio: descripción de la competencia, objetivos, datos clave, filosofía de desarrollo y pasos de instalación. |
| **`AGENT_GUIDELINES.md`** | Manual de directrices obligatorias e invariantes médicas. Establece reglas inviolables (ej. prohibición de volteo horizontal sin invertir etiquetas Medial↔Lateral, tratamiento estricto de `NaN != 0`, ordenamiento espacial obligatorio de cortes DICOM). |
| **`AGENT_WORKFLOW.md`** | Protocolo de trabajo para ingeniería de Machine Learning: priorización (Corrección → Reproducibilidad → Validación → Métrica → Velocidad → Complejidad) y listas de verificación antes de tocar código. |
| **`CONTRIBUTING.md`** | Reglas de colaboración en equipo: flujo de ramas Git (`feature/...` hacia `main`), políticas de Pull Requests y división de responsabilidades en 4 roles (Data Engineering, DICOM/MRI, Labels/NLP, ML/Modelado). |
| **`Diccionario_RSNA_Knee.xlsx`** | Hoja de cálculo con el vocabulario médico y definiciones clínicas de las 12 patologías evaluadas en la articulación de la rodilla. |
| **`requirements.txt`** | Lista de librerías necesarias agrupadas por función: Core (`numpy`, `pandas`, `scikit-learn`), Imagen/DICOM (`pydicom`, `SimpleITK`, `opencv-python`, `Pillow`), Deep Learning (`torch`, `torchvision`, `timm`), NLP (`langdetect`), Tracking (`pyyaml`, `tqdm`) y Testing (`pytest`). |
| **`setup.py`** | Script de instalación de setuptools que configura `rsna_knee` como un paquete local editable (`pip install -e .`), permitiendo importar sus módulos desde cualquier lugar del entorno. |
| **`.gitignore`** | Reglas para ignorar datos masivos (`data/raw/`), entornos virtuales (`.venv/`), caches de Python (`__pycache__/`), archivos de checkpoints/pesos (`*.pt`, `*.pth`) y credenciales sensibles (`kaggle.json`). |

---

## ⚠️ Reglas y Principios Clave a Recordar

1. **La unidad de predicción es el estudio (`StudyInstanceUID`)**: Un paciente tiene múltiples series de imágenes en distintos planos; la predicción final se hace sobre todo el conjunto, no sobre cortes aislados.
2. **`Report` no existe en test**: El texto del informe médico solo puede usarse durante la fase de desarrollo/entrenamiento para asistir en la generación de pseudo-etiquetas, nunca como entrada del modelo final.
3. **Invariante Medial/Lateral**: Si se aplica Data Augmentation con espejo horizontal, las etiquetas `Medial Meniscus` y `Lateral Meniscus`, así como `Medial OA` y `Lateral OA`, deben intercambiarse obligatoriamente para preservar la coherencia anatómica.

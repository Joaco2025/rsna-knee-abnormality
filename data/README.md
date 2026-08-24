# Datos

Los datos de la competencia **no se suben al repositorio** (569.76 GB,
819,640 archivos DICOM). Esta carpeta solo documenta la estructura esperada.

## Estructura esperada en `data/raw/`

```
data/raw/
├── train_series/
│   └── StudyInstanceUID/
│       └── SeriesInstanceUID/
│           └── SOPInstanceUID.dcm
├── test_series/
│   └── StudyInstanceUID/
│       └── SeriesInstanceUID/
│           └── SOPInstanceUID.dcm
├── train.csv
├── train_series.csv
├── test.csv
├── test_series.csv
└── sample_submission.csv
```

## Descripción de archivos

### `train.csv` (4,407 filas = 4,407 estudios)

| Columna | Descripción |
|---|---|
| `StudyInstanceUID` | ID del estudio completo (una rodilla) |
| `Report` | Reporte radiológico original. Multilingüe (español, inglés, alemán, etc.). **No disponible en test.** |
| 12 columnas de labels | `ACL`, `MCL`, `Medial Meniscus`, `Lateral Meniscus`, `Medial OA`, `Lateral OA`, `PF OA`, `Effusion`, `Synovitis`, `Baker's`, `Contusion`, `Fracture` — binarias 0/1, **NaN si no hay label** (NaN ≠ negativo) |

⚠️ Solo **58 de 4,407 estudios** tienen las 12 labels completas (ground truth
de 2 radiólogos musculoesqueléticos + adjudicación de un tercero). Los otros
4,349 tienen las 12 columnas en NaN — no deben tratarse como 0.

### `train_series.csv` (24,371 filas = 24,371 series)

| Columna | Descripción |
|---|---|
| `StudyInstanceUID` | FK al estudio |
| `SeriesInstanceUID` | ID de la serie (una adquisición MRI) |
| `Fluid_Sensitive` | 1 = secuencia enfatiza señal de líquido (T2, PD, STIR, similares) |
| `Fat_Suppression` | 1 = aplica supresión de grasa. Correlacionado con `Fluid_Sensitive` pero **no equivalente** — no usar uno como sustituto del otro |
| `Anatomical_Plane` | `Sagittal` / `Coronal` / `Axial` |

Distribución de planos (train): Sagittal 9,864 · Coronal 8,609 · Axial 5,898.
Promedio de ~5.5 series por estudio (min 3, max 14).

### `test.csv` / `test_series.csv`

Mismo esquema, sin `Report` ni labels. El archivo visible contiene solo
estudios de ejemplo; en scoring se sustituye por el test real (~1,300 estudios).

### `sample_submission.csv`

Formato esperado de entrega: `StudyInstanceUID` + las 12 columnas de labels,
como probabilidades (no binario).

## Jerarquía DICOM

```
StudyInstanceUID
    └── SeriesInstanceUID (una adquisición: plano + secuencia)
            └── SOPInstanceUID.dcm (un slice)
```

- Una serie típica tiene 20–45 slices (mediana ~30), con cola de series de
  varios cientos de slices.
- Metadata reducida a 86 tags DICOM permitidos.
- Transfer syntaxes variados: Explicit VR Little Endian, JPEG Lossless,
  JPEG 2000, Implicit VR Little Endian.
- Resolución, spacing, orientación e intensidades **varían** entre series y
  estudios — no asumir uniformidad.

## Reglas importantes

- ❌ No tratar `NaN` en labels como `0`.
- ❌ No entrenar a nivel de slice individual — la label es del estudio completo.
- ❌ No usar `Report` como input del modelo final (no existe en test). Puede
  usarse solo para investigar derivación de pseudo-labels en entrenamiento.
- ❌ No convertir los 570 GB a PNG de forma indiscriminada — leer DICOM bajo
  demanda con `pydicom` (`stop_before_pixels=True` para solo metadata).
- ❌ No asumir resolución/orientación uniforme entre estudios.
- ❌ No usar `Fluid_Sensitive` y `Fat_Suppression` como intercambiables.

## Descarga

```bash
kaggle competitions download -c rsna-knee-abnormality-detection -p data/raw/
```

(Requiere `kaggle.json` configurado — nunca subir ese archivo al repo.)

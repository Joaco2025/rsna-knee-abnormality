# Experimentos

Cada experimento con entrenamiento real vive en su propia carpeta
`NNN_nombre_descriptivo/` (config usada, notas, checkpoints y logs — estos
últimos ignorados por git).

## Tabla de resultados

| ID | Modelo | Input | CV | Kaggle (público) | Notas |
|----|--------|-------|----|--------------------|-------|
| 001 | — | — | — | — | Baseline pendiente |

Actualizar esta tabla en cada PR que agregue un experimento nuevo, para no
perder de vista qué configuración dio el mejor resultado.

## Convención de carpetas

```
experiments/
├── 001_baseline/
│   ├── config.yaml
│   ├── notes.md
│   └── (logs/ y checkpoints/ ignorados por git)
├── 002_2_5d/
└── ...
```

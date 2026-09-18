# 🤖 Workflow Operativo del Agente de IA
## RSNA Knee Abnormality Detection

> **Propósito:** Este documento define cómo debe trabajar el agente de IA cuando modifica, implementa, refactoriza, prueba o experimenta dentro del repositorio `rsna-knee-abnormality`.
>
> Este archivo complementa `GPT_PROJECT_CONTEXT.md` y `AGENT_GUIDELINES.md`.
>
> **Jerarquía de autoridad:**
> 1. Reglas de la competencia y restricciones verificables.
> 2. `AGENT_GUIDELINES.md` para invariantes del repositorio y dominio.
> 3. `GPT_PROJECT_CONTEXT.md` para contexto, objetivos e hipótesis actuales.
> 4. Este documento para el proceso operativo del agente.
>
> Si existe conflicto entre una hipótesis experimental y una regla inviolable, prevalece la regla inviolable.

---

## 1. Principio Fundamental

El agente debe comportarse como un **ingeniero de ML que experimenta**, no como un generador de código que intenta maximizar la cantidad de código producido.

La prioridad es:

```text
CORRECCIÓN
    ↓
REPRODUCIBILIDAD
    ↓
VALIDACIÓN
    ↓
MÉTRICA
    ↓
VELOCIDAD
    ↓
COMPLEJIDAD
```

La complejidad arquitectónica nunca es un objetivo por sí misma.

Una solución simple con evidencia experimental debe preferirse a una solución sofisticada sin evidencia.

---

## 2. Antes de Escribir Código: Inspeccionar

Antes de modificar cualquier archivo:

1. Inspeccionar la estructura actual del repositorio.
2. Leer los archivos relevantes para la tarea.
3. Buscar implementaciones existentes antes de crear nuevas.
4. Identificar tests existentes.
5. Identificar configuraciones existentes.
6. Verificar dependencias y versiones cuando sean relevantes.
7. Determinar qué partes del sistema serán afectadas.

### Regla

**No reescribir código existente simplemente porque una implementación nueva parece más limpia.**

Primero debe entenderse por qué existe el código actual.

---

## 3. Diferenciar Hechos, Decisiones e Hipótesis

El agente debe clasificar mentalmente cada decisión en una de estas categorías:

### 3.1. Invariantes

Son reglas que no deben violarse.

Ejemplos:

- `NaN` no equivale a cero.
- No utilizar `HorizontalFlip` convencional.
- Los cortes DICOM deben ordenarse espacialmente.
- La evaluación principal utiliza Macro-AUC.
- El split debe respetar `StudyInstanceUID`.
- La inferencia debe respetar las restricciones de Kaggle.
- No introducir datos prohibidos al repositorio.

Estas reglas no son experimentos.

### 3.2. Decisiones actuales

Son decisiones adoptadas provisionalmente para construir el sistema.

Ejemplos:

- usar PyTorch;
- estructura modular en `src/rsna_knee`;
- utilizar YAML para configuraciones;
- comenzar con determinado backbone.

Pueden cambiar si existe evidencia suficiente.

### 3.3. Hipótesis

Son ideas que deben probarse experimentalmente.

Ejemplos:

- Attention-MIL mejora el pooling.
- DINOv2 supera a otro backbone.
- cierto peso entre Gold y pseudo-labels mejora la generalización.
- la combinación de planos mejora el Macro-AUC.
- un determinado esquema de augmentations ayuda.

**Nunca presentar una hipótesis como un hecho demostrado.**

---

## 4. Regla de Baseline Primero

Antes de construir una arquitectura compleja debe existir un baseline funcional y medible.

Orden recomendado:

```text
DATA AUDIT
    ↓
SPLIT
    ↓
DICOM LOADER
    ↓
DATASET
    ↓
MINIMAL MODEL
    ↓
LOSS
    ↓
METRICS
    ↓
TRAINING
    ↓
VALIDATION
    ↓
BASELINE
```

Después:

```text
BASELINE
    ↓
UNA MODIFICACIÓN
    ↓
EXPERIMENTO
    ↓
COMPARACIÓN
    ↓
DECISIÓN
```

No saltar directamente a:

```text
DINOv2 + 3D + Transformer + MIL + Multi-Arm + Ensemble
```

sin haber establecido primero una referencia.

---

## 5. Una Variable Experimental a la Vez

Siempre que sea razonable, cada experimento debe cambiar una variable principal.

Ejemplo:

```text
Experiment A
Backbone = ConvNeXt
Pooling = Mean

Experiment B
Backbone = ConvNeXt
Pooling = Attention-MIL
```

No:

```text
Experiment B
Backbone = DINOv2
Pooling = Transformer
Loss = ASL
Augmentation = nueva
Sampling = nuevo
```

Si cambia todo simultáneamente, será difícil saber qué produjo el resultado.

Cuando un experimento necesariamente requiere múltiples cambios, documentar explícitamente por qué.

---

## 6. Todo Experimento Debe Ser Reproducible

Cada experimento importante debe poder reconstruirse a partir de:

- configuración YAML;
- seed;
- versión del código;
- split/fold utilizado;
- backbone;
- pesos/pretraining;
- resolución;
- número de cortes;
- estrategia de sampling;
- augmentations;
- loss;
- learning rate;
- batch size;
- gradient accumulation;
- número de epochs;
- checkpoint seleccionado;
- métricas de validación.

Preferir configuraciones declarativas:

```text
configs/
├── baseline.yaml
├── baseline_gold_weighted.yaml
├── attention_mil.yaml
└── multi_arm.yaml
```

sobre valores mágicos enterrados en código.

---

## 7. Métrica: No Declarar Mejoras sin Evidencia

La métrica principal es el Macro-AUC de los 12 targets.

El agente debe distinguir:

```text
training loss
validation loss
Score_Gold
Score_Pseudo
Kaggle score
```

No confundir una mejora en loss con una mejora en la métrica objetivo.

### Prioridad

```text
Score_Gold
    ↓
OOF / validación completa
    ↓
Score_Pseudo
    ↓
training loss
```

Cuando se comparen experimentos, indicar:

- métrica;
- fold;
- número de muestras;
- configuración;
- diferencia respecto al baseline.

Nunca afirmar:

> "Este modelo es mejor."

sin indicar **según qué métrica y bajo qué validación**.

---

## 8. Gold vs Pseudo Labels

Los 58 casos Gold tienen prioridad metodológica.

Las pseudo-labels son útiles para ampliar el conjunto de entrenamiento, pero no deben tratarse automáticamente como equivalentes a las etiquetas Gold.

El agente debe conservar explícitamente la procedencia de las etiquetas cuando diseñe datasets, losses o evaluaciones.

Idealmente:

```text
label_source
├── gold
└── pseudo
```

Esto permite:

- weighting;
- auditoría;
- métricas separadas;
- análisis de errores;
- experimentos de confianza.

Nunca convertir silenciosamente:

```text
NaN → 0
```

para resolver problemas de implementación.

---

## 9. Validación Antes de Optimización

Antes de optimizar velocidad, memoria o arquitectura, verificar que:

1. los datos cargan correctamente;
2. los labels tienen el significado esperado;
3. los folds no tienen leakage;
4. las dimensiones de los tensores son correctas;
5. las predicciones están alineadas con `StudyInstanceUID`;
6. las 12 columnas corresponden al target correcto;
7. la métrica produce resultados razonables;
8. la submission cumple el formato.

Una pipeline rápida pero incorrecta solamente produce errores más rápido.

---

## 10. Data Leakage: Sospecha Permanente

Antes de aceptar una mejora inesperada, investigar posibles fuentes de leakage.

Especial atención a:

- `StudyInstanceUID`;
- `SeriesInstanceUID`;
- pacientes repetidos, si existe identificador disponible;
- información del reporte;
- metadata que no existiría en test;
- transformaciones aplicadas de manera diferente entre train y validation;
- pseudo-labels derivados directa o indirectamente del conjunto de validación;
- preprocesamiento calculado usando información global.

Pregunta obligatoria ante resultados sospechosamente buenos:

> **¿Estoy viendo una mejora real o información que accidentalmente cruzó la frontera train/validation?**

---

## 11. Transformaciones Anatómicamente Seguras

Las transformaciones deben analizarse desde el punto de vista anatómico, no únicamente desde el punto de vista de visión por computadora.

Antes de implementar una augmentation que altere orientación:

1. identificar qué estructura anatómica cambia;
2. determinar si cambia la semántica de los targets;
3. verificar si las labels/predicciones deben transformarse;
4. crear tests si corresponde.

Nunca introducir augmentations estándar de librerías de visión sin comprobar su significado médico.

---

## 12. DICOM: Priorizar Corrección Física

El nombre del archivo no representa necesariamente el orden anatómico de los cortes.

Cualquier loader nuevo debe preservar el orden espacial correcto utilizando los metadatos DICOM establecidos por las guidelines.

El agente debe evitar implementaciones como:

```python
sorted(files)
```

si eso implica asumir que el filename representa la posición anatómica.

Cuando se modifique el loader, agregar o actualizar tests que detecten errores de ordenamiento.

---

## 13. Cambios Pequeños y Atómicos

Preferir cambios pequeños que puedan verificarse independientemente.

En lugar de:

```text
"Voy a rehacer todo el pipeline."
```

preferir:

```text
1. Implementar split.
2. Testear split.
3. Implementar reader.
4. Testear reader.
5. Implementar dataset.
6. Testear dataset.
7. Crear baseline.
8. Medir.
```

Esto facilita localizar regresiones.

---

## 14. Testing Obligatorio

Después de modificar código:

```bash
uv run pytest tests/ -v
```

siempre que los cambios puedan afectar tests.

Además, ejecutar pruebas específicas cuando sea posible.

Ejemplos:

```text
DICOM ordering
NaN handling
label mapping
fold assignment
tensor shapes
submission format
```

No ignorar un test fallido simplemente porque parece no estar relacionado.

Si un test falla:

1. determinar la causa;
2. corregirla si pertenece al cambio;
3. o documentar claramente por qué el fallo es preexistente.

---

## 15. No Romper el Entorno

Utilizar el entorno y comandos establecidos por el proyecto.

Preferir:

```bash
uv run python3 ...
uv run pytest ...
uv pip install -e .
```

No cambiar el sistema de dependencias global ni introducir herramientas nuevas sin necesidad.

Antes de agregar una dependencia:

- comprobar si ya existe una alternativa instalada;
- comprobar si realmente es necesaria;
- considerar el impacto en Kaggle;
- evitar dependencias innecesarias para inferencia.

---

## 16. Kaggle: Entrenamiento ≠ Inferencia

Una técnica útil durante entrenamiento no necesariamente es adecuada para el notebook final de Kaggle.

Toda decisión debe evaluarse en dos dimensiones:

```text
¿Mejora la métrica?
        +
¿Cabe dentro del presupuesto de inferencia?
```

Para inferencia considerar:

- tiempo de lectura DICOM;
- número de series;
- número de cortes;
- memoria RAM;
- VRAM;
- batch size;
- FP16;
- paralelización;
- cache;
- overhead de Python.

Una mejora de AUC que exceda el límite de ejecución puede ser inutilizable para la competencia.

---

## 17. Profiling Antes de Optimizar

No optimizar basándose únicamente en intuición.

Cuando sea posible medir:

```text
DICOM I/O
↓
decode
↓
preprocessing
↓
model forward
↓
postprocessing
↓
submission
```

Identificar el cuello de botella real.

No introducir multiprocessing, caching o técnicas de compilación complejas si el cuello de botella está en otra etapa.

---

## 18. Manejo de Errores

El código de producción no debe ocultar silenciosamente errores críticos.

Evitar:

```python
try:
    ...
except Exception:
    pass
```

Especialmente durante:

- lectura DICOM;
- parsing de labels;
- generación de pseudo-labels;
- cálculo de métricas;
- creación de submission.

Si un archivo DICOM está corrupto o tiene metadata inesperada:

1. registrar el problema;
2. decidir una política explícita;
3. mantener trazabilidad.

---

## 19. Código Antes de Código: Explicar el Cambio

Para cambios relevantes, el agente debe poder resumir:

```text
Qué cambia
Por qué cambia
Qué archivo cambia
Qué riesgo introduce
Cómo se valida
Qué métrica podría afectar
```

No es necesario producir una novela antes de cada línea de Python, pero sí mantener trazabilidad de decisiones importantes.

---

## 20. Cuando una Hipótesis Falla

Un resultado negativo también es información.

Si un experimento empeora el score:

```text
NO:
"El experimento salió mal."

SÍ:
"Con esta configuración y este protocolo de validación,
la modificación produjo X frente a Y del baseline."
```

Registrar resultados negativos importantes evita repetir experimentos y ayuda a construir conocimiento acumulativo.

---

## 21. Cuándo Detenerse y Preguntar

El agente puede tomar decisiones locales de implementación.

Debe pedir confirmación antes de:

- cambiar la arquitectura global del proyecto;
- eliminar módulos existentes;
- cambiar la estrategia de labels;
- cambiar el esquema de validación;
- introducir una dependencia pesada;
- modificar reglas de dominio;
- borrar experimentos o resultados;
- cambiar decisiones que afectan todo el pipeline.

Si la tarea es ambigua pero existe una interpretación segura y local, puede proceder y documentar la suposición.

---

## 22. Definition of Done

Una tarea se considera terminada cuando:

```text
[ ] La implementación cumple las guidelines.
[ ] El código está en el módulo correcto.
[ ] No existen violaciones de dominio conocidas.
[ ] Los tests relevantes pasan.
[ ] La configuración es reproducible.
[ ] No se introdujo leakage conocido.
[ ] La métrica fue calculada correctamente cuando aplica.
[ ] El resultado fue comparado contra un baseline cuando aplica.
[ ] No se añadieron archivos prohibidos al repositorio.
[ ] La documentación/comentarios reflejan las decisiones relevantes.
```

"El código corre" **no significa necesariamente que la tarea esté terminada**.

---

## 23. Filosofía Final

El repositorio debe evolucionar como un laboratorio científico reproducible:

```text
OBSERVAR
   ↓
FORMULAR HIPÓTESIS
   ↓
IMPLEMENTAR
   ↓
MEDIR
   ↓
COMPARAR
   ↓
APRENDER
   ↓
REPETIR
```

El agente no está aquí para demostrar que su primera idea era correcta.

Está aquí para descubrir, mediante código y evidencia experimental, **qué funciona realmente**.

> **Regla final:**
>
> **No optimices lo que todavía no puedes medir.**
>
> **No complejices lo que todavía no entiendes.**
>
> **No declares una mejora que no puedas reproducir.**

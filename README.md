# 🦴 RSNA Knee Abnormality Detection

Team repository for the **RSNA Knee Abnormality Detection** competition (Kaggle), organized by the Radiological Society of North America.

## Objective

Build a model that, given a complete knee MRI study (`StudyInstanceUID`, composed of multiple series across different planes and sequences), predicts the probability of 12 abnormalities:

`ACL`, `MCL`, `Medial Meniscus`, `Lateral Meniscus`, `Medial OA`, `Lateral OA`,

`PF OA`, `Effusion`, `Synovitis`, `Baker's`, `Contusion`, `Fracture`.

The prediction unit is the **complete study**, not the individual slice.

## Key Dataset Facts

* ~569.76 GB, 819,640 DICOM files.

* Hierarchy: `StudyInstanceUID → SeriesInstanceUID → SOPInstanceUID.dcm`.

* 4,407 studies in train, but **only 58 have all 12 labels available**.

* `Report` (the original radiology report) is available in train but **will not be available in test**. It cannot be used as an input to the final model.

* Series include `Sagittal`, `Coronal`, and `Axial` planes, as well as `Fluid_Sensitive` / `Fat_Suppression` flags.

See `data/README.md` for the complete data structure and the rules we must follow.

## Repository Structure

```text
rsna-knee-abnormality/
│
├── README.md
├── AGENT_GUIDELINES.md
├── AGENT_WORKFLOW.md
├── ESTRUCTURA_PROYECTO.md
│
├── train.csv
├── train_series.csv
├── test.csv
├── test_series.csv
├── sample_submission.csv
│
├── Diccionario_RSNA_Knee.xlsx
│
├── configs/
│   └── baseline.yaml
│
├── data/
│   └── README.md          # data documentation (data is NOT stored in git)
│
├── notebooks/             # exploration, analysis, and experiments
│   └── README.md
│
├── src/rsna_knee/         # reusable, validated package modules
│   └── data/              # dataset audit and validation
│       └── audit.py
│
└── tests/                 # automated unit tests
    └── test_audit.py
```

## Setup

```bash
git clone <repo-url>
cd rsna-knee-abnormality
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the data downloaded from Kaggle in `data/raw/` following the structure described in `data/README.md` (data is not uploaded to git).

## Philosophy

The project follows a notebook-driven research workflow: notebooks serve as the primary environment for data exploration, MRI visualization, hypothesis testing, and model experimentation.

Reusable Python modules in `src/rsna_knee/` are introduced only when a piece of logic has been thoroughly explored, validated, and there is a clear justification to reuse it in the pipeline.

```text
Dataset → Validation → Baseline → Experiment → Analysis → Improvement → Kaggle
```

With only 58 studies currently known to have all 12 labels available, validation design is just as important as the model itself.

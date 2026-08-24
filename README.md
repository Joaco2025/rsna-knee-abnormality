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
├── .gitignore
├── requirements.txt
│
├── data/
│   └── README.md          # data documentation (data is NOT stored in git)
│
├── notebooks/             # exploration and analysis
│
├── src/rsna_knee/         # reusable pipeline code
│   ├── data/              # loaders, dataset, splits
│   ├── preprocessing/     # intensity, orientation, transforms
│   ├── models/            # baseline, vision, multimodal
│   ├── training/          # train, evaluate, losses
│   └── utils/             # config, logging, seed
│
├── configs/               # experiment configuration (yaml)
├── experiments/           # experiment tracking and results
└── tests/                 # loader/dataset/preprocessing tests
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

## Workflow

Each team member works on their own `feature/...` branch and opens PRs into `main`.

See `CONTRIBUTING.md` (or the corresponding section) for the team's division of responsibilities.

## Philosophy

We are not trying to build the most complex model possible from day one. The order is:

```text
Dataset → Validation → Baseline → Experiment → Analysis → Improvement → Kaggle
```

With only 58 studies currently known to have all 12 labels available, validation design is just as important as the model itself.

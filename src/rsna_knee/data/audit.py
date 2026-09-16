"""Dataset audit module for RSNA Knee Abnormality Detection.

This module inspects the dataset CSVs (train.csv and train_series.csv)
to verify data integrity, label distributions, series characteristics,
and referential consistency, without decoding or loading DICOM images into memory.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

# The 12 official competition pathologies
GOLD_LABEL_COLUMNS = [
    "ACL",
    "MCL",
    "Medial Meniscus",
    "Lateral Meniscus",
    "Medial OA",
    "Lateral OA",
    "PF OA",
    "Effusion",
    "Synovitis",
    "Baker's",
    "Contusion",
    "Fracture",
]


@dataclass
class DatasetAuditReport:
    """Structured report containing audit metrics for train and train_series datasets."""

    # Studies / train.csv overview
    num_train_studies: int
    num_unique_train_studies: int
    num_train_duplicate_studies: int
    missing_reports_count: int

    # Label integrity (Gold vs NaN)
    num_gold_studies: int
    num_all_nan_studies: int
    num_partial_nan_studies: int
    gold_positive_counts: dict[str, int]
    gold_prevalence: dict[str, float]

    # Series / train_series.csv overview
    num_series_rows: int
    num_unique_series: int
    num_series_duplicate_uids: int
    num_unique_studies_in_series: int

    # Series distributions
    plane_distribution: dict[str, int]
    fluid_sensitive_distribution: dict[int, int]
    fat_suppression_distribution: dict[int, int]

    # Sequence alignment finding
    fluid_fat_identical: bool
    fluid_fat_mismatches: int

    # Series per study metrics
    series_per_study_stats: dict[str, float]
    studies_with_all_three_planes: int
    plane_coverage_counts: dict[str, int]

    # Referential integrity between train and series
    studies_in_train_not_in_series: int
    studies_in_series_not_in_train: int
    referential_integrity_ok: bool

    # Metadata & paths
    train_csv_path: str | None = None
    train_series_csv_path: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the report to a standard dictionary."""
        return asdict(self)

    def format_summary(self) -> str:
        """Format the report into a human-readable text summary."""
        lines = [
            "=" * 70,
            "RSNA KNEE ABNORMALITY DETECTION - DATASET AUDIT REPORT",
            "=" * 70,
            f"Train CSV:        {self.train_csv_path or 'In-memory DataFrame'}",
            f"Train Series CSV: {self.train_series_csv_path or 'In-memory DataFrame'}",
            "",
            "1. ESTUDIOS EN TRAIN (train.csv)",
            f"   - Total registros:              {self.num_train_studies}",
            f"   - Estudios únicos:              {self.num_unique_train_studies}",
            f"   - Duplicados en StudyInstanceUID: {self.num_train_duplicate_studies}",
            f"   - Reportes faltantes (NaN):     {self.missing_reports_count}",
            "",
            "2. INTEGRIDAD DE ETIQUETAS (12 Patologías)",
            f"   - Estudios con 12 Gold labels:  {self.num_gold_studies}",
            f"   - Estudios con 12 NaN (todos):  {self.num_all_nan_studies}",
            f"   - Estudios con NaN parcial:     {self.num_partial_nan_studies}",
            "",
            "   Prevalencia en casos Gold (n=58):",
        ]

        for label in GOLD_LABEL_COLUMNS:
            pos = self.gold_positive_counts.get(label, 0)
            prev = self.gold_prevalence.get(label, 0.0) * 100
            lines.append(f"     * {label:<18}: {pos:>2}/58 ({prev:>5.1f}%)")

        lines.extend(
            [
                "",
                "3. SERIES EN TRAIN (train_series.csv)",
                f"   - Total registros de series:    {self.num_series_rows}",
                f"   - Series únicas (SeriesInstanceUID): {self.num_unique_series}",
                f"   - Duplicados en SeriesInstanceUID:   {self.num_series_duplicate_uids}",
                f"   - Estudios en train_series:     {self.num_unique_studies_in_series}",
                "",
                "   Distribución de Anatomical_Plane:",
            ]
        )

        for plane, count in self.plane_distribution.items():
            pct = (count / self.num_series_rows * 100) if self.num_series_rows else 0.0
            lines.append(f"     * {plane:<12}: {count:>6} ({pct:>5.1f}%)")

        lines.extend(
            [
                "",
                "   Distribución de Fluid_Sensitive:",
            ]
        )
        for val, count in self.fluid_sensitive_distribution.items():
            pct = (count / self.num_series_rows * 100) if self.num_series_rows else 0.0
            lines.append(f"     * Valor {val}: {count:>6} ({pct:>5.1f}%)")

        lines.extend(
            [
                "",
                "   Distribución de Fat_Suppression:",
            ]
        )
        for val, count in self.fat_suppression_distribution.items():
            pct = (count / self.num_series_rows * 100) if self.num_series_rows else 0.0
            lines.append(f"     * Valor {val}: {count:>6} ({pct:>5.1f}%)")

        lines.extend(
            [
                "",
                "   Hallazgo Fluid_Sensitive vs Fat_Suppression:",
                f"     * Valores 100% idénticos en todas las filas: {self.fluid_fat_identical}",
                f"     * Número de discrepancias:                   {self.fluid_fat_mismatches}",
                "",
                "4. SERIES POR ESTUDIO",
                f"   - Min:    {self.series_per_study_stats.get('min', 0):.0f}",
                f"   - 25%:    {self.series_per_study_stats.get('25%', 0):.1f}",
                f"   - Mediana:{self.series_per_study_stats.get('50%', 0):.1f}",
                f"   - Media:  {self.series_per_study_stats.get('mean', 0):.2f}",
                f"   - 75%:    {self.series_per_study_stats.get('75%', 0):.1f}",
                f"   - Max:    {self.series_per_study_stats.get('max', 0):.0f}",
                f"   - Estudios con los 3 planos (Axial, Coronal, Sagittal): "
                f"{self.studies_with_all_three_planes}/{self.num_unique_studies_in_series}",
                "",
                "5. INTEGRIDAD REFERENCIAL (train.csv vs train_series.csv)",
                f"   - Estudios en train pero ausentes en series:  {self.studies_in_train_not_in_series}",
                f"   - Estudios en series pero ausentes en train:  {self.studies_in_series_not_in_train}",
                f"   - Integridad referencial perfecta:            {self.referential_integrity_ok}",
                "=" * 70,
            ]
        )

        return "\n".join(lines)


def resolve_default_path(filename: str) -> Path | None:
    """Find a dataset file by checking common locations."""
    candidates = [
        Path(filename),
        Path("data/raw") / filename,
        Path("data") / filename,
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def audit_dataset(
    train_csv: str | Path | pd.DataFrame | None = None,
    train_series_csv: str | Path | pd.DataFrame | None = None,
    label_columns: list[str] | None = None,
) -> DatasetAuditReport:
    """Perform a comprehensive audit of the dataset CSVs.

    Args:
        train_csv: Path to train.csv or a pre-loaded DataFrame.
        train_series_csv: Path to train_series.csv or a pre-loaded DataFrame.
        label_columns: List of 12 target column names. Defaults to GOLD_LABEL_COLUMNS.

    Returns:
        DatasetAuditReport containing structured metrics and findings.
    """
    labels = label_columns or GOLD_LABEL_COLUMNS

    # Resolve train_csv
    train_path_str: str | None = None
    if isinstance(train_csv, pd.DataFrame):
        df_train = train_csv.copy()
    else:
        if train_csv is None:
            resolved = resolve_default_path("train.csv")
            if resolved is None:
                raise FileNotFoundError("Could not locate train.csv in root or data/ directories.")
            train_path = resolved
        else:
            train_path = Path(train_csv)
            if not train_path.is_file():
                raise FileNotFoundError(f"train_csv not found at: {train_path}")

        train_path_str = str(train_path)
        df_train = pd.read_csv(train_path)

    # Resolve train_series_csv
    series_path_str: str | None = None
    if isinstance(train_series_csv, pd.DataFrame):
        df_series = train_series_csv.copy()
    else:
        if train_series_csv is None:
            resolved = resolve_default_path("train_series.csv")
            if resolved is None:
                raise FileNotFoundError(
                    "Could not locate train_series.csv in root or data/ directories."
                )
            series_path = resolved
        else:
            series_path = Path(train_series_csv)
            if not series_path.is_file():
                raise FileNotFoundError(f"train_series_csv not found at: {series_path}")

        series_path_str = str(series_path)
        df_series = pd.read_csv(series_path)

    # 1. Audit train.csv
    num_train_studies = len(df_train)
    num_unique_train_studies = int(df_train["StudyInstanceUID"].nunique())
    num_train_duplicate_studies = int(df_train["StudyInstanceUID"].duplicated().sum())
    missing_reports_count = (
        int(df_train["Report"].isna().sum()) if "Report" in df_train.columns else 0
    )

    # 2. Label audit
    available_labels = [col for col in labels if col in df_train.columns]
    if len(available_labels) != len(labels):
        missing_cols = set(labels) - set(available_labels)
        raise ValueError(f"Target label columns missing from train.csv: {missing_cols}")

    gold_mask = df_train[available_labels].notna().all(axis=1)
    all_nan_mask = df_train[available_labels].isna().all(axis=1)
    partial_nan_mask = (~gold_mask) & (~all_nan_mask)

    num_gold_studies = int(gold_mask.sum())
    num_all_nan_studies = int(all_nan_mask.sum())
    num_partial_nan_studies = int(partial_nan_mask.sum())

    df_gold = df_train[gold_mask]
    gold_positive_counts: dict[str, int] = {}
    gold_prevalence: dict[str, float] = {}

    for col in available_labels:
        pos = int((df_gold[col] == 1).sum())
        gold_positive_counts[col] = pos
        gold_prevalence[col] = (pos / num_gold_studies) if num_gold_studies > 0 else 0.0

    # 3. Audit train_series.csv
    num_series_rows = len(df_series)
    num_unique_series = int(df_series["SeriesInstanceUID"].nunique())
    num_series_duplicate_uids = int(df_series["SeriesInstanceUID"].duplicated().sum())
    num_unique_studies_in_series = int(df_series["StudyInstanceUID"].nunique())

    plane_dist = df_series["Anatomical_Plane"].value_counts(dropna=False).to_dict()
    fluid_dist = df_series["Fluid_Sensitive"].value_counts(dropna=False).to_dict()
    fat_dist = df_series["Fat_Suppression"].value_counts(dropna=False).to_dict()

    # Fluid_Sensitive vs Fat_Suppression comparison
    fluid_fat_identical = bool(
        (df_series["Fluid_Sensitive"] == df_series["Fat_Suppression"]).all()
    )
    fluid_fat_mismatches = int(
        (df_series["Fluid_Sensitive"] != df_series["Fat_Suppression"]).sum()
    )

    # 4. Series per study metrics
    series_per_study = df_series.groupby("StudyInstanceUID").size()
    desc = series_per_study.describe()
    series_stats = {
        "min": float(desc.get("min", 0.0)),
        "25%": float(desc.get("25%", 0.0)),
        "50%": float(desc.get("50%", 0.0)),
        "mean": float(desc.get("mean", 0.0)),
        "75%": float(desc.get("75%", 0.0)),
        "max": float(desc.get("max", 0.0)),
        "std": float(desc.get("std", 0.0)),
    }

    # Anatomical planes per study
    plane_types_per_study = (
        df_series.groupby("StudyInstanceUID")["Anatomical_Plane"]
        .agg(lambda s: tuple(sorted(set(s.dropna()))))
    )
    plane_coverage_counts = {
        "/".join(k): int(v) for k, v in plane_types_per_study.value_counts().items()
    }

    tri_plane_tuple = ("Axial", "Coronal", "Sagittal")
    studies_with_all_three = int(
        (plane_types_per_study == tri_plane_tuple).sum()
    )

    # 5. Referential integrity
    train_study_set = set(df_train["StudyInstanceUID"])
    series_study_set = set(df_series["StudyInstanceUID"])

    studies_in_train_not_in_series = len(train_study_set - series_study_set)
    studies_in_series_not_in_train = len(series_study_set - train_study_set)
    referential_integrity_ok = (
        studies_in_train_not_in_series == 0 and studies_in_series_not_in_train == 0
    )

    notes: list[str] = []
    if fluid_fat_identical:
        notes.append(
            "Fluid_Sensitive y Fat_Suppression tienen exactamente los mismos valores "
            "en todas las filas del conjunto de series analizado."
        )
    if num_partial_nan_studies == 0:
        notes.append(
            "No existen estudios con etiquetas parciales: cada estudio tiene las 12 "
            "etiquetas completas (Gold) o las 12 en NaN."
        )

    return DatasetAuditReport(
        num_train_studies=num_train_studies,
        num_unique_train_studies=num_unique_train_studies,
        num_train_duplicate_studies=num_train_duplicate_studies,
        missing_reports_count=missing_reports_count,
        num_gold_studies=num_gold_studies,
        num_all_nan_studies=num_all_nan_studies,
        num_partial_nan_studies=num_partial_nan_studies,
        gold_positive_counts=gold_positive_counts,
        gold_prevalence=gold_prevalence,
        num_series_rows=num_series_rows,
        num_unique_series=num_unique_series,
        num_series_duplicate_uids=num_series_duplicate_uids,
        num_unique_studies_in_series=num_unique_studies_in_series,
        plane_distribution=plane_dist,
        fluid_sensitive_distribution=fluid_dist,
        fat_suppression_distribution=fat_dist,
        fluid_fat_identical=fluid_fat_identical,
        fluid_fat_mismatches=fluid_fat_mismatches,
        series_per_study_stats=series_stats,
        studies_with_all_three_planes=studies_with_all_three,
        plane_coverage_counts=plane_coverage_counts,
        studies_in_train_not_in_series=studies_in_train_not_in_series,
        studies_in_series_not_in_train=studies_in_series_not_in_train,
        referential_integrity_ok=referential_integrity_ok,
        train_csv_path=train_path_str,
        train_series_csv_path=series_path_str,
        notes=notes,
    )


def main() -> None:
    """CLI entrypoint for auditing the dataset."""
    parser = argparse.ArgumentParser(
        description="Auditoría básica del dataset RSNA Knee Abnormality Detection"
    )
    parser.add_argument(
        "--train-csv",
        type=str,
        default=None,
        help="Ruta a train.csv (por defecto busca en raíz o data/raw/)",
    )
    parser.add_argument(
        "--train-series-csv",
        type=str,
        default=None,
        help="Ruta a train_series.csv (por defecto busca en raíz o data/raw/)",
    )
    args = parser.parse_args()

    report = audit_dataset(
        train_csv=args.train_csv,
        train_series_csv=args.train_series_csv,
    )
    print(report.format_summary())


if __name__ == "__main__":
    main()

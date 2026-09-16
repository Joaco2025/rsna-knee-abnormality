"""Tests for dataset audit module."""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from rsna_knee.data.audit import (
    GOLD_LABEL_COLUMNS,
    DatasetAuditReport,
    audit_dataset,
)


@pytest.fixture
def synthetic_train_df() -> pd.DataFrame:
    """Fixture providing a synthetic train DataFrame with controlled Gold, all-NaN, and partial-NaN."""
    data = {
        "StudyInstanceUID": [f"study_{i}" for i in range(1, 7)],
        "Report": [f"Clinical report for study {i}" for i in range(1, 7)],
    }
    # Initialize all labels to NaN
    for col in GOLD_LABEL_COLUMNS:
        data[col] = [np.nan] * 6

    df = pd.DataFrame(data)

    # study_1: Gold case with all 1s
    for col in GOLD_LABEL_COLUMNS:
        df.loc[df["StudyInstanceUID"] == "study_1", col] = 1.0

    # study_2: Gold case with mixed 0s and 1s (ACL=1, MCL=0)
    for col in GOLD_LABEL_COLUMNS:
        df.loc[df["StudyInstanceUID"] == "study_2", col] = 0.0
    df.loc[df["StudyInstanceUID"] == "study_2", "ACL"] = 1.0

    # study_3, study_4, study_5: completely NaN in all 12 labels (already NaN)

    # study_6: partial NaN (ACL is 1.0, others NaN)
    df.loc[df["StudyInstanceUID"] == "study_6", "ACL"] = 1.0

    return df


@pytest.fixture
def synthetic_series_df() -> pd.DataFrame:
    """Fixture providing a synthetic series DataFrame matching studies 1 to 6."""
    series_data = []
    # Assign series to studies 1 to 6
    # study_1: 3 series (Sagittal, Coronal, Axial)
    for plane, s_id in [("Sagittal", "s1_1"), ("Coronal", "s1_2"), ("Axial", "s1_3")]:
        series_data.append({
            "StudyInstanceUID": "study_1",
            "SeriesInstanceUID": s_id,
            "Fluid_Sensitive": 1,
            "Fat_Suppression": 1,
            "Anatomical_Plane": plane,
        })

    # study_2 to study_6: 2 series each
    for i in range(2, 7):
        study_id = f"study_{i}"
        series_data.append({
            "StudyInstanceUID": study_id,
            "SeriesInstanceUID": f"s{i}_1",
            "Fluid_Sensitive": 1,
            "Fat_Suppression": 1,
            "Anatomical_Plane": "Sagittal",
        })
        series_data.append({
            "StudyInstanceUID": study_id,
            "SeriesInstanceUID": f"s{i}_2",
            "Fluid_Sensitive": 0,
            "Fat_Suppression": 0,
            "Anatomical_Plane": "Coronal",
        })

    return pd.DataFrame(series_data)


def test_audit_gold_and_nan_separation(
    synthetic_train_df: pd.DataFrame, synthetic_series_df: pd.DataFrame
):
    """Verify that Gold cases, complete NaNs, and partial NaNs are partitioned correctly."""
    report = audit_dataset(
        train_csv=synthetic_train_df,
        train_series_csv=synthetic_series_df,
    )

    assert report.num_train_studies == 6
    assert report.num_gold_studies == 2
    assert report.num_all_nan_studies == 3
    assert report.num_partial_nan_studies == 1

    # Check that positive counts are computed only on the Gold cases
    # ACL: study_1 has 1, study_2 has 1 -> total = 2 (study_6 partial is ignored in gold metrics)
    assert report.gold_positive_counts["ACL"] == 2
    assert report.gold_prevalence["ACL"] == 1.0  # 2 out of 2 gold

    # MCL: study_1 has 1, study_2 has 0 -> total = 1
    assert report.gold_positive_counts["MCL"] == 1
    assert report.gold_prevalence["MCL"] == 0.5  # 1 out of 2 gold


def test_audit_referential_integrity_and_duplicates(
    synthetic_train_df: pd.DataFrame, synthetic_series_df: pd.DataFrame
):
    """Verify detection of duplicates and referential inconsistencies."""
    # Add a duplicate study in train
    df_train_dup = pd.concat([synthetic_train_df, synthetic_train_df.iloc[[0]]], ignore_index=True)

    # Add an orphan study in series (study_99 not in train)
    orphan_series = pd.DataFrame([{
        "StudyInstanceUID": "study_99",
        "SeriesInstanceUID": "s99_1",
        "Fluid_Sensitive": 1,
        "Fat_Suppression": 1,
        "Anatomical_Plane": "Axial",
    }])
    # And add a duplicate series UID
    dup_series = pd.DataFrame([{
        "StudyInstanceUID": "study_1",
        "SeriesInstanceUID": "s1_1",  # duplicate UID
        "Fluid_Sensitive": 1,
        "Fat_Suppression": 1,
        "Anatomical_Plane": "Sagittal",
    }])
    df_series_inconsistent = pd.concat([synthetic_series_df, orphan_series, dup_series], ignore_index=True)

    report = audit_dataset(
        train_csv=df_train_dup,
        train_series_csv=df_series_inconsistent,
    )

    assert report.num_train_duplicate_studies == 1
    assert report.num_series_duplicate_uids == 1
    assert report.studies_in_series_not_in_train == 1
    assert report.referential_integrity_ok is False


def test_audit_plane_and_sequence_distributions(
    synthetic_train_df: pd.DataFrame, synthetic_series_df: pd.DataFrame
):
    """Verify plane counts and detection of identical vs mismatched sequence flags."""
    report = audit_dataset(
        train_csv=synthetic_train_df,
        train_series_csv=synthetic_series_df,
    )

    assert report.plane_distribution["Sagittal"] == 6
    assert report.plane_distribution["Coronal"] == 6
    assert report.plane_distribution["Axial"] == 1
    assert report.fluid_fat_identical is True
    assert report.fluid_fat_mismatches == 0

    # Introduce a mismatch in Fluid_Sensitive vs Fat_Suppression
    df_series_mismatch = synthetic_series_df.copy()
    df_series_mismatch.loc[0, "Fat_Suppression"] = 0  # Fluid=1, Fat=0

    report_mismatch = audit_dataset(
        train_csv=synthetic_train_df,
        train_series_csv=df_series_mismatch,
    )
    assert report_mismatch.fluid_fat_identical is False
    assert report_mismatch.fluid_fat_mismatches == 1


def test_audit_series_per_study_stats(
    synthetic_train_df: pd.DataFrame, synthetic_series_df: pd.DataFrame
):
    """Verify series per study statistics and tri-plane coverage."""
    report = audit_dataset(
        train_csv=synthetic_train_df,
        train_series_csv=synthetic_series_df,
    )

    # study_1 has 3 series; studies 2-6 have 2 series
    assert report.series_per_study_stats["min"] == 2.0
    assert report.series_per_study_stats["max"] == 3.0
    assert report.studies_with_all_three_planes == 1  # Only study_1 has all 3


def test_audit_missing_target_column_raises_error(synthetic_series_df: pd.DataFrame):
    """Verify that train DataFrame without required label columns raises ValueError."""
    incomplete_train = pd.DataFrame({
        "StudyInstanceUID": ["s1"],
        "Report": ["text"],
        "ACL": [1.0],  # missing remaining 11 columns
    })

    with pytest.raises(ValueError, match="Target label columns missing"):
        audit_dataset(train_csv=incomplete_train, train_series_csv=synthetic_series_df)


def test_audit_real_csv_if_present():
    """Integration test that runs against actual project CSV files if present on disk."""
    train_path = Path("train.csv")
    series_path = Path("train_series.csv")

    if not (train_path.is_file() and series_path.is_file()):
        pytest.skip("train.csv and train_series.csv not found in working directory.")

    report = audit_dataset(train_csv=train_path, train_series_csv=series_path)

    assert isinstance(report, DatasetAuditReport)
    assert report.num_train_studies == 4407
    assert report.num_unique_train_studies == 4407
    assert report.num_train_duplicate_studies == 0
    assert report.missing_reports_count == 0

    assert report.num_gold_studies == 58
    assert report.num_all_nan_studies == 4349
    assert report.num_partial_nan_studies == 0

    assert report.num_series_rows == 24371
    assert report.num_unique_series == 24371
    assert report.num_series_duplicate_uids == 0

    assert report.referential_integrity_ok is True
    assert report.studies_in_train_not_in_series == 0
    assert report.studies_in_series_not_in_train == 0

    assert report.studies_with_all_three_planes == 4407
    assert report.fluid_fat_identical is True
    assert report.fluid_fat_mismatches == 0

    summary_text = report.format_summary()
    assert "RSNA KNEE ABNORMALITY DETECTION - DATASET AUDIT REPORT" in summary_text
    assert "58/58" in summary_text or "Prevalencia en casos Gold" in summary_text

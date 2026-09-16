"""Loaders de DICOM, dataset de PyTorch, splits de validación y auditoría."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rsna_knee.data.audit import DatasetAuditReport, audit_dataset


def __getattr__(name: str):
    if name in ("DatasetAuditReport", "audit_dataset"):
        from rsna_knee.data import audit

        return getattr(audit, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["DatasetAuditReport", "audit_dataset"]

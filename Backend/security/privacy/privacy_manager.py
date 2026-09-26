"""Privacy manager: classification + consent gating."""

from __future__ import annotations

from typing import Any, Dict

from security.privacy.consent import ConsentManager
from security.privacy.data_classification import DataClassification

__all__ = ["PrivacyManager"]


class PrivacyManager:
    """Gates data access on classification and consent."""

    def __init__(self, consent: ConsentManager) -> None:
        self.consent = consent

    def can_access(
        self,
        subject: str,
        purpose: str,
        classification: DataClassification,
    ) -> bool:
        """Public data is always accessible; others require consent."""
        if classification == DataClassification.PUBLIC:
            return True
        return self.consent.has_consent(subject, purpose)

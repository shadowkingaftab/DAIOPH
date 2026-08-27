"""Threat detector combining injection and anomaly checks."""

from __future__ import annotations

from typing import Any, Dict, List

from security.threat_detection.anomaly_detector import detect_anomalies
from security.threat_detection.prompt_injection import detect_prompt_injection

__all__ = ["ThreatDetector"]


class ThreatDetector:
    """Runs configured detectors and aggregates findings."""

    def __init__(self) -> None:
        self._detectors = {
            "prompt_injection": detect_prompt_injection,
            "anomaly": detect_anomalies,
        }

    def scan(self, text: str = "", values: List[float] = None) -> Dict[str, Any]:
        """Run all detectors; return per-detector findings."""
        findings: Dict[str, Any] = {}
        if text:
            flagged, signals = self._detectors["prompt_injection"](text)
            findings["prompt_injection"] = {
                "flagged": flagged, "signals": signals,
            }
        if values:
            anomalies = self._detectors["anomaly"](values)
            findings["anomaly"] = {"flagged": bool(anomalies), "indices": anomalies}
        return findings

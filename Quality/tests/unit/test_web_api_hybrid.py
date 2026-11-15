from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from Backend import web_api


def _install_fake_models(monkeypatch, local, cloud):
    calls = []

    def run_local(prompt):
        calls.append(("oda", prompt))
        return local

    def run_cloud(prompt):
        calls.append(("cloud", prompt))
        return cloud

    monkeypatch.setitem(
        sys.modules, "qwen_oda", SimpleNamespace(run_qwen=run_local)
    )
    monkeypatch.setitem(
        sys.modules, "grok_cloud", SimpleNamespace(run_grok=run_cloud)
    )
    monkeypatch.setattr(web_api, "HISTORY", [])
    return calls


def test_hybrid_translation_drafts_locally_then_translates_with_cloud(monkeypatch):
    draft = "Dear Manager, I am unwell and need sick leave tomorrow."
    translation = "Cher responsable, je suis malade et dois prendre un congé demain."
    calls = _install_fake_models(monkeypatch, draft, translation)
    monkeypatch.setenv("GROK_API_KEY", "configured")

    response = web_api.chat(
        web_api.ChatRequest(
            message=(
                "Write a short sick-leave email to my manager for tomorrow "
                "and translate it into French."
            ),
            route="Hybrid",
        )
    )

    assert [provider for provider, _ in calls] == ["oda", "cloud"]
    assert "Write a short sick-leave email" in calls[0][1]
    assert "translate it into french" not in calls[0][1].lower()
    assert draft in calls[1][1]
    assert "French" in calls[1][1]
    assert response["route"] == "Hybrid"
    assert draft in response["content"]
    assert translation in response["content"]


def test_hybrid_translation_surfaces_cloud_failure(monkeypatch):
    cloud_error = (
        '❌ Grok API Error: 403 {"code":"permission-denied",'
        '"error":"No credits left; spending limit reached"}'
    )
    calls = _install_fake_models(monkeypatch, "Local draft", cloud_error)
    monkeypatch.setenv("GROK_API_KEY", "configured")

    with pytest.raises(HTTPException) as error:
        web_api.chat(
            web_api.ChatRequest(
                message="Write a sick-leave email and translate it into French.",
                route="Hybrid",
            )
        )

    assert error.value.status_code == 503
    assert "no available credits" in error.value.detail
    assert "permission-denied" not in error.value.detail
    assert [provider for provider, _ in calls] == ["oda", "cloud"]

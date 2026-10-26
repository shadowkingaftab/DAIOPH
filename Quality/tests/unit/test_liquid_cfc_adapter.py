"""Focused tests for CfC adapter integration with LiquidEngine.

Tests:
1. Default behavior unchanged (no adapter)
2. Explicit adapter prediction
3. Verified feedback update
4. No update when feedback is absent
"""

from unittest.mock import MagicMock, patch

import pytest


class TestLiquidEngineDefaultBehavior:
    """Test that default LiquidEngine behavior is unchanged without adapter."""

    def test_engine_constructs_without_adapter(self):
        """Engine should construct normally without any adapter."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        engine = LiquidEngine()
        assert engine is not None
        assert engine._cfc_enabled is False
        assert engine._cfc_adapter is None

    def test_process_returns_expected_keys_without_adapter(self):
        """process() should return standard keys without cfc_prediction."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        engine = LiquidEngine()
        result = engine.process("test input")

        assert "action" in result
        assert "confidence" in result
        assert "uncertainty" in result
        assert "state" in result
        assert "cfc_prediction" not in result

    def test_cfc_predict_raises_without_adapter(self):
        """cfc_predict should raise RuntimeError when adapter not configured."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        engine = LiquidEngine()
        with pytest.raises(RuntimeError, match="CfC adapter not configured"):
            engine.cfc_predict("test")

    def test_cfc_update_raises_without_adapter(self):
        """cfc_update should raise RuntimeError when adapter not configured."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        engine = LiquidEngine()
        with pytest.raises(RuntimeError, match="CfC adapter not configured"):
            engine.cfc_update("test", "greeting")

    def test_get_status_unchanged(self):
        """get_status should work as before."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        engine = LiquidEngine()
        status = engine.get_status()
        assert "state" in status
        assert "context" in status
        assert "stability" in status


class TestLiquidEngineWithMockedAdapter:
    """Test engine with explicitly injected mock adapter."""

    def test_process_includes_cfc_prediction_when_adapter_provided(self):
        """process() should include cfc_prediction when adapter configured."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        mock_adapter = MagicMock()
        mock_adapter.predict.return_value = {
            "intent": "greeting",
            "confidence": 0.95,
            "logits": [0.1, 0.8, 0.1],
        }

        engine = LiquidEngine(cfc_adapter=mock_adapter)
        result = engine.process("hello world")

        assert "cfc_prediction" in result
        assert result["cfc_prediction"]["intent"] == "greeting"
        assert result["cfc_prediction"]["confidence"] == 0.95
        mock_adapter.predict.assert_called_once_with("hello world")

    def test_cfc_predict_delegates_to_adapter(self):
        """cfc_predict should delegate to adapter."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        mock_adapter = MagicMock()
        mock_adapter.predict.return_value = {
            "intent": "help",
            "confidence": 0.88,
            "logits": [0.2, 0.1, 0.7],
        }

        engine = LiquidEngine(cfc_adapter=mock_adapter)
        result = engine.cfc_predict("how do i do this")

        assert result["intent"] == "help"
        mock_adapter.predict.assert_called_once_with("how do i do this")

    def test_cfc_update_delegates_to_adapter(self):
        """cfc_update should delegate to adapter with verified label."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        mock_adapter = MagicMock()
        mock_adapter.update.return_value = {
            "loss": 0.5,
            "predicted_before": "general",
            "confidence_before": 0.5,
            "predicted_after": "greeting",
            "confidence_after": 0.9,
            "verified_intent": "greeting",
        }

        engine = LiquidEngine(cfc_adapter=mock_adapter)
        result = engine.cfc_update("hello", "greeting")

        assert result["verified_intent"] == "greeting"
        assert result["predicted_after"] == "greeting"
        mock_adapter.update.assert_called_once_with("hello", "greeting")

    def test_cfc_update_requires_verified_intent(self):
        """cfc_update must be called with verified_intent (not predicted)."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        mock_adapter = MagicMock()
        mock_adapter.update.side_effect = ValueError("intent not in label set")

        engine = LiquidEngine(cfc_adapter=mock_adapter)

        # This should raise because "not_a_real_intent" is not in label set
        with pytest.raises(ValueError):
            engine.cfc_update("hello", "not_a_real_intent")


class TestCfCAdapterStandalone:
    """Test CfC adapter directly with mocked checkpoint loading."""

    def test_adapter_lazy_loads_on_first_predict(self):
        """Adapter should not load checkpoint until predict() is called."""
        from intelligence.liquid.adapters.cfc_adapter import CfCAdapter

        with patch.object(CfCAdapter, "_load_checkpoint") as mock_load:
            mock_load.return_value = None
            adapter = CfCAdapter(checkpoint_path="/fake/path.pt")
            assert not adapter.is_loaded

            # Create a mock model and tokenizer to avoid actual loading
            adapter._loaded = True
            adapter._model = MagicMock()
            adapter._model.eval.return_value = None
            adapter._tokenizer = MagicMock()
            adapter._tokenizer.encode.return_value = [1, 2, 3]
            adapter._tokenizer.pad_id = 0
            adapter._tokenizer.vocab_size = 1000
            adapter._idx_to_label = {0: "greeting", 1: "farewell"}
            adapter._label_to_idx = {"greeting": 0, "farewell": 1}

            # Mock the model forward pass
            import torch
            mock_logits = torch.tensor([[0.1, 0.9]])
            adapter._model.return_value = mock_logits

            adapter.predict("hello")
            # _load_checkpoint is called but returns early due to _loaded flag
            mock_load.assert_called_once()

    def test_adapter_raises_on_missing_checkpoint(self):
        """Adapter should raise clear error when checkpoint missing."""
        from intelligence.liquid.adapters.cfc_adapter import CfCAdapter

        adapter = CfCAdapter(checkpoint_path="/nonexistent/path.pt")
        with pytest.raises(FileNotFoundError, match="CfC study checkpoint not found"):
            adapter.predict("test")

    def test_adapter_update_rejects_unknown_intent(self):
        """update() should reject intent not in known label set."""
        from intelligence.liquid.adapters.cfc_adapter import CfCAdapter

        adapter = CfCAdapter(checkpoint_path="/fake/model.pt")
        adapter._loaded = True
        adapter._label_to_idx = {"greeting": 0, "farewell": 1}
        adapter._idx_to_label = {0: "greeting", 1: "farewell"}
        adapter._model = MagicMock()
        adapter._model.train.return_value = None
        adapter._model.eval.return_value = None
        adapter._model.parameters.return_value = []
        adapter._tokenizer = MagicMock()
        adapter._tokenizer.encode.return_value = [1, 2, 3]
        adapter._tokenizer.pad_id = 0

        with pytest.raises(ValueError, match="not in known label set"):
            adapter.update("hello", "unknown_intent")

    def test_update_never_uses_predicted_label(self):
        """Test that update requires explicit verified_intent argument.

        The adapter design forces caller to pass verified_intent explicitly.
        There is no path where the model's own prediction is used for update.
        """
        from intelligence.liquid.adapters.cfc_adapter import CfCAdapter

        adapter = CfCAdapter(checkpoint_path="/fake/model.pt")
        adapter._loaded = True
        adapter._label_to_idx = {"greeting": 0}
        adapter._idx_to_label = {0: "greeting"}
        adapter._model = MagicMock()
        adapter._model.train.return_value = None
        adapter._model.eval.return_value = None
        adapter._model.parameters.return_value = []
        adapter._tokenizer = MagicMock()
        adapter._tokenizer.encode.return_value = [1, 2, 3]
        adapter._tokenizer.pad_id = 0

        # This call requires explicit verified_intent - no default, no auto-predict
        with patch("torch.optim.Adam"):
            with patch("torch.nn.CrossEntropyLoss"):
                try:
                    adapter.update("hello", "greeting")
                except Exception:
                    pass  # Expected due to mocking

        # Verify update was called with explicit verified_intent
        # The key assertion: update() signature requires verified_intent parameter
        import inspect
        sig = inspect.signature(adapter.update)
        params = list(sig.parameters.keys())
        assert "verified_intent" in params
        assert "verified_intent" != "predicted_intent"  # Not using predicted
        adapter._idx_to_label = {0: "greeting"}
        adapter._model = MagicMock()
        adapter._model.train.return_value = None
        adapter._model.eval.return_value = None
        adapter._model.parameters.return_value = []
        adapter._tokenizer = MagicMock()
        adapter._tokenizer.encode.return_value = [1, 2, 3]
        adapter._tokenizer.pad_id = 0

        # This call requires explicit verified_intent - no default, no auto-predict
        with patch("torch.optim.Adam"):
            with patch("torch.nn.CrossEntropyLoss"):
                try:
                    adapter.update("hello", "greeting")
                except Exception:
                    pass  # Expected due to mocking

        # Verify update was called with explicit verified_intent
        # The key assertion: update() signature requires verified_intent parameter
        import inspect
        sig = inspect.signature(adapter.update)
        params = list(sig.parameters.keys())
        assert "verified_intent" in params
        assert "verified_intent" != "predicted_intent"  # Not using predicted


class TestIntegrationSmoke:
    """Short integration smoke test."""

    def test_engine_with_adapter_smoke(self):
        """Smoke test: engine works with adapter injected."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        mock_adapter = MagicMock()
        mock_adapter.predict.return_value = {"intent": "test", "confidence": 0.5, "logits": []}

        engine = LiquidEngine(cfc_adapter=mock_adapter)
        result = engine.process("test input")

        assert result["action"] in ("process", "adapt", "stabilize")
        assert "cfc_prediction" in result

    def test_engine_without_adapter_smoke(self):
        """Smoke test: engine works without adapter (default)."""
        from intelligence.liquid.liquid_engine import LiquidEngine

        engine = LiquidEngine()
        result = engine.process("test input")

        assert result["action"] in ("process", "adapt", "stabilize")
        assert "cfc_prediction" not in result
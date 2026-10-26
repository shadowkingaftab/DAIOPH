"""CfC Study Model Adapter for Liquid Intelligence Engine.

This adapter connects a trained CfC (Closed-form Continuous-time) model from the
liquid_streaming study to the LiquidEngine as an optional adaptation component.

The adapter exposes:
- predict(text): returns intent prediction
- update(text, verified_intent): updates model with verified label (never from own prediction)

Model loading is lazy. A clear error is raised if the study checkpoint is missing or incompatible.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn

try:
    from ncps.torch import CfC
except Exception:  # pragma: no cover - optional dependency
    CfC = None

try:
    from Research.experiments.liquid_streaming.src.tokenizer import SimpleTokenizer
except Exception:  # pragma: no cover - optional dependency
    SimpleTokenizer = None


class CfcTextClassifier(nn.Module):
    """CfC text classifier matching the study architecture."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 64,
        hidden_size: int = 64,
        num_classes: int = 10,
        pad_id: int = 0,
        mixed_memory: bool = False,
        mode: str = "default",
    ):
        super().__init__()
        if CfC is None:
            raise RuntimeError("ncps package not installed; cannot instantiate CfC model")
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        self.cfc = CfC(
            input_size=embed_dim,
            units=hidden_size,
            return_sequences=False,
            batch_first=True,
            mixed_memory=mixed_memory,
            mode=mode,
        )
        self.head = nn.Linear(hidden_size, num_classes)
        self.pad_id = pad_id
        self.num_classes = num_classes

    def forward(self, input_ids, lengths=None):
        emb = self.embedding(input_ids)
        out, _ = self.cfc(emb)
        if isinstance(out, (list, tuple)):
            out = out[0]
        if out.dim() == 3:
            out = out[:, -1, :]
        return self.head(out)

    def set_num_classes(self, new_num_classes: int):
        if new_num_classes <= self.num_classes:
            return
        old_out, in_features = self.head.weight.shape
        new_head = nn.Linear(in_features, new_num_classes)
        with torch.no_grad():
            new_head.weight[:old_out] = self.head.weight
            new_head.bias[:old_out] = self.head.bias
            nn.init.xavier_uniform_(new_head.weight[old_out:])
            new_head.bias[old_out:].zero_()
        self.head = new_head
        self.num_classes = new_num_classes


class CfCAdapter:
    """Adapter for CfC study model to integrate with LiquidEngine.

    Usage:
        adapter = CfCAdapter(checkpoint_path="path/to/checkpoint.pt")
        # Default engine behavior unchanged - adapter not used unless explicitly called
        prediction = adapter.predict("hello world")
        # Only update with VERIFIED intent label (never from own prediction)
        adapter.update("hello world", "greeting")
    """

    DEFAULT_CHECKPOINT_REL = Path("Research/experiments/liquid_streaming/outputs/checkpoints/best_model.pt")

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None,
        label_map_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the CfC adapter.

        Args:
            checkpoint_path: Path to model checkpoint (.pt file with state_dict + metadata).
                           If None, tries default location.
            tokenizer_path: Path to tokenizer pickle. If None, derived from checkpoint dir.
            label_map_path: Path to label mapping JSON. If None, derived from checkpoint dir.
            config: Optional configuration dict with keys:
                    - embed_dim, hidden_size, mode, mixed_memory
        """
        self.config = config or {}
        self._model: Optional[CfcTextClassifier] = None
        self._tokenizer: Optional[SimpleTokenizer] = None
        self._label_to_idx: Dict[str, int] = {}
        self._idx_to_label: Dict[int, str] = {}
        self._loaded = False
        self._checkpoint_path = checkpoint_path
        self._tokenizer_path = tokenizer_path
        self._label_map_path = label_map_path

    def _resolve_paths(self) -> Tuple[Path, Path, Path]:
        """Resolve checkpoint, tokenizer, and label map paths."""
        if self._checkpoint_path:
            ckpt = Path(self._checkpoint_path)
        else:
            # Try default relative to project root
            ckpt = Path.cwd() / self.DEFAULT_CHECKPOINT_REL

        if not ckpt.is_absolute():
            # Try relative to current working directory, then project root
            if not ckpt.exists():
                project_root = Path(__file__).resolve().parents[4]
                ckpt = project_root / self.DEFAULT_CHECKPOINT_REL

        if self._tokenizer_path:
            tok = Path(self._tokenizer_path)
        else:
            tok = ckpt.parent / "tokenizer.pkl"

        if self._label_map_path:
            lbl = Path(self._label_map_path)
        else:
            lbl = ckpt.parent / "label_map.json"

        return ckpt, tok, lbl

    def _load_checkpoint(self) -> None:
        """Load model, tokenizer, and label map from checkpoint."""
        if self._loaded:
            return

        ckpt_path, tok_path, lbl_path = self._resolve_paths()

        if not ckpt_path.exists():
            raise FileNotFoundError(
                f"CfC study checkpoint not found at {ckpt_path}. "
                f"Run the liquid_streaming study to generate a checkpoint, "
                f"or provide checkpoint_path explicitly."
            )

        if not tok_path.exists():
            raise FileNotFoundError(
                f"Tokenizer not found at {tok_path}. "
                f"Expected alongside checkpoint."
            )

        if not lbl_path.exists():
            raise FileNotFoundError(
                f"Label map not found at {lbl_path}. "
                f"Expected alongside checkpoint."
            )

        # Load checkpoint
        try:
            ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        except Exception as e:
            raise RuntimeError(f"Failed to load checkpoint {ckpt_path}: {e}")

        # Load tokenizer
        try:
            with open(tok_path, "rb") as f:
                self._tokenizer = pickle.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load tokenizer {tok_path}: {e}")

        # Load label map
        import json
        try:
            with open(lbl_path, "r", encoding="utf-8") as f:
                label_data = json.load(f)
                self._label_to_idx = label_data.get("label_to_idx", {})
                self._idx_to_label = {v: k for k, v in self._label_to_idx.items()}
        except Exception as e:
            raise RuntimeError(f"Failed to load label map {lbl_path}: {e}")

        # Extract model config from checkpoint or use defaults
        vocab_size = ckpt.get("vocab_size", self._tokenizer.vocab_size)
        embed_dim = self.config.get("embed_dim", ckpt.get("embed_dim", 64))
        hidden_size = self.config.get("hidden_size", ckpt.get("hidden_size", 64))
        num_classes = len(self._label_to_idx) or ckpt.get("num_classes", 10)
        pad_id = self.config.get("pad_id", ckpt.get("pad_id", 0))
        mixed_memory = self.config.get("mixed_memory", ckpt.get("mixed_memory", False))
        mode = self.config.get("mode", ckpt.get("mode", "default"))

        # Build model
        self._model = CfcTextClassifier(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            hidden_size=hidden_size,
            num_classes=num_classes,
            pad_id=pad_id,
            mixed_memory=mixed_memory,
            mode=mode,
        )

        # Load state dict
        state_dict = ckpt.get("model_state_dict") or ckpt.get("state_dict") or ckpt
        try:
            self._model.load_state_dict(state_dict, strict=False)
        except Exception as e:
            raise RuntimeError(f"Incompatible checkpoint: state_dict mismatch: {e}")

        self._model.eval()
        self._loaded = True

    def predict(self, text: str, max_len: int = 64) -> Dict[str, Any]:
        """Predict intent for a single text input.

        Args:
            text: Input text to classify.
            max_len: Maximum token sequence length.

        Returns:
            Dict with keys: intent (str), confidence (float), logits (list[float])
        """
        self._load_checkpoint()

        if not text or not text.strip():
            return {"intent": "unknown", "confidence": 0.0, "logits": []}

        # Tokenize
        ids = self._tokenizer.encode(text, max_len=max_len)
        if len(ids) < max_len:
            ids = [self._tokenizer.pad_id] * (max_len - len(ids)) + ids
        else:
            ids = ids[-max_len:]
        input_ids = torch.tensor([ids], dtype=torch.long)

        # Predict
        with torch.no_grad():
            logits = self._model(input_ids)
            probs = torch.softmax(logits, dim=1)
            pred_idx = int(probs.argmax(dim=1).item())
            confidence = float(probs[0, pred_idx].item())

        intent = self._idx_to_label.get(pred_idx, "unknown")
        return {
            "intent": intent,
            "confidence": confidence,
            "logits": logits[0].tolist(),
        }

    def update(self, text: str, verified_intent: str, lr: float = 1e-3, steps: int = 1) -> Dict[str, Any]:
        """Update model with a VERIFIED intent label.

        This method MUST be called with a human-verified or ground-truth label.
        NEVER call this with the model's own predicted label - that would cause
        confirmation bias and degrade performance.

        Args:
            text: Input text.
            verified_intent: Ground-truth intent label (must be verified externally).
            lr: Learning rate for the update step.
            steps: Number of gradient steps to take.

        Returns:
            Dict with update info: loss, predicted_before, predicted_after
        """
        self._load_checkpoint()

        if verified_intent not in self._label_to_idx:
            raise ValueError(
                f"Verified intent '{verified_intent}' not in known label set: "
                f"{list(self._label_to_idx.keys())}"
            )

        # Get prediction before update
        pred_before = self.predict(text)

        # Tokenize
        max_len = 64
        ids = self._tokenizer.encode(text, max_len=max_len)
        if len(ids) < max_len:
            ids = [self._tokenizer.pad_id] * (max_len - len(ids)) + ids
        else:
            ids = ids[-max_len:]
        input_ids = torch.tensor([ids], dtype=torch.long)
        target = torch.tensor([self._label_to_idx[verified_intent]], dtype=torch.long)

        # Enable training mode for this update
        self._model.train()
        optimizer = torch.optim.Adam(self._model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        loss_val = 0.0
        for _ in range(steps):
            optimizer.zero_grad()
            logits = self._model(input_ids)
            loss = criterion(logits, target)
            loss.backward()
            optimizer.step()
            loss_val = float(loss.item())

        self._model.eval()

        # Get prediction after update
        pred_after = self.predict(text)

        return {
            "loss": loss_val,
            "predicted_before": pred_before["intent"],
            "confidence_before": pred_before["confidence"],
            "predicted_after": pred_after["intent"],
            "confidence_after": pred_after["confidence"],
            "verified_intent": verified_intent,
        }

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded

    @property
    def known_intents(self) -> list[str]:
        """Get list of known intent labels."""
        return list(self._label_to_idx.keys())

    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata."""
        self._load_checkpoint()
        return {
            "vocab_size": self._tokenizer.vocab_size if self._tokenizer else 0,
            "num_classes": self._model.num_classes if self._model else 0,
            "known_intents": self.known_intents,
            "loaded": self._loaded,
        }
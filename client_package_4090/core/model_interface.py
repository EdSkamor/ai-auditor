"""
Unified model interface for AI Auditor system.
Supports both HuggingFace and llama.cpp backends.
"""

import logging
import os
import subprocess
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

try:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

    # Mock classes for testing
    class MockTorch:
        class float16:
            pass

        def ones_like(self, *args, **kwargs):
            return None

        def no_grad(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    torch = MockTorch()

    class MockTransformers:
        class AutoTokenizer:
            @staticmethod
            def from_pretrained(*args, **kwargs):
                return None

        class AutoModelForCausalLM:
            @staticmethod
            def from_pretrained(*args, **kwargs):
                return None

        class BitsAndBytesConfig:
            def __init__(self, *args, **kwargs):
                pass

    AutoTokenizer = MockTransformers.AutoTokenizer
    AutoModelForCausalLM = MockTransformers.AutoModelForCausalLM
    BitsAndBytesConfig = MockTransformers.BitsAndBytesConfig

    class MockPEFT:
        class PeftModel:
            @staticmethod
            def from_pretrained(*args, **kwargs):
                return None

    PeftModel = MockPEFT.PeftModel

from .exceptions import AuditorException, ModelLoadError

logger = logging.getLogger(__name__)


class ModelInterface(ABC):
    """Abstract base class for model interfaces."""

    @abstractmethod
    def call_model(self, prompt: str, **kwargs) -> str:
        """Generate response from model."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if model is ready for inference."""
        pass


class HuggingFaceModel(ModelInterface):
    """HuggingFace model interface with LoRA support."""

    def __init__(
        self,
        model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        adapter_dir: Optional[Path] = None,
        use_quantization: bool = True,
        device: str = "auto",
    ):
        self.model_name = model_name
        self.adapter_dir = adapter_dir or (
            Path(__file__).parent.parent / "outputs" / "lora-auditor"
        )
        self.use_quantization = use_quantization
        self.device = device

        self._tokenizer = None
        self._model = None
        self._ready = False

        self.system_prompt = (
            "Jesteś ekspertem ds. audytu finansowego. "
            "Odpowiadasz wyłącznie po polsku, zwięźle i rzeczowo; gdy to pasuje – w punktach. "
            "Przy różnicach wartości podawaj p.p. (punkty procentowe), a nie %."
        )

    def _load_model(self) -> None:
        """Load the model and tokenizer."""
        if self._ready:
            return

        if not HAS_TORCH:
            raise ModelLoadError(
                "PyTorch and transformers not available. Install with: pip install torch transformers",
                self.model_name,
            )

        try:
            logger.info(f"Loading model: {self.model_name}")

            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, use_fast=False
            )
            if self._tokenizer.pad_token_id is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token

            # Load base model
            if self.use_quantization:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=torch.float16,
                )
                base_model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=bnb_config,
                    device_map=self.device,
                )
            else:
                base_model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map=self.device,
                )

            # Load LoRA adapter if available
            if (
                self.adapter_dir.exists()
                and (self.adapter_dir / "adapter_config.json").exists()
            ):
                logger.info(f"Loading LoRA adapter from: {self.adapter_dir}")
                self._model = PeftModel.from_pretrained(
                    base_model, str(self.adapter_dir), device_map=self.device
                )
            else:
                logger.info("No LoRA adapter found, using base model")
                self._model = base_model

            self._model.eval()
            self._ready = True
            logger.info("Model loaded successfully")

        except Exception as e:
            raise ModelLoadError(
                f"Failed to load model {self.model_name}: {str(e)}", self.model_name
            )

    def call_model(
        self,
        prompt: str,
        max_new_tokens: int = 160,
        do_sample: bool = False,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate response using HuggingFace model."""
        self._load_model()

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]

            inputs = self._tokenizer.apply_chat_template(
                messages, return_tensors="pt", add_generation_prompt=True
            )
            input_ids = inputs.to(self._model.device)
            attention_mask = torch.ones_like(input_ids, dtype=torch.long)

            gen_kwargs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "max_new_tokens": max_new_tokens,
                "do_sample": do_sample,
                "pad_token_id": self._tokenizer.eos_token_id,
            }

            if do_sample:
                gen_kwargs.update(temperature=temperature, top_p=top_p)

            with torch.no_grad():
                output_ids = self._model.generate(**gen_kwargs)

            response = self._tokenizer.decode(
                output_ids[0, input_ids.shape[1] :], skip_special_tokens=True
            )

            return response.strip()

        except Exception as e:
            raise AuditorException(f"Model inference failed: {str(e)}")

    def is_ready(self) -> bool:
        """Check if model is ready."""
        return self._ready


class LlamaCppModel(ModelInterface):
    """llama.cpp model interface."""

    def __init__(
        self,
        llama_bin: Optional[Path] = None,
        model_path: Optional[Path] = None,
        ngl: int = 100,
        threads: Optional[int] = None,
    ):
        self.llama_bin = llama_bin or (
            Path(__file__).parent.parent
            / "third_party"
            / "llama.cpp"
            / "build"
            / "bin"
            / "llama-cli"
        )
        self.model_path = model_path or (
            Path.home() / "models" / "llama3" / "meta-llama-3-8b-instruct.Q4_K_M.gguf"
        )
        self.ngl = ngl
        self.threads = threads or os.cpu_count() or 8
        self._ready = False

        self._check_availability()

    def _check_availability(self) -> None:
        """Check if llama.cpp binary and model are available."""
        if not self.llama_bin.exists():
            raise ModelLoadError(f"llama.cpp binary not found: {self.llama_bin}")

        if not self.model_path.exists():
            raise ModelLoadError(f"Model file not found: {self.model_path}")

        self._ready = True

    def call_model(
        self,
        prompt: str,
        n_predict: int = 80,
        temperature: float = 0.2,
        timeout_s: int = 900,
    ) -> str:
        """Generate response using llama.cpp."""
        if not self._ready:
            raise ModelLoadError("llama.cpp model not ready")

        try:
            cmd = [
                str(self.llama_bin),
                "-no-cnv",  # Disable conversation mode
                "-p",
                prompt,
                "-n",
                str(n_predict),
                "-ngl",
                str(self.ngl),
                "-t",
                str(self.threads),
                "--temp",
                str(temperature),
                "-m",
                str(self.model_path),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout_s
            )

            if result.returncode != 0:
                raise AuditorException(f"llama.cpp error: {result.stderr.strip()}")

            return textwrap.dedent(result.stdout).strip()

        except subprocess.TimeoutExpired:
            raise AuditorException(f"Model inference timeout after {timeout_s}s")
        except Exception as e:
            raise AuditorException(f"llama.cpp inference failed: {str(e)}")

    def is_ready(self) -> bool:
        """Check if model is ready."""
        return self._ready


class MockModel(ModelInterface):
    """Mock model for testing and development."""

    def __init__(self):
        self._ready = True

    def call_model(self, prompt: str, **kwargs) -> str:
        """Generate mock response."""
        return f"[MOCK RESPONSE] Analiza promptu: {prompt[:60]}..."

    def is_ready(self) -> bool:
        """Always ready."""
        return True


def create_model_interface(backend: str = "huggingface", **kwargs) -> ModelInterface:
    """Factory function to create model interface."""
    backend = backend.lower()

    if backend == "huggingface":
        return HuggingFaceModel(**kwargs)
    elif backend == "llamacpp":
        return LlamaCppModel(**kwargs)
    elif backend == "mock":
        return MockModel(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")


# Global model instance
_model_interface: Optional[ModelInterface] = None


def get_model_interface() -> ModelInterface:
    """Get the global model interface instance."""
    global _model_interface
    if _model_interface is None:
        # Try HuggingFace first, fallback to mock
        try:
            _model_interface = create_model_interface("huggingface")
        except Exception as e:
            logger.warning(f"Failed to load HuggingFace model: {e}, using mock")
            _model_interface = create_model_interface("mock")

    return _model_interface


def call_model(prompt: str, **kwargs) -> str:
    """Convenience function to call the global model."""
    return get_model_interface().call_model(prompt, **kwargs)

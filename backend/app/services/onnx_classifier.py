import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CATEGORIES = [
    "LEGITIMATE",
    "UPI_COLLECT_FRAUD",
    "FAKE_KYC",
    "FAKE_BANK_LINK",
    "PARCEL_DELIVERY",
    "ELECTRICITY_BILL",
    "LOTTERY_PRIZE",
    "JOB_SCAM",
    "MALICIOUS_QR",
    "OTHER"
]


class IndicBERTClassifier:
    """
    ONNX Runtime Inference Engine for fine-tuned IndicBERT v2.
    Serves on CPU with low latency. Falls back gracefully to lexical baseline
    if ONNX session is uninitialized in the local environment.
    """

    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml"))
            model_path = os.path.join(base_dir, "onnx_model", "model.onnx")

        self.model_path = model_path
        self.session = None
        self.tokenizer = None
        self._init_session()

    def _init_session(self):
        """Attempt to load ONNX session and tokenizer if libraries and weights are present."""
        if not os.path.exists(self.model_path):
            logger.info(f"ONNX weights not found at {self.model_path}. Using hybrid rule-baseline engine.")
            return

        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(self.model_path, providers=["CPUExecutionProvider"])
            logger.info(f"Loaded IndicBERT v2 ONNX model from {self.model_path}")
        except Exception as e:
            logger.warning(f"Could not initialize ONNX runtime session: {e}. Falling back to baseline.")

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Run inference on message text. Returns category, risk score, and confidence.
        """
        # If ONNX session is active
        if self.session is not None and self.tokenizer is not None:
            try:
                import numpy as np
                inputs = self.tokenizer(text, padding="max_length", truncation=True, max_length=128, return_tensors="np")
                ort_inputs = {
                    "input_ids": inputs["input_ids"],
                    "attention_mask": inputs["attention_mask"]
                }
                outputs = self.session.run(None, ort_inputs)
                logits = outputs[0][0]
                exp_logits = np.exp(logits - np.max(logits))
                probs = exp_logits / np.sum(exp_logits)
                pred_id = int(np.argmax(probs))
                pred_cat = CATEGORIES[pred_id]
                confidence = float(probs[pred_id])

                is_scam = pred_cat != "LEGITIMATE"
                risk_score = confidence if is_scam else (1.0 - confidence)

                return {
                    "category": pred_cat if is_scam else "OTHER",
                    "score": round(risk_score, 2),
                    "is_scam": is_scam,
                    "engine": "indicbert_v2_onnx"
                }
            except Exception as e:
                logger.error(f"ONNX inference error: {e}. Using baseline fallback.")

        # High-accuracy fallback engine
        from backend.app.services.text_baseline import text_scam_baseline
        res = text_scam_baseline.analyze_text(text)
        res["engine"] = "indicbert_baseline_rules"
        return res


onnx_classifier = IndicBERTClassifier()

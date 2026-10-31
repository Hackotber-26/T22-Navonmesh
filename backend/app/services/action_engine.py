import os
import logging
from typing import List, Dict, Any
import yaml

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

ALL_CATEGORIES = [
    "UPI_COLLECT_FRAUD",
    "FAKE_KYC",
    "FAKE_BANK_LINK",
    "PARCEL_DELIVERY",
    "ELECTRICITY_BILL",
    "LOTTERY_PRIZE",
    "JOB_SCAM",
    "MALICIOUS_QR",
    "OTHER",
]

ALL_RISK_LEVELS = ["low", "medium", "high", "critical"]
ALL_ACTION_STATES = ["not_acted", "clicked", "paid"]


class ActionEngine:
    """Deterministic Action Engine reading rules/actions.yaml to produce ordered action codes."""

    def __init__(self, rules_file_path: str = None):
        if rules_file_path is None:
            # Look in project root rules/actions.yaml
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../rules"))
            rules_file_path = os.path.join(base_dir, "actions.yaml")

        self.rules_path = rules_file_path
        self.rules_version = "v1.0.0"
        self.matrix: Dict[str, Any] = {}
        self.load_rules()

    def load_rules(self) -> None:
        """Load and parse actions.yaml file."""
        if not os.path.exists(self.rules_path):
            logger.warning(f"Actions file not found at {self.rules_path}, using built-in defaults.")
            self._load_fallback_rules()
            return

        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.rules_version = data.get("version", settings.RULES_VERSION)
                self.matrix = data.get("categories", {})
                logger.info(f"Loaded {len(self.matrix)} categories from actions.yaml (v{self.rules_version})")
        except Exception as e:
            logger.error(f"Error parsing {self.rules_path}: {e}. Falling back to default rules.")
            self._load_fallback_rules()

    def _load_fallback_rules(self) -> None:
        self.rules_version = settings.RULES_VERSION
        self.matrix = {
            "OTHER": {
                "low": {
                    "not_acted": ["VERIFY_OFFICIAL", "DO_NOT_CLICK"],
                    "clicked": ["CALL_BANK", "SAVE_EVIDENCE"],
                    "paid": ["REPORT_1930", "CALL_BANK", "SAVE_EVIDENCE"],
                },
                "medium": {
                    "not_acted": ["DO_NOT_CLICK", "NEVER_SHARE_OTP_PIN", "VERIFY_OFFICIAL"],
                    "clicked": ["CALL_BANK", "SAVE_EVIDENCE", "REPORT_PORTAL"],
                    "paid": ["REPORT_1930", "CALL_BANK", "SAVE_EVIDENCE", "REPORT_PORTAL"],
                },
                "high": {
                    "not_acted": ["DO_NOT_CLICK", "NEVER_SHARE_OTP_PIN", "DELETE_AND_BLOCK", "INFORM_FAMILY"],
                    "clicked": ["CALL_BANK", "CHANGE_PASSWORD", "SAVE_EVIDENCE", "REPORT_PORTAL"],
                    "paid": ["REPORT_1930", "CALL_BANK", "SAVE_EVIDENCE", "REPORT_PORTAL"],
                },
                "critical": {
                    "not_acted": ["DO_NOT_CLICK", "NEVER_SHARE_OTP_PIN", "DELETE_AND_BLOCK", "REPORT_SANCHAR_SAATHI"],
                    "clicked": ["CALL_BANK", "CHANGE_PASSWORD", "SAVE_EVIDENCE", "REPORT_1930", "REPORT_PORTAL"],
                    "paid": ["REPORT_1930", "CALL_BANK", "SAVE_EVIDENCE", "REPORT_PORTAL"],
                },
            }
        }

    def get_actions(
        self,
        category: str,
        risk_level: str,
        user_action_state: str = "not_acted"
    ) -> List[str]:
        """Lookup ordered action codes for category, risk level, and user action state."""
        cat_data = self.matrix.get(category)
        if not cat_data:
            cat_data = self.matrix.get("OTHER", {})

        level_data = cat_data.get(risk_level)
        if not level_data:
            level_data = cat_data.get("low", {})

        action_list = level_data.get(user_action_state)
        if not action_list:
            action_list = level_data.get("not_acted", ["DO_NOT_CLICK", "VERIFY_OFFICIAL"])

        return list(action_list)

    def validate_rules_completeness(self) -> List[str]:
        """Validate that all defined categories have rules for all risk levels and action states."""
        missing = []
        for cat in ALL_CATEGORIES:
            if cat not in self.matrix:
                missing.append(f"Missing category: {cat}")
                continue
            cat_entry = self.matrix[cat]
            for rl in ALL_RISK_LEVELS:
                if rl not in cat_entry:
                    missing.append(f"Missing risk level {rl} in category {cat}")
                    continue
                rl_entry = cat_entry[rl]
                for state in ALL_ACTION_STATES:
                    if state not in rl_entry or not isinstance(rl_entry[state], list):
                        missing.append(f"Missing action state {state} in {cat}->{rl}")
        return missing


action_engine = ActionEngine()


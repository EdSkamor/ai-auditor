"""
Rules loader for AI Auditor
Loads and manages audit rules from YAML configuration
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class RulesLoader:
    """Loader for audit rules from YAML configuration."""

    def __init__(self, rules_file: str = "rules.yaml"):
        """
        Initialize rules loader.

        Args:
            rules_file: Path to rules YAML file
        """
        self.rules_file = rules_file
        self.rules: Dict[str, Any] = {}
        self.load_rules()

    def load_rules(self) -> None:
        """Load rules from YAML file."""
        try:
            rules_path = Path(self.rules_file)
            if not rules_path.exists():
                logger.warning(
                    f"Rules file {self.rules_file} not found, using defaults"
                )
                self.rules = self._get_default_rules()
                return

            with open(rules_path, "r", encoding="utf-8") as f:
                self.rules = yaml.safe_load(f) or {}

            logger.info(f"Loaded rules from {self.rules_file}")

        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            self.rules = self._get_default_rules()

    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default rules if file is not available."""
        return {
            "general": {"app_name": "AI Auditor", "version": "1.0.0", "language": "pl"},
            "tolerances": {
                "amount": {
                    "max_difference": 0.01,
                    "percentage_tolerance": 0.1,
                    "min_amount": 1.0,
                    "max_amount": 1000000.0,
                },
                "date": {
                    "max_days_difference": 1,
                    "weekend_tolerance": True,
                    "holiday_tolerance": True,
                },
            },
            "invoice_rules": {
                "duplicate_numbers": {"enabled": True, "severity": "high"}
            },
        }

    def get_rule(self, path: str, default: Any = None) -> Any:
        """
        Get rule value by dot-separated path.

        Args:
            path: Dot-separated path to rule (e.g., 'tolerances.amount.max_difference')
            default: Default value if rule not found

        Returns:
            Rule value or default
        """
        try:
            keys = path.split(".")
            value = self.rules

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default

            return value

        except Exception as e:
            logger.error(f"Error getting rule {path}: {e}")
            return default

    def get_tolerance(self, category: str, field: str, default: Any = None) -> Any:
        """
        Get tolerance value for specific category and field.

        Args:
            category: Tolerance category (e.g., 'amount', 'date')
            field: Field name (e.g., 'max_difference')
            default: Default value if not found

        Returns:
            Tolerance value or default
        """
        return self.get_rule(f"tolerances.{category}.{field}", default)

    def get_invoice_rule(
        self, rule_name: str, field: str = None, default: Any = None
    ) -> Any:
        """
        Get invoice rule value.

        Args:
            rule_name: Rule name (e.g., 'duplicate_numbers')
            field: Field name (e.g., 'enabled', 'severity')
            default: Default value if not found

        Returns:
            Rule value or default
        """
        if field:
            return self.get_rule(f"invoice_rules.{rule_name}.{field}", default)
        else:
            return self.get_rule(f"invoice_rules.{rule_name}", default)

    def get_ksef_rule(
        self, rule_name: str, field: str = None, default: Any = None
    ) -> Any:
        """
        Get KSeF rule value.

        Args:
            rule_name: Rule name (e.g., 'uuid_check')
            field: Field name (e.g., 'enabled', 'severity')
            default: Default value if not found

        Returns:
            Rule value or default
        """
        if field:
            return self.get_rule(f"ksef_rules.{rule_name}.{field}", default)
        else:
            return self.get_rule(f"ksef_rules.{rule_name}", default)

    def get_contractor_rule(
        self, rule_name: str, field: str = None, default: Any = None
    ) -> Any:
        """
        Get contractor rule value.

        Args:
            rule_name: Rule name (e.g., 'nip_validation')
            field: Field name (e.g., 'enabled', 'severity')
            default: Default value if not found

        Returns:
            Rule value or default
        """
        if field:
            return self.get_rule(f"contractor_rules.{rule_name}.{field}", default)
        else:
            return self.get_rule(f"contractor_rules.{rule_name}", default)

    def is_rule_enabled(self, rule_path: str) -> bool:
        """
        Check if rule is enabled.

        Args:
            rule_path: Dot-separated path to rule

        Returns:
            True if rule is enabled, False otherwise
        """
        return self.get_rule(f"{rule_path}.enabled", False)

    def get_rule_severity(self, rule_path: str) -> str:
        """
        Get rule severity.

        Args:
            rule_path: Dot-separated path to rule

        Returns:
            Severity level (low, medium, high, critical)
        """
        return self.get_rule(f"{rule_path}.severity", "medium")

    def get_rule_message(self, rule_path: str) -> str:
        """
        Get rule message.

        Args:
            rule_path: Dot-separated path to rule

        Returns:
            Rule message
        """
        return self.get_rule(f"{rule_path}.message", "Rule violation detected")

    def reload_rules(self) -> None:
        """Reload rules from file."""
        self.load_rules()

    def get_all_rules(self) -> Dict[str, Any]:
        """
        Get all rules.

        Returns:
            Dictionary with all rules
        """
        return self.rules.copy()

    def update_rule(self, path: str, value: Any) -> None:
        """
        Update rule value.

        Args:
            path: Dot-separated path to rule
            value: New value
        """
        try:
            keys = path.split(".")
            current = self.rules

            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            current[keys[-1]] = value
            logger.info(f"Updated rule {path} = {value}")

        except Exception as e:
            logger.error(f"Error updating rule {path}: {e}")

    def save_rules(self) -> None:
        """Save rules to YAML file."""
        try:
            with open(self.rules_file, "w", encoding="utf-8") as f:
                yaml.dump(self.rules, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved rules to {self.rules_file}")

        except Exception as e:
            logger.error(f"Error saving rules: {e}")


# Global rules instance
_rules_loader: Optional[RulesLoader] = None


def get_rules() -> RulesLoader:
    """
    Get global rules loader instance.

    Returns:
        RulesLoader instance
    """
    global _rules_loader
    if _rules_loader is None:
        _rules_loader = RulesLoader()
    return _rules_loader


def reload_rules() -> None:
    """Reload global rules."""
    global _rules_loader
    if _rules_loader is not None:
        _rules_loader.reload_rules()


def get_rule(path: str, default: Any = None) -> Any:
    """
    Get rule value using global rules loader.

    Args:
        path: Dot-separated path to rule
        default: Default value if not found

    Returns:
        Rule value or default
    """
    return get_rules().get_rule(path, default)


def is_rule_enabled(rule_path: str) -> bool:
    """
    Check if rule is enabled using global rules loader.

    Args:
        rule_path: Dot-separated path to rule

    Returns:
        True if rule is enabled, False otherwise
    """
    return get_rules().is_rule_enabled(rule_path)

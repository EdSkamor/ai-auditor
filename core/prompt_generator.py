"""
Unified prompt generation system for AI Auditor.
Handles MCP templates and prompt filling.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from .exceptions import FileProcessingError, ConfigurationError

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Handles prompt generation from MCP templates."""
    
    def __init__(self, mcp_dir: Optional[Path] = None):
        self.mcp_dir = mcp_dir or (Path(__file__).parent.parent / "inference" / "mcp")
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all MCP templates from the directory."""
        if not self.mcp_dir.exists():
            logger.warning(f"MCP directory not found: {self.mcp_dir}")
            return
        
        for template_file in self.mcp_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                
                template_name = template_data.get("name", template_file.stem)
                self._templates[template_name] = template_data
                logger.debug(f"Loaded template: {template_name}")
                
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
    
    def get_template(self, name: str) -> Dict[str, Any]:
        """Get template by name."""
        if name not in self._templates:
            raise ConfigurationError(f"Template '{name}' not found")
        return self._templates[name]
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self._templates.keys())
    
    def fill_template(self, template_name: str, **substitutions) -> str:
        """Fill template with substitutions."""
        template = self.get_template(template_name)
        prompt_template = template.get("prompt_template", "")
        
        if not prompt_template:
            raise ConfigurationError(f"Template '{template_name}' has no prompt_template")
        
        # Replace all {{placeholder}} with values
        filled_prompt = prompt_template
        for key, value in substitutions.items():
            placeholder = f"{{{{{key}}}}}"
            filled_prompt = filled_prompt.replace(placeholder, str(value))
        
        # Check for unfilled placeholders
        import re
        unfilled = re.findall(r'\{\{([^}]+)\}\}', filled_prompt)
        if unfilled:
            logger.warning(f"Unfilled placeholders in template '{template_name}': {unfilled}")
        
        return filled_prompt
    
    def generate_prompt(self, template_file: str, data: Dict[str, Any]) -> str:
        """Generate prompt from template file (legacy method)."""
        template_path = Path(template_file)
        if not template_path.exists():
            raise FileProcessingError(f"Template file not found: {template_file}")
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_json = json.load(f)
            
            prompt_template = template_json.get("prompt_template", "")
            if not prompt_template:
                raise ConfigurationError(f"Template file has no prompt_template: {template_file}")
            
            # Replace placeholders
            filled_prompt = prompt_template
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                filled_prompt = filled_prompt.replace(placeholder, str(value))
            
            return filled_prompt
            
        except Exception as e:
            raise FileProcessingError(f"Failed to generate prompt from {template_file}: {e}")


# Global prompt generator instance
_prompt_generator: Optional[PromptGenerator] = None


def get_prompt_generator() -> PromptGenerator:
    """Get the global prompt generator instance."""
    global _prompt_generator
    if _prompt_generator is None:
        _prompt_generator = PromptGenerator()
    return _prompt_generator


def generate_prompt(template_file: str, data: Dict[str, Any]) -> str:
    """Convenience function to generate prompt from template file."""
    return get_prompt_generator().generate_prompt(template_file, data)


def fill_template(template_name: str, **substitutions) -> str:
    """Convenience function to fill template with substitutions."""
    return get_prompt_generator().fill_template(template_name, **substitutions)


def load_mcp(name: str) -> Dict[str, Any]:
    """Convenience function to load MCP template (legacy method)."""
    return get_prompt_generator().get_template(name)


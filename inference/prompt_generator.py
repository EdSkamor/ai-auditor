import json
from pathlib import Path

def generate_prompt(template_file: str, data: dict) -> str:
    template_path = Path(template_file)
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_file} not found.")

    # Wczytaj plik JSON i pobierz pole "prompt"
    with open(template_path, "r", encoding="utf-8") as f:
        template_json = json.load(f)

    prompt = template_json.get("prompt", "")

    # Podmień wszystkie {{placeholdery}} na wartości z `data`
    for key, value in data.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)

    return prompt

if __name__ == "__main__":
    example_data = {
        "financial_data": "Zestawienie roczne firmy X",
        "timestamp": "2025-08-01 14:00"
    }
    result = generate_prompt("inference/mcp/risk_detection.json", example_data)
    print(result)

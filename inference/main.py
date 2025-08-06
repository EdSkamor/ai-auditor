from prompt_generator import generate_prompt
from model import call_model
from pathlib import Path

if __name__ == "__main__":
    data = {
        "financial_data": "Zestawienie roczne firmy X",
        "timestamp": "2025-08-01 15:00"
    }

    # 1. Wygeneruj prompt
    prompt = generate_prompt("inference/mcp/risk_detection.json", data)

    # 2. Przekaż do modelu
    response = call_model(prompt)

    # 3. Zapisz wynik jako fragment raportu
    output_path = Path("outputs/report_fragment.txt")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(response)

    print(f"Zapisano fragment raportu do {output_path}")

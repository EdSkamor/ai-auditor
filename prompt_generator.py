import json, pathlib
from model_hf_interface import call_model

BASE = pathlib.Path(__file__).parent

def load_mcp(name):
    with open(BASE / "inference" / "mcp" / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)

def fill(t: str, **subs):
    for k, v in subs.items():
        t = t.replace("{{" + k + "}}", v)
    return t

def main():
    risk_in   = "Przychody spadły o 40% w Q2 przy rosnącym zadłużeniu z 30% do 65%."
    series_in = "[['2025-01', 100], ['2025-02', 120], ['2025-03', 75], ['2025-04', 80]]"

    risk_prompt  = fill(load_mcp("risk_detection")["prompt_template"], financial_data=risk_in)
    chart_prompt = fill(load_mcp("chart_generation")["prompt_template"], data_series=series_in)

    print("=== RISK PROMPT ===\n", risk_prompt)
    print("\n=== RISK OUTPUT ===\n", call_model(risk_prompt, max_new_tokens=180, temperature=0.2))
    print("\n=== CHART PROMPT ===\n", chart_prompt)
    print("\n=== CHART OUTPUT ===\n", call_model(chart_prompt, max_new_tokens=180, temperature=0.2))

if __name__ == "__main__":
    main()

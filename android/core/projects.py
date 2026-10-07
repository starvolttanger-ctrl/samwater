import json, os

DIR = os.path.join(os.path.expanduser("~"), "Documents", "SAMWATER_Projects")
os.makedirs(DIR, exist_ok=True)

def save(name, data):
    p = os.path.join(DIR, name + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return p

def load(name):
    with open(os.path.join(DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)

def list_all():
    return sorted(p[:-5] for p in os.listdir(DIR) if p.endswith(".json"))

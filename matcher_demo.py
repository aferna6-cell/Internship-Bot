import json
from pathlib import Path

def main():
    data = json.loads(Path("aidan_resume_with_prefs.json").read_text())

    prefs = data.get("preferences", {})
    locations = prefs.get("preferred_locations", [])
    roles = prefs.get("role_types", [])

    print("Name:", data.get("name"))
    print("Preferred locations:", locations)
    print("Preferred roles:", roles)

if __name__ == "__main__":
    main()

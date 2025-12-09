import json

nb_path = "notebooks/01_quickstart_basic_usage.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for cell in data["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            if 'assert promethium.__version__ ==' in line:
                line = line.replace('"1.0.0"', '"1.0.4"').replace('"1.0.2"', '"1.0.4"')
            new_source.append(line)
        cell["source"] = new_source

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1)

print(f"Fixed {nb_path}")

import toml
from tasi._version import get_versions

# Lade die aktuelle Version
version = get_versions()['version']

# Lese pyproject.toml ein
with open("pyproject.toml", "r") as f:
    pyproject = toml.load(f)

# Ersetze die Version
pyproject["tool"]["poetry"]["version"] = version

# Schreibe die geänderte Version zurück in pyproject.toml
with open("pyproject.toml", "w") as f:
    toml.dump(pyproject, f)

print(f"Updated pyproject.toml to version {version}")

import json
from pathlib import Path


def get_scanner_parameters():
    with open(Path(__file__).parents[0] / "metadata.json") as scanner_data:
        data = json.load(scanner_data)
    return data.get('scanner_params')

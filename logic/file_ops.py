import json
import os


def save_json(file_path, data):
    # create folders if not exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_json(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return json.load(f)
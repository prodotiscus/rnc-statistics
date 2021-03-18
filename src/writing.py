import json
import os
from default import fkw
from random import randrange
from typing import Any, Dict, List, Tuple


def make_id() -> int:
    return randrange(10**5, 10**10)


def get_metadata(res_path: str, file_name: str) -> Dict[str, Any]:
    text = open(os.path.join(res_path, "queries", file_name, **fkw)).read()
    return json.loads(text)


def save_metadata(res_path: str, file_name: str, data: Dict[str, Any]) -> None:
    with open(os.path.join(res_path, "queries", file_name, **fkw)) as qq:
        qq.write(json.dumps(data))
        qq.close()


def append_to_data(res_path: str, file_id: int, matches: List[Tuple[str, str, str]]):
    path = os.path.join(res_path, "data", f"{file_id}.json")
    if not os.path.exists(path):
        with open(path, "w", **fkw) as new_data_file:
            new_data_file.write(json.dumps({
                "matches": matches
            }))
            new_data_file.close()
    else:
        with open(path, "w", **fkw) as existing_data_file:
            decoded = json.loads(existing_data_file.read())
            decoded["matches"] += matches
            existing_data_file.write(json.dumps(decoded))
            existing_data_file.close()


def get_data(res_path: str, file_id: int) -> List[Tuple[str, str, str]]:
    path = os.path.join(res_path, "data", f"{file_id}.json")
    return json.loads(open(path, **fkw).read())["matches"]

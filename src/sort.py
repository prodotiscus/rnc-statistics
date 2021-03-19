import os
import json
from typing import Callable, Iterable
from default import fkw
from random import randrange


def sort_data(res_path: str,
            file_id: int,
            sort_func: Callable[[Iterable[int]], Iterable[int]],
            sorting_name: str) -> int:
    prefs = json.loads(
            open(os.path.join(res_path, "preferences.json")).read())

    data = json.loads(open(os.path.join(res_path, "data", f"{file_id}.json"), **fkw).read())
    data_indices = range(len(data["matches"]))
    new_indices = sort_func(data_indices)
    ext_id = randrange(10**5, 10**10)

    with open(os.path.join(res_path, "extractions", f"{ext_id}.json")) as new_ext:
        new_ext.write(json.dumps({
            "name": sorting_name,
            "refers_to_data": file_id,
            "index_sequence": new_indices,
            "checked_indices": [],
            "now_item_of_sequence": 0,
            "items_per_page": prefs["items_per_page"]
        }))

    return ext_id

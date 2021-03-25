import json
import os
from default import fkw
from typing import List, Tuple
from writing import get_metadata


def open_extraction(res_path: str, extraction_id: int, offset=0, limit=10) -> List[Tuple[str,str,str]]:
    e_path = os.path.join(res_path, "extractions", f"{extraction_id}.json")
    extraction = json.loads(open(e_path, **fkw).read())
    d_file = extraction["refers_to_data"]
    seq = extraction["index_sequence"]
    ckd = extraction["checked_indices"]
    now = extraction["now_item_of_sequence"]
    data_path = os.path.join(res_path, "data", f"{d_file}.json")
    data = json.loads(open(data_path, **fkw).read())
    for index in range(offset, limit):
        if index >= len(seq):
            break
        yield {
            "checked": index in ckd,
            "j": index,
            "k": index-offset,
            "item": data["matches"][seq[index]]
        }


def extraction_meta(res_path: str, extraction_id: int, items_per_page: int=10):
    e_path = os.path.join(res_path, "extractions", f"{extraction_id}.json")
    extraction = json.loads(open(e_path, **fkw).read())
    return {
        "refers_to": extraction["refers_to_data"],
        "sequence": extraction["index_sequence"],
        "selected": extraction["checked_indices"],
        "now_on": extraction["now_item_of_sequence"],
        "number_all": len(extraction["index_sequence"]),
        "number_checked": len(extraction["checked_indices"])
    }


def mark_as_stop(res_path: str, extraction_id: int,
    query_name: str, nav_index: int, items_per_page: int=10):
    e_path = os.path.join(res_path, "extractions", f"{extraction_id}.json")
    extraction = json.loads(open(e_path, **fkw).read())
    processed = nav_index*items_per_page
    metadata = get_metadata(res_path, query_name)
    if metadata["number_matches"] < processed:
        processed = metadata["number_matches"]

    extraction["now_item_of_sequence"] = processed-1
    with open(e_path, "w", **fkw) as saving_extraction:
        saving_extraction.write(json.dumps(extraction))
        saving_extraction.close()


def update_selection(res_path: str, extraction_id: int, global_index: int, sel_value: bool):
    e_path = os.path.join(res_path, "extractions", f"{extraction_id}.json")
    extraction = json.loads(open(e_path, **fkw).read())
    if not sel_value:
        while global_index in extraction["checked_indices"]:
            extraction["checked_indices"].remove(global_index)
    else:
        extraction["checked_indices"].append(global_index)
    with open(e_path, "w", **fkw) as updated_extraction:
        updated_extraction.write(json.dumps(extraction))
        updated_extraction.close()


def nav_number_to_lo(nav_number: int, num_indices: int, items_per_page: int) -> Tuple[int,int]:
    print(nav_number*items_per_page-items_per_page, nav_number*items_per_page)
    return nav_number*items_per_page-items_per_page, nav_number*items_per_page


def generate_navs(num_indices: int, now_on_item: int, items_per_page: int, nav_len: int) -> List[int]:
    if not nav_len % 2:
        raise ValueError("nav_len must be an odd integer!")
    left_navs = range(1, now_on_item//items_per_page+1)
    right_navs = range(now_on_item//items_per_page+1+1, len(num_indices)//items_per_page+1+1)
    left_navs = list(left_navs[-(nav_len-1)//2:])
    right_navs = list(right_navs[:(nav_len-1)//2])
    return left_navs + [now_on_item//items_per_page+1] + right_navs

import browse
import json
import os
import writing
from default import fkw
from difflib import SequenceMatcher
from itertools import groupby
from typing import Dict, List


res_path = os.path.join(os.path.dirname(__file__), "..", "res")

if not os.path.exists(res_path):
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res")


def strings_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def jsoned_text(obj_list: List[Dict[str, str]]) -> str:
    return "".join([item["text"] for item in obj_list])


HAMMING_COMPARISON_CONST: float = 0.9


def notation1_to_extraction(extraction_id: int, imported_filename: str, verbose: bool = False):
    imp_path = os.path.join(res_path, "imported", imported_filename)
    imp_file = json.loads(open(imp_path, **fkw).read())
    imp_data = imp_file["nk:datasetContent"]["items"]
    data_file = writing.get_data(
        res_path,
        browse.extraction_meta(res_path, extraction_id)["refers_to"]
    )
    indexed_data = [(e, x) for (e, x) in enumerate(data_file)]
    grouped_data = groupby(indexed_data, key=lambda i: i[1][0])
    for title, citations in grouped_data:
        for global_index, cite in citations:
            _, markup, text = cite
            texts = [
                jsoned_text(item["text"]) for item in imp_data if item["title"] == title]
            for imported_text in texts:
                if strings_similarity(text, imported_text) > HAMMING_COMPARISON_CONST:
                    if verbose:
                        print(f"Selecting {global_index} of extraction {extraction_id}")
                    browse.update_selection(res_path, extraction_id, global_index, True)
                    break
    return True


if __name__ == "__main__":
    importer = eval(input("Which importer to use? "))
    verbose = True
    extraction_id = int(input("Extraction ID: "))
    imported_filename = input("Name of the imported file: ")
    importer(extraction_id, imported_filename, verbose)

import browse
import json
import os
import rnc_agent
import rnc_loader
import webview
from default import fkw
from flask import Flask, render_template, jsonify, request, send_from_directory
from typing import Dict, Iterator, List
from writing import get_metadata, get_data, save_data

gui_path = os.path.join(os.path.dirname(__file__), "..", "gui")
res_path = os.path.join(os.path.dirname(__file__), "..", "res")

if not os.path.exists(gui_path):
    gui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui")
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res")

server = Flask(__name__, static_folder=gui_path, template_folder=gui_path)
server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1
prefs: Dict = json.loads(open(os.path.join(res_path, "preferences.json")).read())


def iter_query_objects() -> Iterator[Dict[str, str]]:
    queries_path = os.path.join(res_path, "queries")
    for object_name in os.listdir(queries_path):
        yield json.loads(open(os.path.join(queries_path, object_name), **fkw).read())


def list_query_objects() -> List[Dict[str, str]]:
    query_obj = []
    for q in iter_query_objects():
        print(q)
        q["extractions"] = []
        e_path = os.path.join(res_path, "extractions")
        exts = os.listdir(e_path)
        for ext_name in exts:
            ext_c = json.loads(open(os.path.join(e_path, ext_name), **fkw).read())
            if ext_c["refers_to_data"] == q["data_id"]:
                q["extractions"].append(int(ext_name.replace(".json", "")))
        query_obj.append(q)
    return query_obj


@server.route("/")
def main_page():
    return send_from_directory(gui_path, "main.html")


@server.route("/static/<filename>")
def response_static(filename):
    return send_from_directory(gui_path, filename)


@server.route("/load_query_objects")
def load_query_objects():
    return jsonify({"query_objects": list_query_objects()})


@server.route("/download_check_ten/<query_file>")
def download_check_ten(query_file):
    a = rnc_agent.Agent(res_path, f"{query_file}.json")
    query_meta = get_metadata(res_path, query_file)
    working_on = None

    for n in range(len(query_meta["query_strings"])):
        if n not in query_meta["query_strings_done"]:
            working_on = n
            break

    finished = False
    if working_on is not None:
        a.query_builder = rnc_loader.safe_select_builder(
            query_meta["use_builder"])
        try:
            result = a.load_more(working_on, 10)
        except StopIteration:
            finished = True
        # refresh meta-data
        query_meta = get_metadata(res_path, query_file)
    if working_on is not None and not finished:
        finished = working_on in query_meta["query_strings_done"]
    elif working_on is None:
        finished = True

    return jsonify({
        "all_matches": query_meta["number_matches"],
        "downloaded": len(get_data(res_path, query_meta["data_id"])),
        "finished": finished
    })


@server.route("/navs_for_extraction/<int:extraction_id>/<int:page_index>")
def navs_for(extraction_id: int, items_per_page: int = 10, page_index: int=1):
    em = browse.extraction_meta(res_path, extraction_id)
    num_indices = em["sequence"]
    now_on_item = page_index * items_per_page - 1
    nav_len = 11
    navs = browse.generate_navs(num_indices, now_on_item, items_per_page, nav_len)
    return jsonify({
        "navs": navs,
        "selected": page_index
    })


@server.route("/get_items/<int:extraction_id>/<int:nav_index>")
def get_items(extraction_id: int, nav_index: int):
    em = browse.extraction_meta(res_path, extraction_id)
    ipp = 10
    limit, offset = browse.nav_number_to_lo(nav_index, len(em["sequence"]), ipp)
    items = browse.open_extraction(res_path, extraction_id, limit, offset)
    return jsonify({
        "items": [x for x in items]
    })


@server.route("/change_selection/<int:extraction_id>/<int:g_index>/<command>")
def change_selection(extraction_id, g_index, command):
    sel_value: bool = (command == "select")
    em = browse.update_selection(res_path, extraction_id, g_index, sel_value)
    return jsonify({
        "result": "success"
    })

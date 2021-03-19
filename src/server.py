import json
import os
import webview
from default import fkw
from flask import Flask, render_template, jsonify, request, send_from_directory
from typing import Dict, Iterator, List

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
    return [query_obj for query_obj in iter_query_objects()]


@server.route("/")
def main_page():
    return send_from_directory(gui_path, "main.html")


@server.route("/static/<filename>")
def response_static(filename):
    return send_from_directory(gui_path, filename)


@server.route("/load_query_objects")
def load_query_objects():
    return jsonify({"query_objects": list_query_objects()})

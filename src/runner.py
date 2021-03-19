import json
import os
from server import server
import webview
from typing import Dict

res_path = os.path.join(os.path.dirname(__file__), "..", "res")
if not os.path.exists(res_path):
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res")

prefs: Dict = json.loads(open(os.path.join(res_path, "preferences.json")).read())


def open_window() -> None:
    window = webview.create_window(prefs["main_title"], server)
    webview.start(debug=True)


if __name__ == "__main__":
    open_window()

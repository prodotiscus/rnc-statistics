import browse
import os
import re
import writing

res_path = os.path.join(os.path.dirname(__file__), "..", "res")

if not os.path.exists(res_path):
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res")


def clean_to_notation1(html: str):
    html = re.sub(r'(<\/span>)(.+?)(<span)', r'\1!!special%%%\2!!\3', html)
    html = re.sub(r'<span class="(.+?)"\s?>(.+?)<\/span>', r'!!\1%%%\2!!', html)
    for item in html.split('!!'):
        percent_delim = item.split('%%%')
        if len(percent_delim) < 2:
            continue
        proto, text = percent_delim
        status = None
        if "g-em" in proto:
            status = "selected"
        elif "b-wrd-expl" in proto:
            status = "token"
        elif "special" in proto:
            status = "special"
        if status is None:
            raise ValueError
        yield {"status": status, "text": text}


def extraction_to_notation1(extraction_id: int, dataset_name: str):
    notation1_object = {
        "nk:datasetName": dataset_name,
        "nk:datasetContent": {
            "items": [],
            "processed": 0
        }
    }
    em = browse.extraction_meta(res_path, extraction_id)
    notation1_object["nk:datasetContent"]["processed"] = em["now_on_item"] + 1
    data = writing.get_data(res_path, em["refers_to_data"])
    for index in em["selected"]:
        title, clean_html, text = data["matches"][index]
        notation1_object["nk:datasetContent"]["items"].append({
            "title": title,
            "text": [x for x in clean_to_notation1(clean_html)]
        })
    return notation1_object

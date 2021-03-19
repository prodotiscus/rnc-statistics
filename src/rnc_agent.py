import json
import os
import requests
import rnc_parser as prs
from default import fkw
from random import randrange
from rnc_agent import CorpusQuery
from rnc_loader import QueryBuilder
from typing import List, Tuple, Union


class Agent:
    def __init__(self, res_path: str, query_name: str):
        self.res_path: str = res_path
        qf_path = os.path.join(res_path, "queries", query_name)
        q_file = json.loads(open(qf_path).read())
        self.q_file = q_file
        if q_file["data_id"] is None:
            q_file["data_id"] = randrange(10**5, 10**8)
            data_path = os.path.join(res_path, "data", f"{q_file['data_id']}.json")
            with open(data_path, "w", **fkw) as data_file:
                data_file.write(json.dumps({
                    "matches": []
                }))
                data_file.close()
        self.data_id: int = q_file["data_id"]
        self.data_list: List[Tuple[str, str, str]]
        self.query_builder: Union[QueryBuilder, None] = None

    def update_query_file(self, num_query: int):
        nq = str(num_query)
        if str(num_query) not in self.q_file["last_pages_by_query"]:
            self.q_file["last_page_by_query"] = 0
        self.rewrite_query_file()

    def rewrite_query_file(self) -> bool:
        with open(self.res_path, "w", **fkw) as query_file:
            query_file.write(json.dumps(self.q_file))
            query_file.close()
        return True

    def load_more(self, num_query: int, yet_more: int=10) -> List[Tuple[str,str,str]]:
        self.update_query_file(num_query)

        nq = str(num_query)
        query_string = self.q_file["query_strings"][nq]

        if self.query_builder is None:
            raise ValueError(".query_builder is not defined!")

        local_data: List[Tuple[str, str, str]] = []
        last_page = self.q_file["last_page_by_query"]
        builder = self.query_builder()
        for lexeme in CorpusQuery(query_string).to_lexeme_tuples():
            builder.add_lexeme(lexeme)

        for page in range(last_page, last_page + yet_more):
            loaded = self.load_page(builder.build_query())

            if num_query not in self.q_file["query_strings_started"]:
                self.q_file["number_documents"] += loaded["stats"]["documents"]
                self.q_file["number_matches"] += loaded["stats"]["matches"]
                self.q_file["query_strings_started"].append(num_query)
                self.rewrite_query_file()

            local_data += loaded["page_matches"]

            if loaded["is_last_page"]:
                break

        return local_data

    def load_page(self, url: str):
        r = requests.get(url)
        raw_html: str = r.text

        return {
            "stats": prs.parse_search_stats(raw_html),
            "page_matches": prs.parse_listed_matches(raw_html),
            "is_last_page": prs.is_last_page(raw_html)
        }

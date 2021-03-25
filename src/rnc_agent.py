import json
import os
import requests
import rnc_parser as prs
from default import fkw
from parse_query import CorpusQuery
from random import randrange
from rnc_loader import QueryBuilder
from time import sleep
from typing import Dict, List, Tuple, Union

import logging
logging.basicConfig(level=logging.DEBUG)


class Agent:
    def __init__(self, res_path: str, query_name: str):
        self.res_path: str = res_path
        qf_path = os.path.join(res_path, "queries", query_name)
        self.qf_path = qf_path
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
            self.rewrite_query_file()
        self.data_id: int = q_file["data_id"]
        self.data_list: List[Tuple[str, str, str]] = []
        self.query_builder: Union[QueryBuilder, None] = None

    def update_query_file(self, num_query: int):
        nq = str(num_query)
        if nq not in self.q_file["last_pages_by_query"]:
            self.q_file["last_pages_by_query"][nq] = -1
        self.rewrite_query_file()

    def rewrite_query_file(self) -> bool:
        with open(self.qf_path, "w", **fkw) as query_file:
            query_file.write(
                json.dumps(self.q_file, indent=2))
            query_file.close()
        return True

    def update_data_file(self, appended_data: List[Tuple[str,str,str]]):
        df_path = os.path.join(self.res_path, "data", f"{self.data_id}.json")
        old = json.loads(open(df_path, **fkw).read())
        with open(df_path, "w", **fkw) as df:
            old["matches"] += appended_data
            df.write(json.dumps(old))
            df.close()
        return True

    def load_more(self, num_query: int, yet_more: int=10) -> List[Tuple[str,str,str]]:
        self.update_query_file(num_query)

        if num_query in self.q_file["query_strings_done"]:
            raise StopIteration

        nq = str(num_query)
        query_string = self.q_file["query_strings"][num_query]

        if self.query_builder is None:
            raise ValueError(".query_builder is not defined!")

        local_data: List[Tuple[str, str, str]] = []
        last_page = self.q_file["last_pages_by_query"][nq]
        builder = self.query_builder()
        for lexeme in CorpusQuery(query_string).to_lexeme_tuples():
            print(lexeme)
            builder.add_lexeme(lexeme)
        builder.current_page = last_page + 1

        for _ in range(last_page, last_page + yet_more):
            break_loop: bool = False
            for n in range(3): # triple-check before finishing the query
                loaded = self.load_page(builder.build_query())

                if num_query not in self.q_file["query_strings_started"]:
                    self.q_file["number_documents"] += loaded["stats"]["documents"]
                    self.q_file["number_matches"] += loaded["stats"]["matches"]
                    self.q_file["query_strings_started"].append(num_query)
                    self.rewrite_query_file()

                local_data += loaded["page_matches"]

                self.q_file["last_pages_by_query"][str(num_query)] = builder.current_page

                if loaded["is_last_page"] and n > 1:
                    self.q_file["query_strings_done"].append(num_query)
                    self.rewrite_query_file()
                    break_loop = True
                    break
                elif not loaded["is_last_page"]:
                    builder.next_page()
                    break

            if break_loop:
                break
        self.rewrite_query_file()
        self.update_data_file(local_data)

        return local_data

    def load_page(self, url: str):
        r, times = self.handled_get_request(url, 1)

        if prs.is_last_page(r.text):
            while times < 3 and prs.is_last_page(r.text):
                r, times = self.handled_get_request(url, times, -2)
                times += 1

        return {
            "stats": prs.parse_search_stats(r.text),
            "page_matches": prs.parse_listed_matches(r.text),
            "is_last_page": prs.is_last_page(r.text)
        }

    @staticmethod
    def handled_get_request(url: str, times: int, status_code: int=-1):
        ua_header_dict: Dict[str, str] = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        while status_code != 200:
            if status_code != -1:
                sleep(30)
            r = requests.get(url, headers=ua_header_dict)
            if r.status_code == 200:
                return r, times
            status_code = r.status_code

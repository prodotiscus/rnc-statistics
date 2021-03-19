import re
from typing import Iterator, List, Union
from rnc_loader import lexeme


class CorpusQuery:
    def __init__(self, query):
        self.parser = re.compile(r'''
        (?P<class> \[|{) # token or a distance pattern?
        (?P<content>
            (?P<type>lex|add|gr):(?P<properties>[^\]]+)\] # if it's a token, then lex/add/gr?
            | (?P<limits>[\d,_]+)\} # if it's a d pattern, what are the limits?
        )''', re.X)
        self.class_token = "["
        self.class_distance = "{"
        self.query = query

    def decode(self):
        result = [{"class": "token"}]
        for item in self.parser.finditer(self.query):
            if item.group("class") == self.class_token:
                result[-1][item.group("type")] = item.group("properties").split(",")
            elif item.group("class") == self.class_distance:
                result.append({
                    "class": "distance",
                    "limits": item.group("limits").split(",")
                })
                result.append({"class": "token"})
        return result

    def to_lexeme_tuples(self) -> Iterator[lexeme]:
        decoded = self.decode()
        for k, item in enumerate(decoded):
            passing = []
            if item["class"] == "token":
                for attr in ["lex", "gr", "add", "sem"]:
                    passing.append(item[attr] if attr in item else None)
                lmt: List[Union[int,str,None]] = [None, None]
                if k < len(decoded)-1 and decoded[k+1]["class"] == "distance":
                    lmt = decoded[k+1]["limits"]
                if lmt[0] is None:
                    lmt[0] = 1
                if len(lmt) == 1:
                    lmt.append(lmt[0])
                elif lmt[1] is None:
                    lmt[1] = lmt[0]
                passing += lmt
                yield lexeme(*passing)
            else:
                continue

from collections import namedtuple
from typing import Union

lexeme = namedtuple(
    "lexeme",
    "word gram flags sem dist1 dist2",
    defaults=(None,) * 6
)


class QueryBuilder:
    def __init__(self):
        self.start: str = "https://processing.ruscorpora.ru/search.xml?"
        self.default_parameters: str = "env=alpha&api=1.0&mycorp=&mysent=&mysize=&mysentsize=&dpp=&spp=&spd=&mydocsize="
        self.subcorpus_parameters: Union[str, None] = None
        self.current_lexeme: int = 1
        self.number_lexemes: int = 0
        self.final_url: str = ""
        self.lexemes_part: Union[str, None] = None
        self.current_page: int = 0
        self.stop_on_page: Union[int, None] = None

    def build_subcorpus_start(self) -> str:
        if self.subcorpus_parameters is None:
            raise ValueError
        return self.start + self.default_parameters + self.subcorpus_parameters

    def build_end(self) -> str:
        return f"&p={self.current_page}"

    def next_page(self) -> None:
        if self.stop_on_page is not None and self.current_page == self.stop_on_page:
            raise StopIteration
        self.current_page += 1

    def build_lexeme_start(self, lexeme: lexeme) -> str:
        return ""

    def build_lexeme_params(self, lexeme: lexeme) -> str:
        return ""

    def add_lexeme(self, lexeme: lexeme) -> None:
        if self.lexemes_part is None:
            self.lexemes_part = ""
        self.lexemes_part += self.build_lexeme_start(lexeme) + self.build_lexeme_params(lexeme)

    def build_query(self) -> str:
        if self.lexemes_part is None:
            raise ValueError
        self.final_url = self.build_subcorpus_start() + self.lexemes_part + self.build_end()
        return self.final_url


class MainCorpusLexGram(QueryBuilder):
    def __init__(self):
        super().__init__()
        self.subcorpus_parameters = "&dpp=&spp=&spd=&mydocsize=&mode=main&lang=ru&sort=i_grtagging&nodia=1&text=lexgramm"

    def build_lexeme_start(self, lexeme: lexeme) -> str:
        n = self.number_lexemes + 1
        return f"&parent{n}=0&level{n}=0"

    def build_lexeme_params(self, lexeme: lexeme) -> str:
        n = self.number_lexemes + 1
        lex_n = lexeme.word if lexeme.word else ""
        gramm_n = lexeme.gram if lexeme.gram else ""
        sem_n = lexeme.sem if lexeme.sem else ""
        flags_n = lexeme.flags if lexeme.flags else ""
        sem_mod_n = "sem"
        if lexeme.dist1 is None or lexeme.dist2 is None:
            raise ValueError
        return f"&lex{n}={lex_n}&gramm{n}={gramm_n}" +\
        f"&sem{n}={sem_n}&flags{n}={flags_n}&sem-mod{n}={sem_mod_n}" +\
        f"&min{n+1}={lexeme.dist1}&max{n+1}={lexeme.dist2}"

    def add_lexeme(self, lexeme: lexeme) -> None:
        super().add_lexeme(lexeme)
        self.number_lexemes += 1

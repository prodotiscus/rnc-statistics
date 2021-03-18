import lxml.html
import re
from typing import Dict, Iterator, Tuple


def parse_search_stats(raw_html: str) -> Dict[str, int]:
    model = lxml.html.fromstring(raw_html)
    stat_blocks = model.xpath("//*[@class='stat-number']/..")
    local_search = 1
    d, m = stat_blocks[local_search].xpath("./*[@class='stat-number']")
    return {
        "documents": int(d.text.replace(" ", "")),
        "matches": int(m.text.replace(" ", ""))
    }


def parse_listed_matches(raw_html: str) -> Iterator[Tuple[str, str, str]]:
    model = lxml.html.fromstring(raw_html)
    titled_matches = model.xpath("//ol/li")
    for match in titled_matches:
        title = match.xpath("./*[@class='b-doc-expl']")[0].text
        title = re.sub(r'^\s+|\s+$', '', title)
        end_clear = re.compile(r'\s+\[[^\]]+\]\s+\[[^\]]+\]\s+←…→\s*$')
        submatches = match.xpath("./table//td/ul/li")
        for submatch in submatches:
            text = submatch.xpath('string(.)')
            text = re.sub(end_clear, "", text)
            text = re.sub(r'\s+', ' ', text)
            yield (
                title,
                clear_match_html(lxml.etree.tostring(submatch, encoding="unicode")),
                text
            )


def clear_match_html(text: str) -> str:
    text = re.sub(r'<!--.*?>|explain=".*?"|<a href="\/search.xml.*?">.*?<\/a>', '', text)
    text = re.sub(r'\s{2,}|^\s+', '', text)
    return text

"""
Helper functions for dealing with wiki syntax as well as format
output posts triggered by :class:`.action.WikiLink`
"""
from dataclasses import dataclass
import wikitextparser as wtp

@dataclass
class WikiPage:
    title:str
    source:str
    content:wtp.WikiText

    @classmethod
    def from_source(self, title, source) -> 'WikiPage':
        content = wtp.parse(source)
        return WikiPage(title, source, content)
"""
Actions triggered by inline text content
"""
from typing import List, Optional
from wiki_postbot.actions import Action

class Inline(Action):
    """
    An action triggered by the content of a tweet
    """

class WikiLink(Inline):
    """
    Detect a wikilink and add it to the wiki!
    """

    def __init__(self, **kwargs):
        super(WikiLink, self).__init__(**kwargs)

        self.wikilinks = None # type: Optional[List[str]]

    def check(self, response: Response) -> bool:
        """
        Check if the condition of this action is met
        """
        wikilinks = self.pattern.findall(response.data.text)
        if len(wikilinks)>0:
            return Result(ok=True, log=f"Found wikilinks: {wikilinks}")
        else:
            return Result(ok=False, log="No wikilinks found")



    def do(self, response: Response) -> Result:
        """
        """

        # @abstractmethod




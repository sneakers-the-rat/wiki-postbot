"""
Actions triggered by inline text content
"""
from typing import List, Optional
from wiki_postbot.actions import Action, Result
from wiki_postbot.patterns import WIKILINK
from tweepy import Response

class Inline(Action):
    """
    An action triggered by the content of a message.

    Inline actions are within a message that is not exclusively intended for the bot,
    as opposed to :class:`.Command` actions which need to be their own message.
    """

class WikiLink(Inline):
    """
    Detect a wikilink and add it to the wiki!

    .. note:

        These commands will not include the full text of messages from users that have not opted in to the bot,
        (typically by following it) but will only archive a link.
    """
    pattern = WIKILINK

    def __init__(self, **kwargs):
        super(WikiLink, self).__init__(**kwargs)

        self.wikilinks = None # type: Optional[List[str]]

    def check(self, response: Response) -> bool:
        """
        Check if the condition of this action is met
        """
        wikilinks = self.pattern.findall(response.data.text)
        if len(wikilinks)>0:
            return True
        else:
            return False

    def do(self, response: Response) -> Result:
        """
        """

        # @abstractmethod




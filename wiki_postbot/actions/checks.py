from wiki_postbot.actions.action import Action, Result
from wiki_postbot.patterns.wikilink import WIKILINK
from tweepy import Response
import re

class Check(Action):
    """
    Base class for actions that check something about the tagged message
    to see if we should handle it.
    """


class Mentioned(Check):
    """
    Check that we have been directly mentioned in the message
    """

    def do(self, response:Response) -> Result:
        mentioned_users = [u['username'] == self.bot.username for u in response.data.entities.get('mentions', [])]
        result = Result(ok=any(mentioned_users))
        if not result.ok:
            result.log = "Mentioned, but not directly mentioned"

        return result

class Wikilink(Check):
    """
    Check if a post contains a wikilink
    """
    pattern = WIKILINK
    """
    stolen from the agora bot
    https://github.com/flancian/agora-bridge/blob/9cfe0a41e55bba4f628875ecf0c8fefd3ad509fd/bots/twitter/agora-bot.py#L48
    """

    def do(self, response:Response) -> Result:
        wikilinks = self.pattern.findall(response.data.text)
        if len(wikilinks)>0:
            return Result(ok=True, log=f"Found wikilinks: {wikilinks}")
        else:
            return Result(ok=False, log="No wikilinks found")



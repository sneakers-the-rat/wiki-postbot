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

    This action uses an extended wikilink syntax that includes

    * **n-back links** - allows the user to specify messages in threads that are not the initiating message, and
    * **Semantic wikilinks** - specify a triplet subject-predicate-object link

    In each of the following examples, `LINK` is a placeholder for the text of the wikilink to be made.

    # N-Back Links

    For all of these, whitespace in-between the n-back specifier and the link text will be ignored. So
    `[[^LINK]]` and `[[^ LINK]]` are both valid.

    * **Preceding Message** - `[[^LINK]]`
    * **Entire Preceding Thread** - `[[^*LINK]]`
    * **Ranges**
    ** **Fully specified** - `[[^{n,m}LINK]]` where `n` and `m` are the start and end of the range to be included, inclusive.
       eg. `[[^{2,5}LINK]]` would specify four messages: the 2nd one above the initiating message through the 5th, and
       `n == 0` indicates the initiating message.
    ** **End specified** - `[[^{,m}LINK]]` OR `[[^{m}LINK]]` - include the initiating message and the `m` messages above it.
    ** **Start specified** - `[[^{n,}LINK]]` - include all preceding messages in the thread before the `nth` message

    # Semantic Wikilinks

    Semantic wikilinks create a subject, predicate, object triplet. The subject will be the page that the

    Semantic wikilinks use `::` as a delimiter between terms, and a `::` indicates that a wikilink is semantic.

    `SUB`, `PRED`, and `OBJ` are placeholders for the parts of
    a triplet in the following examples.

    * **Complete Triplet** - `[[SUB::PRED::OBJ]]` - create a semantic wikilink on the `SUB`ject page that links to the
      `OBJ`ect page with the indicated predicate.

      eg. `[[Paper::Has DOI::https://doi.org/10.xxx/yyyy]]`

    * **Implicit Triplet** - `[[PRED::OBJ]]` after a `[[SUB]]` wikilink has been previously used in the message or thread.
      A subject can also be declared with a complete triplet.

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




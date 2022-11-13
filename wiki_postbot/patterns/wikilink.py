import re
from wiki_postbot.patterns.patterns import Pattern
from dataclasses import dataclass
from typing import Optional, Union, List
import pyparsing as pp
from pprint import pformat


WIKILINK = re.compile(r'\[\[(.*?)\]\]', re.IGNORECASE)
"""
Basic structure of wikilink, used to detect presence
"""

class NBack:
    FIELDS = ('wildcard', 'start', 'end')

    def __init__(self, start:Optional[int]=None, end:Optional[int]=None,
                 wildcard:Optional[Union[str,bool]]=None,
                 one:Optional[str]=None):

        if wildcard:
            self.wildcard = True
            self.start = None
            self.end = None
            return
        else:
            self.wildcard = False

        if one:
            self.start = 1
            self.end = 1
        else:
            if start is not None:
                start = int(start)
            if end is not None:
                end = int(end)
            self.start = start
            self.end = end

        if self.start is not None and self.end is not None:
            if self.start > self.end:
                raise ValueError(f"Start value must be less than end value, got start:{self.start}, end:{self.end}")

    @classmethod
    def make_parser(cls) -> pp.ParserElement:
        # --------------------------------------------------
        # n-back links immediately follow the [[ and can be one of
        # ^
        # ^*
        # ^{n,m}
        # ^{n,}
        # ^{,m}
        # ^{m}

        # make elements
        caret = pp.Literal("^")
        lcurly = pp.Literal('{').suppress()
        rcurly = pp.Literal('}').suppress()
        integer = pp.Word(pp.nums)
        comma = pp.Literal(',').suppress()
        nb_range = caret + lcurly

        # combine into matches
        nb_wildcard = caret.suppress() + "*"
        nb_wildcard.set_name("NBack - Wildcard")
        # start or end can be omitted if comma is present
        nb_full = nb_range + pp.Optional(integer("start")) + comma + pp.Optional(integer("end")) + rcurly
        nb_full.set_name("NBack - Fully Specified")
        # if no comma present, it's just an end
        nb_end = nb_range + integer("end") + rcurly
        nb_end.set_name("NBack - End Specified")

        # combine into full nback parser
        nback = pp.Group(nb_wildcard('wildcard') | nb_full | nb_end | caret("one")).set_results_name("nback")
        nback.set_name("NBack Prefix")
        return nback

    def __eq__(self, other:'NBack'):
        return all([getattr(self, f) == getattr(other, f) for f in self.FIELDS])

    def __repr__(self) -> str:
        return pformat({f:getattr(self, f) for f in self.FIELDS})

class Wikilink(Pattern):
    """
    Pattern for detecting wikilinks!

    This pattern implements an extended wikilink syntax that includes

    * **n-back links** - allows the user to specify messages in threads that are not the initiating message, and
    * **Semantic wikilinks** - specify a triplet subject-predicate-object link

    In each of the following examples, `LINK` is a placeholder for the text of the wikilink to be made.

    # N-Back Links (see :class:`.NBack`)

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
    """
    FIELDS = ('link', 'nback', 'predicate', 'object', 'section')

    def __init__(
            self,
            link: Optional[str] = None,
            nback: Optional[Union[NBack, tuple, dict]] = None,
            predicate: Optional[str] = None,
            object: Optional[str] = None,
            section: Optional[str] = None,
            **kwargs):
        super(Wikilink, self).__init__(**kwargs)

        self.link = link
        if isinstance(nback, (tuple, list)):
            nback = NBack(*nback)
        elif isinstance(nback, dict):
            nback = NBack(**nback)
        elif isinstance(nback, pp.ParseResults):
            nback = NBack(**dict(nback))

        if isinstance(section, pp.ParseResults):
            section = section[0]

        self.nback = nback
        self.predicate = predicate
        self.object = object
        self.section = section

    @classmethod
    def make_parser(cls) -> pp.ParserElement:
        """
        Make the parser to detect wikilinks!
        """
        # All wikilinks start with [[ and end with ]]
        lbracket = pp.Literal('[[').suppress()
        rbracket = pp.Literal(']]').suppress()

        #nback parser
        nback = NBack.make_parser()

        # main wikilink subject text
        #link = pp.Word(pp.printables+ " ", excludeChars="#[]{}|:") + pp.Optional(pp.Literal(':')) + pp.Optional(pp.Word(pp.printables+ " ", excludeChars="#[]{}|:"))
        # allow single, but not double colons
        # "Look for a printable character and an optional colon that isn't a double colon,
        # combine those. Then look for one or more instances of that, and combine that."
        link = pp.Combine(
            pp.OneOrMore(
                pp.Combine(
                    pp.Word(pp.printables+ " ", excludeChars="#[]{}|:").set_name("Link Body") + \
                    pp.Optional(
                        pp.Literal(':')+ ~pp.Literal(':')
                    ).set_name('Single Colon')
                )
            )
        )
        link.set_name("Wikilink - Body")


        # optional page section
        hash = pp.Literal("#").suppress()
        section = hash + link
        section.set_name("Section")

        # combined they make a fully qualified link#section link
        link_full = link("link") + pp.Optional(section("section"))
        link_full.set_name("Wikilink - Full")

        #### SMW
        # Predicate::Object with implicit subject
        smw_delimiter = pp.Literal('::').suppress()
        implicit_semantic = link("predicate") + smw_delimiter + link("object")

        # or
        # Link::Predicate::Object with explicit subject
        explicit_semantic = link_full + smw_delimiter + implicit_semantic

        ### Combine link bodies
        # optionally matching depending on the form
        link_bodies = explicit_semantic.set_name('Explicit Semantic Link') | implicit_semantic.set_name('Implicit Semantic Link') | link_full
        # link_bodies = implicit_semantic

        # Combine all
        #parser = lbracket + pp.Optional(nback) + link_full + rbracket
        parser = lbracket + pp.Optional(nback) + link_bodies + rbracket
        parser.set_name('Wikilink Parser')
        return parser

    @classmethod
    def parse(cls, string:str, return_parsed:bool=False) -> List['Wikilink']:
        parser = cls.make_parser()
        results = parser.search_string(string)
        if return_parsed:
            return results
        else:
            return [Wikilink(**dict(res.items())) for res in results]

    def __eq__(self, other:'Wikilink'):
        return all(getattr(self, f) == getattr(other, f) for f in self.FIELDS)

    def __repr__(self) -> str:
        return pformat({f:getattr(self, f) for f in self.FIELDS if getattr(self, f) is not None})




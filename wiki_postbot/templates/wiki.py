"""
Templates for representing different kinds of messages on mediawiki
"""

from wiki_postbot.formats.wiki import WikiPage
from abc import abstractmethod
from discord.message import Message

class WikiTemplate(WikiPage):

    @abstractmethod
    def format_discord(self, msg:Message) -> str:
        """
        Format a discord message into a template string
        """

class TemplateMessage(WikiTemplate):

    @classmethod
    def format_discord(self, msg:Message) -> str:
        return (
            "{{Message\n"
            f"|Author={msg.author.name}\n"
            f"|Avatar={msg.author.avatar.url}\n"
            f"|Date Sent={msg.created_at.strftime('%y-%m-%d %H:%M:%S')}\n"
            f"|Channel={msg.channel}\n"
            f"|Text={msg.content}\n"
            f"|Link={msg.jump_url}\n"
            "}}"
            )



template_message = TemplateMessage.from_source(
    title="Template:Message",
    source="""<noinclude>
<pre>
{{Message
|Author=
|Avatar=
|Date Sent=
|Channel=(Optional)
|Text=
|Link=
}}
</pre>
</noinclude>
<includeonly>

{{#subobject:{{{Author}}}-{{{Date Sent}}}
  |Message topic={{PAGENAME}}
  |Has author={{{Author}}}
  |Date sent={{{Date Sent}}}
  |Has URL={{{Link}}}
  |Contains text={{{Text}}}
}}
<div style="border: 1px solid black; border-radius: 5px;padding:5px"
>
<div style="display:flex; flex-direction:row; align-items:center; border-bottom:1px solid black; gap:10px; padding-bottom:5px;"><img src={{{Avatar|}}} style="width:30px;border-radius:10px"/><span style="font-weight:bold;">{{{Author}}}</span><span><nowiki>#</nowiki>{{{Channel|}}}</span><span style="font-style:italic;color:#999999">[{{{Link}}} {{{Date Sent}}}]</span></div>
<div>
{{{Text}}}
</div>
</div>
</includeonly>
"""
)
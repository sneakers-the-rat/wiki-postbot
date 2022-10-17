"""
Class for interfacing with mediawiki
"""
from typing import List
from urllib.parse import urljoin
from dataclasses import dataclass
from wiki_postbot.creds import Mediawiki_Creds
from wiki_postbot.formats.wiki import WikiPage
from wiki_postbot.templates.wiki import TemplateMessage
from wiki_postbot.patterns.wikilink import Wikilink
from wiki_postbot.actions import Result
from datetime import datetime
import requests
from discord.message import Message, Embed
import pdb

# creds = Mediawiki_Creds.from_json('mediawiki_creds.json')


class Wiki:
    def __init__(self, url:str, api_suffix:str="/api.php", index_page="Discord Messages"):
        self.url = url
        self.api_url = urljoin(self.url, api_suffix)
        self.sess = None
        self.index_page = index_page


    def login(self, creds:Mediawiki_Creds):
        # get token to log in
        sess = requests.Session()

        login_token = sess.get(
            self.api_url,
            params={
                "action":"query",
                "meta":"tokens",
                "type":"login",
                "format":"json"
            },
            verify=False
        ).json()['query']['tokens']['logintoken']


        login_result = sess.post(
            self.api_url,
            data = {
                "action":"login",
                "lgname":creds.user,
                "lgpassword":creds.password,
                "lgtoken": login_token,
                "format": "json"
            },
            verify=False
        )
        assert login_result.json()['login']['result'] == "Success"
        self.sess = sess

    def get_page(self, page:str) -> WikiPage:

        content = self.sess.get(
            self.api_url,
            params={
                'action':'parse',
                'page': page,
                'prop': 'wikitext',
                'formatversion':'2',
                'format':'json'
            }
        ).json()
        return WikiPage.from_source(title=content['parse']['title'], source=content['parse']['wikitext'])

    def insert_text(self, page, section, text):

        # TODO: Move finding section IDs into the page class!
        page_text = self.get_page(page)

        sections = page_text.content.get_sections()
        matching_section = -1
        for i, page_section in enumerate(sections):
            if page_section.title is not None and page_section.title.strip().lower() == section.lower():
                matching_section = i
                break


        token = self.sess.get(
            self.api_url,
            params={
                "action": "query",
                "meta": "tokens",
                "format": "json"
            },
            verify=False
        ).json()['query']['tokens']['csrftoken']

        if matching_section >= 0:
            print(f'found matching section {matching_section}')
            result = self.sess.post(
                self.api_url,
                data={
                    "action":"edit",
                    "title":page,
                    "section":str(matching_section),
                    "appendtext":text,
                    "format":"json",
                    "token":token
                }
            )
        else:
            print('making new section')
            result = self.sess.post(
                self.api_url,
                data={
                    "action":"edit",
                    "title":page,
                    "section":"new",
                    "sectiontitle":section,
                    "appendtext":text,
                    "format":"json",
                    "token":token
                }
            )
        return result

    def handle_discord(self, msg:Message) -> Result:
        """
        Not being precious about this, just implementing
        and will worry about generality later!
        """
        # Get message in mediawiki template formatting
        template_str = TemplateMessage.format_discord(msg)

        # parse wikilinks, add to each page
        wikilinks = Wikilink.parse(msg.content)
        errored_pages = []
        for link in wikilinks:
            if link.section is None:
                section = "Discord"
            else:
                section = link.section

            res = self.insert_text(link.link, section, template_str)
            if res.json()['edit']['result'] != 'Success':
                errored_pages.append(res.json())

        # Add to index page (only once)
        self.add_to_index(template_str)

        if len(errored_pages) == 0:
            # gather links for a reply
            reply = '\n'.join([f"[{l.link}]({urljoin(self.url, l.link.replace(' ', '_'))})" for l in wikilinks])

            return Result(ok=True, log=f"Successfully posted message to {[l.link for l in wikilinks]}", reply=reply)
        else:
            return Result(ok=False, log=f"Got exceptions: {errored_pages}")

    def add_to_index(self, message):
        section = datetime.today().strftime("%y-%m-%d")
        self.insert_text(page=self.index_page, section=section, text=message)

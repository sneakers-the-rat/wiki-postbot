"""
Class for interfacing with mediawiki
"""
from typing import List
from urllib.parse import urljoin
from dataclasses import dataclass
from wiki_postbot.creds import Mediawiki_Creds
import requests

# creds = Mediawiki_Creds.from_json('mediawiki_creds.json')




class Wiki:
    def __init__(self, url:str, api_suffix:str="/api.php"):
        self.url = url
        self.api_url = urljoin(self.url, api_suffix)
        self.sess = None


    def login(self, creds:Mediawiki_Creds) -> requests.Session:
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
        return sess

    def get_page_content(self, page:str) -> str:

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
        return content['parse']['wikitext']

    def insert_text(self, page, section, text):

        token = self.sess.get(
            self.api_url,
            params={
                "action": "query",
                "meta": "tokens",
                "format": "json"
            },
            verify=False
        ).json()['query']['tokens']['csrftoken']

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

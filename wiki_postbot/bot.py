from pathlib import Path
import logging
import tweepy
import typing
import pdb
from typing import List, Optional, Type

from wiki_postbot.creds import Creds, Zenodo_Creds
from wiki_postbot.thread import Thread
from wiki_postbot.logger import init_logger
from wiki_postbot.actions import checks, commands
if typing.TYPE_CHECKING:
    from wiki_postbot.actions import Action


class WikiPostBot(tweepy.StreamingClient):
    check_classes = [checks.Wikilink] # type: List[Type[checks.Check]]
    #command_classes = [commands.Identify] # type: List[Type[commands.Command]]
    command_classes = []

    def __init__(
            self,
            creds:Path = Path('twitter_creds.json'),
            wiki_creds:Path = Path('wiki_creds.json'),
            username:str='wikibot3k',
            following:Optional[List[str]]=None,
            basedir:Path=Path().home()/"wiki_postbot",
            loglevel="DEBUG",
            debug:bool = False
    ):

        self._creds = None
        self._wiki_creds = None
        self._client = None
        self.basedir=Path(basedir)

        self.creds_path = Path(creds)
        self.wiki_creds_path = Path(wiki_creds)
        self.username = username
        self.debug = debug
        self.following = following
        self.logger = init_logger('wiki_postbot.bot', basedir, loglevel=loglevel)

        super(WikiPostBot, self).__init__(self.creds.bearer_token)

        self.add_rules(self.rule)

        self.checks = [cls(self) for cls in self.check_classes]
        self.commands = [cls(self) for cls in self.command_classes]

    @property
    def rule(self) -> tweepy.StreamRule:
        """
        StreamRule for accounts we're following or if we're mentioned
        """
        rule = f"@{self.username}"
        if self.following is not None:
            following = [f'from:{user}' for user in self.following]
            rule = ' OR '.join([*following, rule])
        return tweepy.StreamRule(rule)


    def on_response(self, response:tweepy.Response):
        """
        Check if the tweet has a wikilink in it
        """

        if self.debug:
            pdb.set_trace()

        self.logger.info(f'Mentioned: {response.data.text}')


        # Do checks to see if we should do anything!
        for check in self.checks:
            res = check.do(response)
            if not res.ok:
                if res.log:
                    self.logger.info(res.log)
                return

        # Determine what action we should do!
        for command in self.commands:
            if command.check(response):
                self.logger.info(f"Given Command {command.name}")
                res = command.do(response)
                if res.log:
                    self.logger.debug(res.log)
                if res.reply:
                    self.reply(response, res.reply)
                return

        # TODO: move this to a command class
        # thread = Thread.from_tweet(self.creds, response)
        # self.logger.info('thread received')
        # try:
        #     pdf = thread.to_pdf()
        #     self.logger.info('pdf created')
        #     depo = post_pdf(pdf, thread, self.zenodo_creds)
        #     self.logger.info('posted pdf')
        #     self.logger.debug(depo)
        #
        # finally:
        #     pdf.unlink()
        #
        # self.reply_completed(response, depo)


    def reply_completed(self, response: tweepy.Response, deposit:Deposition):

        self.client.create_tweet(text=f"The preprint of your thread is ready: {deposit.doi_url} - {deposit.title}",
                            in_reply_to_tweet_id=response.data.id)
        self.logger.info('replied')

    def reply(self, response: tweepy.Response, text:str):
        self.client.create_tweet(text=text,
                                 in_reply_to_tweet_id=response.data.id)



    def run(self, threaded:bool=False):
        self.logger.debug('starting')
        self.filter(threaded=threaded,
                    tweet_fields=[
                        "in_reply_to_user_id",
                        "author_id",
                        "created_at",
                        "conversation_id",
                        "entities",
                        "referenced_tweets"
                    ],
                    expansions=[
                        'author_id'
                    ]
                    )
        self.logger.debug('stopped')

    @property
    def client(self) -> tweepy.Client:
        if self._client is None:
            self._client = tweepy.Client(
                consumer_key=self.creds.api_key,
                consumer_secret=self.creds.api_secret,
                access_token=self.creds.access_token,
                access_token_secret=self.creds.access_secret)
        return self._client

    @property
    def creds(self) -> Creds:
        if self._creds is None:
            self._creds = Creds.from_json(self.creds_path)
        return self._creds

    @property
    def wiki_creds(self) -> Zenodo_Creds:
        if self._wiki_creds is None:
            self._wiki_creds = Zenodo_Creds.from_json(self.wiki_creds_path)
        return self._wiki_creds




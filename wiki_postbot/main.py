import argparse
from wiki_postbot.bot import WikiPostBot
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a wiki_postbot bot!")
    parser.add_argument('--creds', type=Path, help="Location of twitter credentials .json file",
                        default=Path('twitter_creds.json'))
    parser.add_argument('--wiki_creds', type=Path, help="Path to wiki credentials .json file",
                        default=Path('wiki_creds.json'))
    parser.add_argument('-u', '--username', type=str, help="Username of our bot",
                        default="wikibot3k")
    parser.add_argument('-b', '--basedir', help="Base directory to store files",
                        type=Path, default=Path().home() / "wiki_postbot")
    parser.add_argument('-l', '--loglevel', type=str, help="Loglevel for wiki_postbot bot, DEBUG, INFO, WARNING, or ERROR",
                        default='DEBUG')
    parser.add_argument('-d', '--debug', action='store_true', help="Debug responses from bot")
    return parser.parse_args()

def main():
    args = parse_args()
    tt = WikiPostBot(**args.__dict__)
    tt.run()

if __name__ == "__main__":
    main()

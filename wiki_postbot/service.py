"""
Install a systemd service to run the discord bot
"""
import shutil
from pathlib import Path
from dataclasses import dataclass, field, asdict
from wiki_postbot.clients.discord_client import argparser

SERVICE_TEMPLATE = """
[Unit]
Description=Discord Wikibot
After=syslog.target
After=network.target

[Service]
RestartSec=2s
Type=simple
User={user}
Group={user}
ExecStart={bot_script} --directory {directory} --wiki {wiki_url}
Restart=always

[Install]
WantedBy=multi-user.target
"""

@dataclass
class Service:
    wiki_url:str
    directory:Path=Path('/etc/wikibot')
    user:str='wikibot'
    bot_script:str=field(default_factory=lambda: shutil.which('discord_bot'))

    def install_service(self):
        # make directory and set permissions
        mode = 0o660
        self.directory.mkdir(exist_ok=True, mode=mode)
        (self.directory / 'logs').mkdir(exist_ok=True, mode=mode)
        for file in self.directory.glob('*.json'):
            shutil.chown(
                str(file),
                self.user,
                self.user
            )
            file.chmod(mode)

        # make service file and write
        service = SERVICE_TEMPLATE.format(
            **asdict(self)
        )
        with open('/etc/systemd/system/wikibot.service', 'w') as sfile:
            sfile.write(service)

        print('System file created, you should now enable it with \nsystemctl enable wikibot\nand start it with\nsystemctl start wikibot')

def main():
    parser = argparser()
    args = parser.parse_args()

    service = Service(wiki_url=args.wiki, directory=args.directory)
    service.install_service()

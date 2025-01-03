#!/usr/bin/python3
from typing import List
import subprocess

from Config import Config
from locale import str

class DesktopMailer:
    _body: str
    _subject: str
    _receiver: List[str]
    _attach: List[str]

    def __init__(self, config: Config):
        self._body = None
        self._subject = None
        self._receiver = None
        self._attach = []

    async def load(self) -> None:
        pass #for compatibility to other mailer
    async def startNewMail(self) -> None:
        pass #for compatibility to other mailer
    
    async def setBody(self, html) -> None:
        self._body = html

    async def setSubject(self, subject: str) -> None:
        self._subject = subject

    async def setTo(self, receiver: List[str]) -> None:
        self._receiver = receiver

    async def addAttachment(self, absFilePath: str) -> None:
        self._attach.append(absFilePath)

    async def composeMail(self):
        self._assertNotEmpty(self._receiver, "To")
        self._assertNotEmpty(self._subject, "Subject")
        self._assertNotEmpty(self._body, "Body")
        args = ["xdg-email", 
                        "--subject", self._subject,
                        "--body", self._body]
        for file in self._attach:
            args.append("--attach")
            args.append(file)

        
        args.append(', '.join(self._receiver))
        subprocess.run(args)
        print('If email body is showing as raw HTML, run the following command in command line.')
        print('This will put body text in clipboad. You may just paste it in your mail clients window.')
        print(f'xclip -selection clipboard -t text/html -i < <(echo "{self._body}")')
        # klembord.init()
        # klembord.set_with_rich_text('', self._body)
#         subprocess.run("xclip", "-selection", "clipboard", "-t", "text/html", "-i", "<", "<(echo ", self._body, ")")
# xclip -selection clipboard -t text/html -i < <(echo self._body)

        
    def _assertNotEmpty(self, setting, label: str):
        if (setting is None or setting is []):
            raise Exception(f'"{label}" must not be empty')

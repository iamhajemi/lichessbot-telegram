"""Allows lichess-bot to send messages to the chat."""
import logging
import chess
import test_bot.lichess
from lib import model
from lib.engine_wrapper import EngineWrapper
from lib import lichess
from lib.lichess_types import GameEventType
from collections.abc import Sequence
from lib.timer import seconds
from typing import Union
MULTIPROCESSING_LIST_TYPE = Sequence[model.Challenge]
LICHESS_TYPE = Union[lichess.Lichess, test_bot.lichess.Lichess]

logger = logging.getLogger(__name__)


class ChatLine:
    """Information about the message."""

    def __init__(self, message_info: GameEventType) -> None:
        """Information about the message."""
        self.room = message_info["room"]
        """Whether the message was sent in the chat room or in the spectator room."""
        self.username = message_info["username"]
        """The username of the account that sent the message."""
        self.text = message_info["text"]
        """The message sent."""


class Conversation:
    """Enables the bot to communicate with its opponent and the spectators."""

    def __init__(self, game: model.Game, engine: EngineWrapper, xhr: LICHESS_TYPE, version: str,
                 challenge_queue: MULTIPROCESSING_LIST_TYPE) -> None:
        """
        Communication between lichess-bot and the game chats.

        :param game: The game that the bot will send messages to.
        :param engine: The engine playing the game.
        :param xhr: A class that is used for communication with lichess.
        :param version: The lichess-bot version.
        :param challenge_queue: The active challenges the bot has.
        """
        self.game = game
        self.engine = engine
        self.xhr = xhr
        self.version = version
        self.challengers = challenge_queue

    command_prefix = "!"

    def react(self, line: ChatLine) -> None:
        """
        React to a received message.

        :param line: Information about the message.
        """
        logger.info(f"*** {self.game.url()} [{line.room}] {line.username}: {line.text}")
        if line.text[0] == self.command_prefix:
            self.command(line)

    def command(self, line: ChatLine) -> None:
        """Handle incoming chat messages."""
        if line.text[0] == "!":
            command = line.text[1:].lower()
            if command == "eval" and self.game.is_abortable():
                self.send_reply(line, "Oyun henüz başlamadı!")
            elif command == "eval":
                stats = self.engine.get_stats(for_chat=True)
                # İstatistikleri tek satırda birleştir
                self.send_reply(line, " | ".join(stats))
            elif command == "name":
                self.send_reply(line, f"lichess-bot {self.version}")
            elif command == "howto":
                self.send_reply(line, "Komutlar: !eval, !name")
            else:
                self.send_reply(line, "Geçersiz komut. Komutlar: !eval, !name")

    def send_reply(self, line: ChatLine, reply: str) -> None:
        """Send a reply to a chat message."""
        logger.info(f"*** {self.game.url()} [{line.room}] {self.game.username}: {reply}")
        self.xhr.chat(self.game.id, line.room, reply)

    def send_message(self, room: str, message: str) -> None:
        """Send the message to the chat."""
        if message:
            self.send_reply(ChatLine({"room": room, "username": "", "text": ""}), message)

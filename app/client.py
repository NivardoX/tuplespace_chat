import random
from datetime import datetime
from typing import List, Dict, Set

import Pyro4

from settings import PYRO_URL

import time

from entry import Entry


class Client:
    broker = None

    name = None
    topics = None
    broker_topics = None

    buffer: List[Dict] = []
    rooms: Set[str] = set()
    participants = set()
    messages: List[str] = []

    counter = None

    def __init__(self, room="default", name=None):
        self.last_seen = 0
        self.name = name
        self.room = room
        self.server = Pyro4.core.Proxy(PYRO_URL)
        self.counter = time.time()

    def update(self):
        self.rooms: Set[str] = set()
        self.participants = set()
        self.messages: List[str] = []

        now = time.time()
        if now - self.counter < 0.16:
            return

        # Fetch rooms
        tuples = self.fetch_new_tuples(Entry())
        for tuple in tuples:
            self.register_room(tuple)

        # Fetch room messages
        tuples = self.fetch_new_tuples(Entry(room=self.room, type="message"))
        for tuple in tuples:
            self.register_message(tuple)

        # Fetch private messages
        tuples = self.fetch_new_tuples(Entry(target=self.name, type="private_message"))
        for tuple in tuples:
            self.register_message(tuple)

    def get_participants(self):
        tuples = self.server.scan(Entry(room=self.room))
        participants = set()

        for tuple in tuples:
            participants.add(tuple["source"])
        return list(participants)

    def register_message(self, tuple):
        self.messages.append(Client.format_message(tuple))

    def register_room(self, tuple):
        if tuple["room"]:
            self.rooms.add(tuple["room"])

    def send_message(self, message, room=None, target=None):
        type = "message"
        if target:
            type = "private_message"
        self.server.put(
            Entry(
                type=type, message=message, source=self.name, room=room, target=target
            )
        )

    def fetch_new_tuples(self, tuple=Entry()):
        tuples = self.server.scan(tuple)
        if len(tuples) == 0:
            return []

        tuples: List[dict] = sorted(tuples, key=lambda x: x["created_at"])

        if len(tuples) == 0:
            return []
        return tuples

    @staticmethod
    def format_message(tuple):

        time = datetime.fromtimestamp(tuple["created_at"]).strftime("%H:%M:%S")
        target = tuple["target"] or tuple["room"]
        return f"[{time}]{tuple['source']}@{target} :  {tuple['message']}"

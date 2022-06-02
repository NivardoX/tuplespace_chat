import logging
from copy import deepcopy
import Pyro4

from typing import List

from entry import Entry


@Pyro4.expose
class Server(object):
    entries: List[Entry] = list()

    def _search_for_tuples(self, tupla: Entry):
        return list(filter(lambda obj: tupla.equals(obj), self.entries))

    def put(self, tupla: Entry):
        if not isinstance(tupla, Entry):
            tupla = Entry.deserialize(tupla)

        self.entries.append(tupla)

    def get(self, tupla: Entry):
        if not isinstance(tupla, Entry):
            tupla = Entry.deserialize(tupla)

        filtered = self._search_for_tuples(tupla)
        if len(filtered) == 0:
            return None

        next_tuple = filtered[0]

        tuple_found = deepcopy(next_tuple)
        self.entries.remove(next_tuple)
        return tuple_found

    def getp(self, tupla: Entry):
        if not isinstance(tupla, Entry):
            tupla = Entry.deserialize(tupla)

        filtered = self._search_for_tuples(tupla)
        if len(filtered) == 0:
            return None
        next_tuple = filtered[0]

        return next_tuple

    def query_all(self, tupla: Entry):
        if not isinstance(tupla, Entry):
            tupla = Entry.deserialize(tupla)

        tuples = list(self._search_for_tuples(tupla))
        return tuples

    def count(self, tupla: Entry):
        if not isinstance(tupla, Entry):
            tupla = Entry.deserialize(tupla)

        tuples = list(self.query_all(tupla))
        return len(tuples)

    @staticmethod
    def start():
        Pyro4.Daemon.serveSimple(
            {
                Server: "Server",
            },
            host="0.0.0.0",
            port=8081,
            ns=False,
            verbose=True,
        )
        logging.info("[Server started]")

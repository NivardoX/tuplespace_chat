import dataclasses

import nanoid

from app.server import Server

from app.gui import GUI
from settings import PYRO_URL
from entry import Entry
import Pyro4

import logging

Pyro4.util.SerializerBase.register_class_to_dict(Entry, dataclasses.asdict)


def start():
    with Pyro4.Proxy(PYRO_URL) as p:
        try:
            p._pyroBind()
            # name = input("What's your name?")
            name = nanoid.generate()

            GUI(name=name).start()

        except Pyro4.errors.CommunicationError:

            logging.info("Iniciando servidor")
            Server.start()


if __name__ == "__main__":
    start()

from threading import Thread
from time import sleep
from queue import Queue
from copy import copy


class Fryer(Thread):

    def __init__(self, donuts, queue, *args, **kwargs):

        super(Fryer, self).__init__(*args, **kwargs)

        self._donuts = donuts
        self._queue = queue

    def start(self):

        while True:

            if self._queue.empty():

                sleep(0.01)

                continue

            donut = self._queue.get()

            if donut.status == 'new_order':

                donut.status = 'received'

                self._donuts

                self._queue.put(donut)

            elif donut.status == 'received':

                sleep(0.4)

                donut.status = 'cooking'

                self._queue.put(donut)

            elif donut.status == 'cooking':

                sleep(1)

                donut.status = 'ready'


class KitchenService(object):

    def __init__(self):

        self._donuts = []
        self._fryer = Queue()

        self._queue = Fryer(self._donuts, self._queue, daemon=True)

    def get_donuts(self):

        copied_donuts = []

        for donut in self._donuts:

            copied_donuts.append(copy(donut))

        return copied_donuts

    def add_donut(self, donut):

        self._queue.put(donut)


__all__ = ['KitchenService']

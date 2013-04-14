import logging
log = logging.getLogger("history")
import os
import time

class History(object):
    def __init__(self, pth, sim=None):
        self.path = pth

        if sim is not None:
            self.running = True
            self.sim = sim
            self.init()
        else:
            start = time.clock()
            self.sim = self.load()
            elapsed = time.clock() - start
            log.debug("Loading history from %s took %f seconds", pth, elapsed)
            self.running = False

    def load(self):
        pass

    def init(self):
        pass

    def close(self):
        pass

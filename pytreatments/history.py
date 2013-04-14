import logging
log = logging.getLogger("history")
import os
import time

class History(object):
    def __init__(self, pth, sim=None, replicate_seed=None):
        self.path = pth

        if sim is not None:
            self.running = True
            self.sim = sim
            self.init()
        else:
            assert replicate_seed is not None
            start = time.clock()
            self.sim = self.load()
            elapsed = time.clock() - start
            log.debug("Loading history from %s took %f seconds", pth, elapsed)
            self.running = False

            # Verify that the seed is the same (ensures stability of analysis
            # under changing code)
            if self.sim.seed != replicate_seed:
                log.warning("The replicate seed %d is different from the simulation seed %d",
                            replicate_seed, self.sim.seed)

            # Extra verification can be built into here
            self.verify()

    def load(self):
        pass

    def init(self):
        pass

    def close(self):
        pass

    def verify(self):
        pass


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
            self.mark_time()
            self.sim = self.load()
            log.debug("Loading history from %s took %f seconds",
                      pth, self.report_time())
            self.running = False

            # Verify that the seed is the same (ensures stability of analysis
            # under changing code)
            if self.sim.seed != replicate_seed:
                log.warning(
                    "The replicate seed %d is different from the simulation seed %d",
                    replicate_seed, self.sim.seed)

            # Extra verification can be built into here
            self.verify()

    def mark_time(self):
        self.start_counting = time.clock()

    def report_time(self):
        return time.clock() - self.start_counting

    def load(self):
        pass

    def init(self):
        pass

    def close(self):
        pass

    def verify(self):
        pass

import logging
log = logging.getLogger("pytreatments.simulation")

class Interrupt(Exception):
    pass


class BaseProgress(object):
    def __init__(self):
        self.running = True
        self.paused = False

    def begin(self, sim):
        pass

    def update(self, sim):
        pass

    def interact(self, sim):
        pass

    def end(self, sim):
        pass


class Simulation(object):
    def __init__(self, seed, name, replicate_seq):
        """Construction a simulation.
        """
        self.seed = seed
        self.name = name
        self.replicate_seq = replicate_seq
        self.description = "T{0.name} R{0.replicate_seq:0>3}".\
            format(self)
        self.time_step = 0
        self.more = True

    def _begin(self):
        return self.begin()

    def _end(self):
        self.end()

    def end(self):
        pass

    def _step(self, history):
        self.more = self.step(history)

    def run(self, history=None, callbacks=None, progress=None):
        if progress:
            progress.begin()

        while 1:
            self._step(history)

            if callbacks:
                for c in callbacks:
                    c(self)
            if progress:
                progress.update(self)
                while progress.paused:
                    progress.interact(self)
                if progress.running is False:
                    log.info("User interrupted simulation...")
                    self.more = False

            if not self.more:
                break

            # Update time step after we've done all the processing
            self.time_step += 1

        if progress:
            progress.end(self)

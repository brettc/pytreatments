import logging
log = logging.getLogger("pytreatments.simulation")

import active


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
    def __init__(self, seed=None, treatment=None, replicate=None):
        """Construction a simulation.
        """
        self.seed = seed
        self.treatment = treatment
        self.replicate = replicate
        if self.treatment is not None and self.replicate is not None:
            self.description = "{0.treatment} R{0.replicate:0>3}".format(self)
        else:
            self.description = ""

        self.history = None
        self.time_step = 0

    def _begin(self):
        active.set_active(self)
        self.begin()

    def begin(self):
        pass

    def _end(self):
        self.end()
        active.clear_active()

    def end(self):
        pass

    def _step(self):
        self.more = self.step()

    def run(self, callbacks=None, progress=None):
        if progress:
            progress.begin(self)

        while 1:
            self._step()

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

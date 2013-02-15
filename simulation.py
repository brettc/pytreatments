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
    def __init__(self, treatment=None, replicate=None):
        """Construction a simulation.
        """
        self.treatment = treatment
        self.replicate = replicate
        if self.treatment is not None and self.replicate is not None:
            self.description = "{0.treatment} R{0.replicate:0>3}".format(self)
        else:
            self.description = ""

        self.time_step = 0

    def begin(self):
        active.set_active(self)
        self.on_begin()

    def end(self):
        self.on_end()
        active.clear_active()

    def step(self):
        self.more = self.on_step()

    def run(self, callbacks=None, progress=None):
        if progress:
            progress.begin(self)

        while 1:
            self.step()

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

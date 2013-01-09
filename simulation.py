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
    def __init__(self, parameters, challenges, treatment=None, replicate=None):
        """Construction a simulation.

        This brings populations and challenges together
        Both progress and analyses are optional.
        """
        self.parameters = parameters
        self.challenges = challenges
        self.challenge_index = -1

        self.treatment = treatment
        self.replicate = replicate
        if self.treatment is not None and self.replicate is not None:
            self.description = "{0.treatment} R{0.replicate:0>3}".format(self)
        else:
            self.description = ""

        self.time_step = 0

    def run(self, callbacks=None, progress=None):
        if progress:
            progress.begin(self)

        while 1:
            self.more = self.step()

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

            self.time_step += 1
            if self.time_step == self.parameters.max_steps:
                log.warning("Reached max steps, ending simulation...")
                break

        if progress:
            progress.end(self)


    def step(self):
        raise NotImplementedError

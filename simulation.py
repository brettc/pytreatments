import logging
log = logging.getLogger("simulation")

from population import Population


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

        self.population = Population(parameters)
        self.about_to_sweep = False
        self.goto_next_challenge()
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

    def goto_next_challenge(self):
        if self.challenge_index + 1 >= len(self.challenges):
            log.info("No further challenges...")
            return False
        self.bump_challenge = True
        return True

    def step(self):
        if self.bump_challenge:
            self.bump_challenge = False
            self.challenge_index += 1
            log.info(">>> Moving to new challenge %s", self.challenge_index)

        self.population.new_generation(self.about_to_sweep)
        # Always reset
        self.about_to_sweep = False

        ch = self.challenges[self.challenge_index]
        self.population.encounter(ch)
        log.info('%s: Challenge %02d, Generation %05d, max fitness is %5.5f',
                 self.description, self.challenge_index,
                 self.population.generation, max(self.population.fitnesses))

        # If we've found the best, we're done with this challenge
        best = max(self.population.fitnesses)
        if best == 1.0:
            if self.parameters.sweep:
                self.about_to_sweep = True
            return self.goto_next_challenge()

        return True

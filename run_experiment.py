import logging
log = logging.getLogger("run_experiment")

import sys
from pytreatments import (
    run_main, Context, Simulation,
    register_plugin, TreatmentPlugin, ReplicatePlugin
)


class Parameters(object):
    def __init__(self, name, cycles):
        self.name = name
        self.cycles = cycles


class MyContext(Context):
    def load_namespace(self, ns):
        # load our parameters into here
        ns['parameters'] = Parameters


class MySimulation(Simulation):
    def __init__(self, seed, treatment, replicate, params):
        Simulation.__init__(self, seed, treatment, replicate)
        self.params = params

    def begin(self):
        log.info("Starting up with Parameters:"
                 "name:{0.name}, cycles:{0.cycles}".format(self.params))

    def step(self):
        log.info("Stepping %s", self.description)
        if self.time_step < self.params.cycles:
            return True

        return False

    def end(self):
        log.info("Ending ...")


class MyHistory(object):
    def __init__(self, folder, sim=None):
        if sim is None:
            log.info("Loading history object from '%s'" % folder)
        else:
            log.info("Creating history object for recording '%s'" % folder)

    def close(self):
        pass


@register_plugin
class simple_capture(ReplicatePlugin):

    def begin_replicate(self, sim):
        self.output = self.get_file('captured.txt')

    def step(self, sim):
        self.output.write("stepping in sim %s" % sim.time_step)

    def analyse(self, history):
        log.info("Analysing history ...")


@register_plugin
class nothing(TreatmentPlugin):
    def begin_treatment(self):
        self.output = self.get_file('yippeee.txt')

    def begin_replicate(self, sim):
        self.output.write("Another one\n")


if __name__ == "__main__":
    sys.exit(run_main(MySimulation, MyContext, MyHistory))

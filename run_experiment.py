import logging
log = logging.getLogger("run_experiment")

import sys
from pytreatments import (
    run_main, Context, Simulation, ReplicatePlugin, register_plugin
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
    def __init__(self, treatment, replicate, params):
        Simulation.__init__(self, treatment, replicate)
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


@register_plugin
class simple_capture(ReplicatePlugin):

    def begin_replicate(self, sim):
        self.output = self.get_file('captured.txt')

    def step(self, sim):
        self.output.write("stepping in sim %s" % sim.time_step)


if __name__ == "__main__":
    sys.exit(run_main(MySimulation, MyContext))

import logging
log = logging.getLogger("run_experiment")

import sys
from pytreatments import (
    run_main, Context, Simulation,
    register_plugin, Plugin, History
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
    def __init__(self, seed, name, replicate_seq, params):
        Simulation.__init__(self, seed, name, replicate_seq)
        self.params = params

    def begin(self):
        log.info("Starting up with Parameters:"
                 "name:{0.name}, cycles:{0.cycles}".format(self.params))
        return True

    def step(self, history):
        log.info("Stepping %s", self.description)
        if self.time_step >= self.params.cycles:
            return False
        return True

    def end(self):
        log.info("Ending ...")


class MyHistory(History):
    pass


@register_plugin
class simple_capture(Plugin):

    def begin_replicate(self, r):
        self.output = self.get_file('captured.txt')

    def step(self, sim):
        self.output.write("stepping in sim %s\n" % sim.time_step)

    def end_replicate(self, r):
        self.output.close()
        h = r.get_history()
        log.info("Analysing history ...%s", h)

    def end_experiment(self, exp):
        for t in exp.treatments:
            for r in t.replicates:
                log.info("Another rep...%s", r.output_path)
                h = r.get_history()
                if h:
                    s = h.sim
                    log.info("simulation seed %s", s.seed)
                

if __name__ == "__main__":
    sys.exit(run_main(MySimulation, MyContext, MyHistory))

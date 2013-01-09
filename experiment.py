import logging
log = logging.getLogger("experiment")

from itertools import chain
from simulation import Simulation
from plugin import TreatmentPlugin, ReplicatePlugin, ExperimentPlugin
import random


class Treatment(object):
    def __init__(self, experiment, name, rcount, parameters, challenges):
        self.experiment = experiment
        self.name = name
        self.replicate = None
        self.replicate_count = rcount
        self.parameters = parameters
        self.challenges = challenges

    def run(self, e_analyses, e_callbacks, progress=None):

        # Set up and run the treatment_analyses
        t_analyses = []
        callbacks = e_callbacks[:]
        for cls, kwargs in self.experiment.treatment_analyses:
            c = cls(self.experiment.config, self)
            c.__dict__.update(kwargs)
            t_analyses.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for c in chain(e_analyses, t_analyses):
            if hasattr(c, 'begin_treatment'):
                log.debug("Begin Treatment processing for PLUGIN '%s'" % c.name)
                c.begin_treatment()

        # Run all the replicates
        for i in range(self.replicate_count):
            self.replicate = i
            self.run_replicate(e_analyses, t_analyses, callbacks[:], progress)

        for c in chain(reversed(t_analyses), reversed(e_analyses)):
            if hasattr(c, 'end_treatment'):
                c.end_treatment()
                log.debug("End Treatment processing for PLUGIN '%s'" % c.name)

    def run_replicate(self, e_analyses, t_analyses, callbacks, progress):
        log.info("{:-<78}".format("Begin Treatment '%s', replicate %d of %d" % (
                 self.name,
                 self.replicate + 1,
                 self.replicate_count)))

        sim = Simulation(self.parameters, self.challenges, self.name, self.replicate)

        r_analyses = []
        for cls, kwargs in self.experiment.replicate_analyses:
            c = cls(self.experiment.config, self)
            c.__dict__.update(kwargs)
            r_analyses.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for c in chain(e_analyses, t_analyses, r_analyses):
            if hasattr(c, 'begin_replicate'):
                log.debug("Begin Replicate processing for PLUGIN '%s'" % c.name)
                c.begin_replicate(sim)

        sim.run(callbacks, progress)

        for c in chain(reversed(r_analyses),
                       reversed(t_analyses),
                       reversed(e_analyses)):
            if hasattr(c, 'end_replicate'):
                c.end_replicate(sim)
                log.debug("End Replicate processing for PLUGIN '%s'" % c.name)

        # log.info("{:-<78}".format("End Treatment '%s', replicate %d of %d" % (
                 # self.name,
                 # self.replicate + 1,
                 # self.replicate_count)))


class Experiment(object):
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.seed = random.seed()

        self.treatments = []

        self.replicate_analyses = []
        self.treatment_analyses = []
        self.experiment_analyses = []

    def add_treatment(self, name, parameters, challenges, replicates):
        log.info("Adding treatment '%s' to Experiment '%s', with %d replicates",
                 name, self.name, replicates)
        self.treatments.append(Treatment(self, name, replicates, parameters, challenges))


    def load_plugin(self, plugin_cls, kwargs):
        """Add some analyses to run both during and after the simulation"""
        # if ExperimentPlugin in plugin_cls.__subclasses__():
        log.info("Loading PLUGIN '%s' into Experiment '%s'",
                 plugin_cls.__name__, self.name)
        if issubclass(plugin_cls, TreatmentPlugin):
            self.treatment_analyses.append((plugin_cls, kwargs))
        if issubclass(plugin_cls, ReplicatePlugin):
            self.replicate_analyses.append((plugin_cls, kwargs))
        if issubclass(plugin_cls, ExperimentPlugin):
            self.experiment_analyses.append((plugin_cls, kwargs))

    def order_by_priority(self):
        for c in (self.treatment_analyses,
                  self.replicate_analyses,
                  self.experiment_analyses):
            c.sort(key=lambda x: x[0].priority)

    def run(self, progress):
        callbacks = []
        e_analyses = []

        self.order_by_priority()

        for cls, kwargs in self.experiment_analyses:
            c = cls(self.config)
            c.__dict__.update(kwargs)
            if hasattr(c, 'begin_experiment'):
                log.info("begin experiment analysis '%s'", c.name)
                c.begin_experiment()
            e_analyses.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for t in self.treatments:
            t.run(e_analyses, callbacks, progress)

        for c in reversed(e_analyses):
            if hasattr(c, 'end_experiment'):
                log.info("end experiment analysis '%s'", c.name)
                c.end_experiment()



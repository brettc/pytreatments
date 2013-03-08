import logging
log = logging.getLogger("experiment")
import os

from itertools import chain
from plugin import TreatmentPlugin, ReplicatePlugin, ExperimentPlugin
import random

RUNNING = "RUNNING"
COMPLETE = "COMPLETE"

class Interrupt(Exception):
    """Use this to stop an experiment"""
    pass


class Experiment(object):
    def __init__(self, config, name):
        self.config = config
        self.name = name

        self.treatments = []

        self.replicate_plugin = []
        self.treatment_plugin = []
        self.experiment_plugin = []

        # We use this to generates seeds for all of the experiments
        self.rand = random.Random()
        self.output_path = self.config.output_path

    def set_seed(self, seed):
        self.rand.seed(seed)

    def add_treatment(self, name, replicates, **kwargs):
        log.info(
            "Adding treatment '%s' to Experiment '%s', with %d replicates",
            name, self.name, replicates)
        self.treatments.append(Treatment(self, name, replicates, **kwargs))

    def load_plugin(self, plugin_cls, kwargs):
        """Add some plugin to run both during and after the simulation"""
        # if ExperimentPlugin in plugin_cls.__subclasses__():
        log.info("Loading plugin: priority {0.priority}, name '{0.__name__}'".format(
                 plugin_cls))
        if issubclass(plugin_cls, TreatmentPlugin):
            self.treatment_plugin.append((plugin_cls, kwargs))
        if issubclass(plugin_cls, ReplicatePlugin):
            self.replicate_plugin.append((plugin_cls, kwargs))
        if issubclass(plugin_cls, ExperimentPlugin):
            self.experiment_plugin.append((plugin_cls, kwargs))

    def order_by_priority(self):
        for c in (self.treatment_plugin,
                  self.replicate_plugin,
                  self.experiment_plugin):
            c.sort(key=lambda x: x[0].priority)

    @property
    def experiment_mark(self):
        return os.path.join(self.output_path, RUNNING)

    def run_begin(self):
        open(self.experiment_mark, 'a').close()

    def run_end(self):
        os.unlink(self.experiment_mark)

    def run(self, progress):
        text = "Beginning Simulations"
        log.info("{:=<78}".format(text))

        callbacks = []
        e_plugin = []

        # Order the all
        self.order_by_priority()
        self.run_begin()

        # Create any ExperimentPlugins
        for cls, kwargs in self.experiment_plugin:
            c = cls(self.config)
            c.__dict__.update(kwargs)
            if hasattr(c, 'begin_experiment'):
                log.info("Begin experiment processing for '%s'", c.name)
                c.begin_experiment()
            e_plugin.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for t in self.treatments:
            t.run(e_plugin, callbacks, progress)

        for c in e_plugin:
            if hasattr(c, 'end_experiment'):
                log.info("End Experiment processing '%s'", c.name)
                c.end_experiment()

        for c in reversed(e_plugin):
            if hasattr(c, 'unload'):
                log.debug("Unloading plugin '%s'..." % c.name)
                c.unload()

        self.run_end()

    def analyse(self):
        if self.config.history_class is None:
            log.warning("Post analysis not possible as there is not history class")
            return
        text = "Beginning Analyses"
        log.info("{:=<78}".format(text))

        # for cls, kwargs in self.experiment_plugin:
            # if hasattr(cls, 'analyse'):
                # c = cls(self.config)
                # c.__dict__.update(kwargs)

        for t in self.treatments:
            t.analyse()

    def make_path(self, pth):
        if not os.path.exists(pth):
            log.debug("Making path %s", pth)
            os.makedirs(pth)


class Treatment(object):
    def __init__(self, experiment, name, rcount, **kwargs):
        self.experiment = experiment
        self.sim_class = experiment.config.sim_class
        self.name = name
        self.replicate = None
        self.replicate_count = rcount
        self.extra_args = kwargs
        self.treatment_output_path = os.path.join(
            self.experiment.output_path, self.name)
        self.experiment.make_path(self.treatment_output_path)

    @property
    def treatment_mark(self):
        return os.path.join(self.treatment_output_path, RUNNING)

    def run_begin(self):
        open(self.treatment_mark, 'a').close()

    def run_end(self):
        os.unlink(self.treatment_mark)

    def run(self, e_plugin, e_callbacks, progress=None):
        # Set up and run the treatment_plugin
        t_plugin = []
        callbacks = e_callbacks[:]

        self.run_begin()

        for cls, kwargs in self.experiment.treatment_plugin:
            c = cls(self.experiment.config, self)
            c.__dict__.update(kwargs)

            t_plugin.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for c in chain(e_plugin, t_plugin):
            if hasattr(c, 'begin_treatment'):
                log.debug(
                    "Begin Treatment processing for plugin '%s'" % c.name)
                c.begin_treatment()

        # Run all the replicates
        for i in range(self.replicate_count):
            self.replicate = i
            self.run_replicate(
                i, e_plugin, t_plugin, callbacks[:], progress)

        # Treatment processing
        for c in chain(t_plugin, e_plugin):
            if hasattr(c, 'end_treatment'):
                c.end_treatment()
                log.debug("End Treatment processing for plugin '%s'" % c.name)

        # Let them unload themselves if needed
        for c in reversed(t_plugin):
            if hasattr(c, 'unload'):
                log.debug("unloading plugin '%s'..." % c.name)
                c.unload()

        self.run_end()

    @property
    def running_mark(self):
        return os.path.join(self.replicate_output_path, RUNNING)

    @property
    def complete_mark(self):
        return os.path.join(self.replicate_output_path, COMPLETE)

    @property
    def replicate_output_path(self):
        return os.path.join(self.treatment_output_path, "{:0>3}".format(self.replicate))

    def replicate_run_begin(self):
        self.experiment.make_path(self.replicate_output_path)

        if os.path.exists(self.complete_mark):
            return False

        open(self.running_mark, 'a').close()
        return True

    def replicate_run_end(self):
        os.unlink(self.running_mark)
        open(self.complete_mark, 'a').close()

    def run_replicate(self, r_i, e_plugin, t_plugin, callbacks, progress):
        seed = self.experiment.rand.randint(0, 1 << 32)
        text = "Treatment '%s', replicate %d of %d with seed %s" % (
            self.name, r_i, self.replicate_count, seed)

        if not self.replicate_run_begin():
            log.info("{:-<78}".format("Skipping Completed %s" % text))
            return

        log.info("{:-<78}".format("Beginning %s" % text))


        sim = self.sim_class(seed=seed, treatment=self.name,
                replicate=self.replicate, **self.extra_args)

        sim._begin()

        # Create a history class if we have one
        if self.experiment.config.history_class is None:
            sim.history = None
        else:
            sim.history = self.experiment.config.history_class(self.replicate_output_path, sim)

        r_plugin = []
        for cls, kwargs in self.experiment.replicate_plugin:
            c = cls(self.experiment.config, self)
            c.__dict__.update(kwargs)
            r_plugin.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for c in chain(e_plugin, t_plugin, r_plugin):
            if hasattr(c, 'begin_replicate'):
                log.debug(
                    "begin_replicate processing for plugin '%s'..." % c.name)
                c.begin_replicate(sim)

        sim.run(callbacks, progress)

        for c in chain(r_plugin, t_plugin, e_plugin):
            if hasattr(c, 'end_replicate'):
                log.debug("end_replicate Replicate processing for plugin '%s'..." % c.name)
                c.end_replicate(sim)

        sim._end()

        # This might help shut some stuff down, before running the unloading...
        if sim.history is not None:
            sim.history.close()

        del sim

        for c in reversed(r_plugin):
            if hasattr(c, 'unload'):
                log.debug("unloading plugin '%s'..." % c.name)
                c.unload()

        self.replicate_run_end()

    def analyse(self):
        # for cls, kwargs in self.experiment.treatment_plugin:
            # if hasattr(cls, 'analyse'):
                # c = cls(self.experiment.config, self)
                # c.__dict__.update(kwargs)
                # c.analyse()

        for i in range(self.replicate_count):
            self.replicate = i
            self.analyse_replicate()

    def analyse_replicate(self):
        text = "Treatment '%s', replicate %d of %d" % (
            self.name, self.replicate, self.replicate_count)
        log.info("{:-<78}".format("Analysing %s" % text))

        r_analyses = []
        for cls, kwargs in self.experiment.replicate_plugin:
            if hasattr(cls, 'analyse'):
                c = cls(self.experiment.config, self)
                c.__dict__.update(kwargs)
                r_analyses.append(c)

        hist = self.experiment.config.history_class(self.replicate_output_path)
        for a in r_analyses:
            a.analyse(hist)


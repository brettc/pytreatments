import logging
log = logging.getLogger("experiment")
import os

from itertools import chain
from plugin import TreatmentPlugin, ReplicatePlugin, ExperimentPlugin
import random

RUNNING = "RUNNING"
COMPLETE = "COMPLETE"
SEED = "SEED"


class Interrupt(Exception):
    """Use this to stop an experiment"""
    pass


class Experiment(object):
    def __init__(self, config):
        self.config = config
        self.name = None

        self.treatments = []
        self.current_treatment = None

        self.replicate_plugin = []
        self.treatment_plugin = []
        self.experiment_plugin = []

        # We use this to generates seeds for all of the experiments
        self.rand = random.Random()

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

    # @property
    # def experiment_mark(self):
        # return os.path.join(self.output_path, RUNNING)

    def run_begin(self):
        text = "Experiment:'{}'".format(self.name)
        log.info("{:=^78}".format(text))
        self.output_path = self.config.output_path
        # open(self.experiment_mark, 'a').close()

    def run_end(self):
        text = "Ending Simulations"
        log.info("{:=^78}".format(text))
        # os.unlink(self.experiment_mark)

    def run(self, progress):

        callbacks = []
        e_plugin = []

        # Order everything by the class priority. This sort out dependencies
        # between the different plugins
        self.order_by_priority()
        self.run_begin()

        # Create any Experiment Plugins
        for cls, kwargs in self.experiment_plugin:
            c = cls(self.config)
            c.__dict__.update(kwargs)

            # Internal begin
            c.begin()
            e_plugin.append(c)

            # Run any user begin_experiment
            if hasattr(c, 'begin_experiment'):
                log.info("Begin experiment processing for '%s'", c.name)
                c.begin_experiment()
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for t in self.treatments:
            # Skip to desired treatment
            if self.config.args.treatment is not None:
                if t.name != self.config.args.treatment:
                    continue

            self.current_treatment = t
            t.run(e_plugin, callbacks, progress)

        self.current_treatment = None

        for c in e_plugin:
            if hasattr(c, 'end_experiment'):
                log.info("End Experiment processing '%s'", c.name)
                c.end_experiment()

        for c in e_plugin:
            c.end()

        for c in reversed(e_plugin):
            if hasattr(c, 'unload'):
                log.debug("Unloading plugin '%s'..." % c.name)
                c.unload()

        self.run_end()

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
        self.seeds = [self.experiment.rand.randint(0, 1 << 32)
                      for i in range(self.replicate_count)]

    @property
    def running_mark(self):
        return os.path.join(self.replicate_output_path, RUNNING)

    @property
    def complete_mark(self):
        return os.path.join(self.replicate_output_path, COMPLETE)

    @property
    def replicate_output_path(self):
        return os.path.join(self.treatment_output_path, "{:0>3}".format(self.replicate))

    def run(self, e_plugin, e_callbacks, progress=None):
        self.treatment_text = "Experiment:'{0}' Treatment:'{1}'".format(self.experiment.name, self.name)
        log.info("{:=^78}".format(""))
        log.info("{: ^78}".format(self.treatment_text))

        t_plugin = []
        callbacks = e_callbacks[:]

        self.treatment_output_path = os.path.join(self.experiment.output_path, self.name)

        # We've not run this experiment before
        # self.experiment.make_path(self.treatment_output_path)

        # Run everything
        for cls, kwargs in self.experiment.treatment_plugin:
            c = cls(self.experiment.config, self)
            c.__dict__.update(kwargs)
            t_plugin.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        # Run begin and end to setup plugin for running
        for c in t_plugin:
            c.begin()

        self.run_treatment(e_plugin, t_plugin, callbacks, progress)

        for c in t_plugin:
            c.end()

        # Let them unload themselves if needed
        for c in reversed(t_plugin):
            if hasattr(c, 'unload'):
                log.debug("plugin:'%s' unload" % c.name)
                c.unload()

    def run_treatment(self, e_plugin, t_plugin, callbacks, progress):
        for c in chain(e_plugin, t_plugin):
            if hasattr(c, 'begin_treatment'):
                log.debug("plugin:'%s' begin_treatment" % c.name)
                c.begin_treatment()

        for i in range(self.replicate_count):
            if self.experiment.config.args.replicate is not None:
                if self.experiment.config.args.replicate != i:
                    continue
            self.replicate = i
            self.run_replicate(e_plugin, t_plugin, callbacks[:], progress)

        for c in chain(t_plugin, e_plugin):
            if hasattr(c, 'end_treatment'):
                c.end_treatment()
                log.debug("plugin:'%s' end_treatment" % c.name)

    def run_replicate(self, e_plugin, t_plugin, callbacks, progress):
        seed = self.seeds[self.replicate]
        text = "{0} Rep:{1:0>3}/{2:0>3} Seed:{3:}".format(
            self.treatment_text,
            self.replicate + 1,
            self.replicate_count,
            seed)
        log.info("{:-^78}".format(""))
        log.info("{: ^78}".format(text))

        # Create the replicate plugins
        r_plugin = []
        for cls, kwargs in self.experiment.replicate_plugin:
            c = cls(self.experiment.config, self)
            c.__dict__.update(kwargs)
            r_plugin.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for c in r_plugin:
            c.begin()

        # Is it done?
        if not os.path.exists(self.complete_mark):
            # Are we just doing an analysis?
            if not self.experiment.config.args.analysis:
                self.run_simulation(e_plugin, t_plugin, r_plugin, callbacks, progress, seed)
            else:
                log.info("Not running Simulation (analysis only).")
        else:
            log.info("Simulation has already successfully run.")

        self.analyse_simulation(e_plugin, t_plugin, r_plugin)

        for c in r_plugin:
            c.end()

        # If required, unload the plugins in reverse loading order
        for c in reversed(r_plugin):
            if hasattr(c, 'unload'):
                log.debug("plugin:'%s' unloading..." % c.name)
                c.unload()

    def run_simulation(self, e_plugin, t_plugin, r_plugin, callbacks, progress, seed):
        log.info("{:.^78}".format("Running Simulation"))
        self.experiment.make_path(self.replicate_output_path)
        open(self.running_mark, 'a').close()

        # Finally, we actually create a simulation
        sim = self.sim_class(
            seed=seed,
            treatment=self.name,
            replicate=self.replicate,
            **self.extra_args
        )

        sim._begin()

        # Create a history class if we have one.
        if self.experiment.config.history_class is not None:
            cls = self.experiment.config.history_class
            sim.history = cls(self.replicate_output_path, sim)

        for c in chain(e_plugin, t_plugin, r_plugin):
            c.replicate = self.replicate
            if hasattr(c, 'begin_replicate'):
                log.debug("plugin:'%s' begin_replicate..." % c.name)
                c.begin_replicate(sim)

        # Actually run the simulation. Here is where the action is.
        sim.run(callbacks, progress)

        for c in chain(r_plugin, t_plugin, e_plugin):
            if hasattr(c, 'end_replicate'):
                log.debug("plugin:'%s' end_replicate..." % c.name)
                c.end_replicate(sim)

        sim._end()

        # This might help shut some stuff down, before running the unloading...
        if sim.history is not None:
            sim.history.close()

        # If the history is safely closed, we can now say we're done
        os.unlink(self.running_mark)
        open(self.complete_mark, 'a').close()

    def analyse_simulation(self, e_plugin, t_plugin, r_plugin):
        # Put this warning at the beginning
        log.info("{:.^78}".format(""))
        if self.experiment.config.history_class is None:
            log.warning("{: ^78}".format("No analysis possible as there no history class"))
            return

        if not os.path.exists(self.complete_mark):
            log.info("{: ^78}".format("Can't Analyse Incomplete Simulation"))
            # Can't analyse what ain't there
            for c in chain(e_plugin, t_plugin, r_plugin):
                c.failed_analysis = True
            return

        log.info("{: ^78}".format("Analysing Simulation"))

        # Load the history
        hist = self.experiment.config.history_class(self.replicate_output_path)
        for c in chain(e_plugin, t_plugin, r_plugin):
            if hasattr(c, 'analyse'):
                c.replicate = self.replicate
                c.do_analyse(hist)


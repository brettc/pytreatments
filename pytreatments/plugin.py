import logging
log = logging.getLogger("plugin")

import os

ANALYSED = 'ANALYSED'

class Plugin(object):

    # Default load priority
    priority = 5

    def __init__(self, config):
        self.config = config
        self.treatment = None
        self.replicate = None
        self.output_path = None
        log.debug("Creating Plugin %s", self.name)

    def get_file(self, name, attr='wb'):
        pth = self.get_file_name(name)
        return open(pth, attr)

    def get_file_name(self, name):
        # Only make output folder when needed
        self.make_output_folder()
        pth = os.path.join(self.output_path, name)
        log.info("Acquiring file name '%s'", pth)
        return pth

    def make_output_folder(self):
        if not os.path.exists(self.output_path):
            log.info("Making folder '%s'", self.output_path)
            os.makedirs(self.output_path)

    @property
    def analysed_mark(self):
        self.make_output_folder()
        return os.path.join(self.output_path, ANALYSED)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def experiment_output_path(self):
        basepth = self.config.experiment.output_path
        return os.path.join(basepth, self.name)

    @property
    def treatment_output_path(self):
        basepth = self.treatment.output_path
        return os.path.join(basepth, self.name)

    @property
    def replicate_output_path(self):
        basepth = self.treatment.replicate_output_path
        return os.path.join(basepth, self.name)

    def do_begin_experiment(self):
        # Run any user begin_experiment
        self.output_path = self.experiment_output_path
        if hasattr(self, 'begin_experiment'):
            log.info("Begin experiment processing for '%s'", self.name)
            self.begin_experiment()

    def do_begin_treatment(self, t):
        self.treatment = t
        self.output_path = self.treatment_output_path
        if hasattr(self, 'begin_treatment'):
            log.debug("plugin:'%s' begin_treatment" % self.name)
            self.begin_treatment()

    def do_begin_replicate(self, r):
        self.replicate = r
        self.output_path = self.replicate_output_path
        if hasattr(self, 'begin_replicate'):
            log.debug("plugin:'%s' begin_replicate..." % self.name)
            self.begin_replicate(sim)

    def do_begin_simulation(self, sim):
        if hasattr(self, 'begin_simulation'):
            self.begin_simulation(sim)

    def do_end_simulation(self, sim):
        if hasattr(self, 'end_simulation'):
            self.end_simulation(sim)

    def do_analyse_replicate(self, history):
        if not hasattr(self, 'analyse_replicate'):
            return
        if os.path.exists(self.analysed_mark):
            if not self.config.args.reanalyse:
                log.info("Analysis already complete in '%s'", self.output_path)
                return

        self.analyse_replicate(history)
        open(self.analysed_mark, 'a').close()

    def do_end_replicate(self):
        if hasattr(self, 'end_replicate'):
            log.debug("plugin:'%s' end_replicate..." % self.name)
            self.end_replicate()
        self.replicate = None

    def do_end_treatment(self):
        self.output_path = self.treatment_output_path
        if hasattr(self, 'begin_treatment'):
            log.debug("plugin:'%s' begin_treatment" % self.name)
            self.begin_treatment()
        self.treatment = None


    def do_end_experiment(self):
        self.output_path = self.experiment_output_path
        if hasattr(self, 'end_experiment'):
            log.info("End Experiment processing '%s'", self.name)
            self.end_experiment()




# This allows us to export them to the namespace in the config_loader
plugin_classes = set()


def register_plugin(a):
    global plugin_classes
    plugin_classes.add(a)
    return a

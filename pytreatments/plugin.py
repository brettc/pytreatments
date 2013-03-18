import logging
log = logging.getLogger("plugin")

import os

ANALYSED = 'ANALYSED'


class Plugin(object):

    # Default load priority
    priority = 5

    def __init__(self, config):
        self.config = config
        self.output_path = None

    def get_file(self, name):
        """Makes a file and puts it in the appropriate place"""
        pth = self.get_file_name(name)
        # log.info("creating %s", pth)
        return open(pth, 'wb')

    def get_file_name(self, name):
        pth = os.path.join(self.output_path, name)
        log.info("Acquiring file name '%s'", pth)
        return pth

    def make_output_folder(self):
        if not os.path.exists(self.output_path):
            log.info("Making folder '%s'", self.output_path)
            os.makedirs(self.output_path)

    @property
    def analysed_mark(self):
        return os.path.join(self.output_path, ANALYSED)

    @property
    def name(self):
        return self.__class__.__name__


class ExperimentPlugin(Plugin):
    def __init__(self, config):
        Plugin.__init__(self, config)
        basepth = self.config.experiment.output_path
        self.output_path = os.path.join(basepth, self.__class__.__name__)
        self.make_output_folder()


class TreatmentPlugin(Plugin):
    def __init__(self, config, treatment):
        Plugin.__init__(self, config)
        self.treatment = treatment
        basepth = treatment.treatment_output_path
        self.output_path = os.path.join(basepth, self.__class__.__name__)
        self.make_output_folder()


class ReplicatePlugin(Plugin):
    def __init__(self, config, treatment):
        Plugin.__init__(self, config)
        self.treatment = treatment
        self.replicate = treatment.replicate
        basepth = treatment.replicate_output_path
        self.output_path = os.path.join(basepth, self.__class__.__name__)
        self.make_output_folder()

    def do_analyse(self, history):
        if os.path.exists(self.analysed_mark):
            log.info("Analysis already complete in '%s'", self.output_path)
            return

        self.analyse(history)
        open(self.analysed_mark, 'a').close()

# This allows us to export them to the namespace in the config_loader
plugin_classes = set()


def register_plugin(a):
    global plugin_classes
    plugin_classes.add(a)
    return a

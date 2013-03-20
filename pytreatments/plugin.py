import logging
log = logging.getLogger("plugin")

import os

ANALYSED = 'ANALYSED'


class Plugin(object):

    # Default load priority
    priority = 5

    def __init__(self, config):
        self.config = config
        self.failed_analysis = False
        self.output_path = None

    def get_file(self, name):
        pth = self.get_file_name(name)
        return open(pth, 'wb')

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
        return os.path.join(self.output_path, ANALYSED)

    @property
    def name(self):
        return self.__class__.__name__

    def begin(self):
        pass

    def do_analyse(self, history):
        if not os.path.exists(self.treatment.complete_mark):
            # Can't analyse what ain't there
            self.failed_analysis = True

        if os.path.exists(self.analysed_mark):
            if not self.config.args.reanalyse:
                log.info("Analysis already complete in '%s'", self.output_path)
                return

        self.analyse(history)

    def end(self):
        if not self.failed_analysis:
            open(self.analysed_mark, 'a').close()


class ExperimentPlugin(Plugin):
    def __init__(self, config):
        log.debug("Creating Plugin %s", self.__class__.__name__)
        Plugin.__init__(self, config)
        basepth = self.config.experiment.output_path
        self.output_path = os.path.join(basepth, self.__class__.__name__)

class TreatmentPlugin(Plugin):
    def __init__(self, config, treatment):
        log.debug("Creating Plugin %s", self.__class__.__name__)
        Plugin.__init__(self, config)
        self.treatment = treatment
        basepth = treatment.treatment_output_path
        self.output_path = os.path.join(basepth, self.__class__.__name__)


class ReplicatePlugin(Plugin):
    def __init__(self, config, treatment):
        log.debug("Creating Plugin %s", self.__class__.__name__)
        Plugin.__init__(self, config)
        self.treatment = treatment
        self.replicate = treatment.replicate
        basepth = treatment.replicate_output_path
        self.output_path = os.path.join(basepth, self.__class__.__name__)


# This allows us to export them to the namespace in the config_loader
plugin_classes = set()


def register_plugin(a):
    global plugin_classes
    plugin_classes.add(a)
    return a

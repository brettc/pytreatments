import logging
log = logging.getLogger("plugin")

import os


class Plugin(object):

    # Default load priority
    priority = 5

    def __init__(self, config):
        self.config = config
        self.output_path = None

    def get_file(self, name):
        """Makes a file and puts it in the appropriate place"""
        pth = self.get_file_name(name)
        log.info("creating %s", pth)
        return open(pth, 'wb')

    def get_file_name(self, name):
        pth = os.path.join(self.output_path, name)
        return pth

    @property
    def name(self):
        return self.__class__.__name__


class ExperimentPlugin(Plugin):
    def __init__(self, config):
        Plugin.__init__(self, config)
        self.output_path = self.config.experiment.output_path


class TreatmentPlugin(Plugin):
    def __init__(self, config, treatment):
        Plugin.__init__(self, config)
        self.treatment = treatment
        self.output_path = treatment.output_path


class ReplicatePlugin(Plugin):
    def __init__(self, config, treatment):
        Plugin.__init__(self, config)
        self.treatment = treatment
        self.replicate = treatment.replicate
        self.output_path = treatment.replicate_output_path


# This allows us to export them to the namespace in the config_loader
plugin_classes = set()


def register_plugin(a):
    global plugin_classes
    plugin_classes.add(a)
    return a

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
        self.make_output_path()
        pth = os.path.join(self.output_path, name)
        return pth

    @property
    def name(self):
        return self.__class__.__name__


class ExperimentPlugin(Plugin):
    def __init__(self, config):
        Plugin.__init__(self, config)

    def make_output_path(self):
        self.output_path = self.config.output_path


class TreatmentPlugin(Plugin):
    def __init__(self, config, treatment):
        Plugin.__init__(self, config)
        self.treatment = treatment

    def make_output_path(self):
        if self.output_path is None:
            self.output_path = os.path.join(self.config.output_path, self.treatment.name)
            if not os.path.exists(self.output_path):
                log.debug("Making path %s", self.output_path)
                os.makedirs(self.output_path)


class ReplicatePlugin(Plugin):
    def __init__(self, config, treatment):
        Plugin.__init__(self, config)
        self.treatment = treatment
        self.replicate = treatment.replicate

    def make_output_path(self):
        if self.output_path is None:
            self.output_path = os.path.join(self.config.output_path,
                                            self.treatment.name,
                                            "{:0>3}".format(self.replicate),
                                            )
            if not os.path.exists(self.output_path):
                log.debug("Making path %s", self.output_path)
                os.makedirs(self.output_path)


# This allows us to export them to the namespace in the config_loader
plugin_classes = set()


def register_plugin(a):
    global plugin_classes
    plugin_classes.add(a)
    return a

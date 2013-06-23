import logging
log = logging.getLogger("context")

import plugin


class Context(object):
    def __init__(self, config):
        self.config = config

        ns = {}
        self.load_namespace(ns)
        ns['add_treatment'] = self.add_treatment
        ns['load_plugin'] = self.load_plugin
        ns['seed'] = self.set_seed
        ns['output'] = self.set_output

        # Load the plugin class into the namespace
        for p in plugin.plugin_classes:
            ns[p.__name__] = p

        self.namespace = ns

    def load_namespace(self, ns):
        raise NotImplementedError

    def init(self, pth):
        self.config.init_from_script(pth)

    def set_output(self, pth):
        log.info("The script is setting the output_path to '%s'", pth)
        self.config.set_base_path(pth)

    def set_seed(self, seed):
        log.info("Setting the experiment random seed to %s", seed)
        self.config.experiment.set_seed(seed)

    def add_treatment(self, name, replicates=1, **kwargs):
        # Duplicate the parameters so that they can't be changed
        self.config.experiment.add_treatment(name, replicates, **kwargs)

    def load_plugin(self, cls, **kwargs):
        if cls not in plugin.plugin_classes:
            log.error("Ignoring unknown plugin %s", str(cls))
        else:
            self.config.experiment.load_plugin(cls, kwargs)

import logging
log = logging.getLogger("context")

import plugin


def scripted(method):
    # Don't wrap the function, just record it
    # print method.func_name, method.func_globals
    # print dir(method)
    # script_functions.append(method.func_name)
    method.scripted = True
    return method


class Context(object):
    def __init__(self, config):
        self.config = config
        self.namespace = {}

        # Initialise a namespace dictionary for loading the script. Keys in
        # this dictionary will be available in the namespace of the
        # configuration file
        for name in dir(self):
            attr = getattr(self, name)
            # if type(attr) is types.MethodType and hasattr(attr, 'scripted'):
            # TODO should warn about collisions
            if hasattr(attr, 'scripted'):
                self.namespace[name] = attr

        self.load_namespace()

    def load_namespace(self):
        raise NotImplementedError

    def init(self, pth):
        self.config.init_from_script(pth)

    # -------------------------------------------------
    # Scripted functions available to config file
    @scripted
    def add_treatment(self, name, p, challenges, replicates=1):
        # Duplicate the parameters so that they can't be changed
        self.config.experiment.add_treatment(name, p, challenges, replicates)

    @scripted
    def load_plugin(self, cls, **kwargs):
        if cls not in plugin.plugin_classes:
            log.error("Ignoring unknown plugin %s", str(cls))
        else:
            self.config.experiment.load_plugin(cls, kwargs)

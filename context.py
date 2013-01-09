import logging
log = logging.getLogger("context")

import parameters
import plugin
import plugins
import booltree
import binding
import challenge


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

        self.namespace['parameters'] = parameters.Parameters

        for k, v in booltree.ops.items():
            self.namespace[k] = k

        # We need to add the agent classes too...
        for cls in binding.all_bindings:
            self.namespace[cls.__name__] = cls

        # We need to add the agent classes too...
        for cls in plugin.plugin_classes:
            self.namespace[cls.__name__] = cls

        for cls in challenge.challenge_classes:
            self.namespace[cls.__name__] = cls

        for cls in challenge.cue_classes:
            self.namespace[cls.__name__] = cls

        for cls in challenge.state_classes:
            self.namespace[cls.__name__] = cls

        self.defaults = {}

    def init(self, pth):
        self.config.init_from_script(pth)

    # -------------------------------------------------
    # Scripted functions available to config file
    @scripted
    def set_defaults(self, **kwargs):
        for k, v in kwargs.items():
            log.info("setting default of '%s' to %s", k, v)
            self.defaults[k] = v

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

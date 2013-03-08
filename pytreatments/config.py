import logging
log = logging.getLogger("config")
import os
import shutil
from experiment import Experiment


class Configuration(object):
    """This holds the user configuration info"""

    def __init__(self, sim_class, history_class, args, name=None):
        self.sim_class = sim_class
        self.history_class = history_class
        self.args = args
        self.base_path = None
        self.script_path = None
        self.name = name
        self.experiment = Experiment(self)

    def set_name_from_script(self, pth):
        base_path, name = os.path.split(pth)
        name, ext = os.path.splitext(name)
        self.base_path = base_path
        self.experiment.name = name

    def set_base_path(self, pth):
        # Script can override this
        self.base_path = pth

    def init(self):
        """Call this one if you're doing it programmatically"""

        # Modify the base_path if we're told to
        if self.args.output is not None:
            self.base_path = self.args.output

        self.base_path = os.path.expanduser(self.base_path)
        self.base_path = os.path.normpath(self.base_path)
        if not os.path.exists(self.base_path):
            log.error("Base path '%s' does not exist", self.base_path)
            raise RuntimeError

        self.make_output(self.experiment.name + '.output')
        self.init_logger(self.output_path)

        if self.script_path:
            # We're going to stick a copy of the script into the output folder.
            # This is good for referring to later
            shutil.copy(self.script_path, self.output_path)

    def make_output(self, pth):
        pth = os.path.join(self.base_path, pth)

        if os.path.exists(pth):
            if os.path.isdir(pth):
                if self.args.clean:
                    log.info("Removing existing folder '%s'", pth)
                    shutil.rmtree(pth)
            else:
                log.error("Cannot create folder '%s'", pth)
                raise RuntimeError

        if not os.path.exists(pth):
            os.mkdir(pth)
            log.info("Created folder '%s'", pth)

        self.output_path = pth
        log.info("Setting output folder to '%s'", self.output_path)

    def init_logger(self, pth):
        log_path = os.path.join(pth, "log.txt")
        handler = logging.FileHandler(log_path, 'a')
        formatter = logging.Formatter(
            "%(levelname)-8s | %(asctime)s | %(name)-15s | %(message)s")
        handler.setFormatter(formatter)

        # Actually, let's keep it trim...
        handler.setLevel(logging.WARNING)
        logging.getLogger("").addHandler(handler)
        logging.getLogger("reporting").addHandler(handler)

        log.info("Full output log can be found in '%s'", log_path)

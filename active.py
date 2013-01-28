"""A mechanism for having globally activated parameter

It's saves passing stuff around all the time
"""
import logging
log = logging.getLogger('active')

sim = None
param = None


def set_active(s):
    global sim, param
    if sim is not None:
        raise RuntimeError
    sim = s
    param = sim.parameters


def clear_active():
    global sim, param
    sim = None
    param = None

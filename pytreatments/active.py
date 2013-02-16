"""A mechanism for having globally activated parameter

It's saves passing stuff around all the time
"""
import logging
log = logging.getLogger('active')

sim = None


def set_active(s):
    global sim
    if sim is not None:
        raise RuntimeError
    sim = s


def clear_active():
    global sim
    sim = None

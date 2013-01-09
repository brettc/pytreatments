import logging
log = logging.getLogger("parameters")

import binding


def lchar(x):
    return chr(x + ord('a'))


def uchar(x):
    return chr(x + ord('A'))


class ParametersError(Exception):
    pass


class Parameters(object):

    # A bunch of defaults
    mutation_rate = .01

    reg_gene_count = 5
    sub_count = 2

    cue_shapes = 2
    reg_shapes = 3
    out_shapes = 1

    sweep = True
    pop_size = 100
    max_steps = 10000

    binding = None

    def __init__(self, **kwargs):

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                log.warning("'%s' is not a valid setting", k)

        if self.binding is None:
            self.binding = binding.random_binding()

        self._calc_sizes()
        self.binding._generate(self)

    def __repr__(self):
        return \
            "<Parameters"\
            ": popN:{0.pop_size}"\
            ", geneN:{0.gene_count}"\
            ", subN:{0.sub_count}"\
            ", mrate:{0.mutation_rate}"\
            ", signals:{1}"\
            ">".format(self, self.signals_to_string())

    def _calc_sizes(self):
        # Calculate the total number of elements given the overlap
        # An example, with an overlap of 2, looks like this:
        # cue_range [ 0 1 2 3 ]
        # sub_range [ 0 1 2 3 4 5 ]
        # pub_range         [ 4 5 6 7 8 9 10 ]
        # out_range             [ 6 7 8 9 10 ]
        #
        # sub_space.shape_count = 6
        # pub_space.shape_count = 7
        # overlap = 2
        # In this case, the network can only produce 2 shapes that will
        # self-regulate 4 & 5. <4 are external binding >5 are structural

        self.sub_shapes = self.cue_shapes + self.reg_shapes

        self.signal_count = self.cue_shapes + self.reg_shapes + \
            self.out_shapes

        self.sub_range = 0, self.cue_shapes + self.reg_shapes
        self.reg_range = self.cue_shapes, self.cue_shapes + self.reg_shapes
        self.pub_range = self.cue_shapes, self.cue_shapes + \
            self.reg_shapes + self.out_shapes
        self.cue_range = 0, self.cue_shapes
        self.out_range = self.sub_range[1], self.pub_range[1]

        self.gene_count = self.reg_gene_count + self.out_shapes

    def signals_to_string(self, signals=None):
        x = []
        if signals is None:
            signals = [1] * self.signal_count
        assert len(signals) == self.signal_count
        for i, e in enumerate(signals):
            if i == self.cue_range[1]:
                x.append('|')
            elif i == self.reg_range[1]:
                x.append('|')

            c = uchar(i) if e else '-'
            x.append(c)
        return "".join(x)

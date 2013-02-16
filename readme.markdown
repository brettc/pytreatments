# pytreatments: an experimental simulation framework

I use this framework to aid in running a simulation like an experiment, under different "treatments", or parameter sets. It aids in gathering statistics about what went on in each run, and over the experiment as a whole. It only works with simulations that have discrete time steps.

I've built it to work under MacOS. It may work elsewhere (perhaps with a little tweaking). 

It provides the following:

* Simple python scripting for configuring simulations and different treatments

* Produces a sensible hierarchy of output for the different treatments, and for each replicates

* A plugin framework for gathering information as the simulations run.

* More to come...

## Test Usage

Try typing in the following

    python run_experiment.py script1.py
    python run_experiment.py script2.py

## Where it is being used:

<https://github.com/brettc/epistemic-landscapes>

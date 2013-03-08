# pytreatments: a simulation framework

I use this framework to aid in running a simulation like an experiment, under different "treatments", or parameter sets. It can gather statistics about what went on in each run, for each treatment, and over the experiment as a whole. It puts them all in a nice folder structure. You can plug in various bits as it is running too. If you use the history feature, you can add analyses after the simulations have run. It works with simulations that have discrete time steps.

I've built it to work under MacOS. It may work elsewhere (perhaps with a little tweaking). 

It provides the following:

* Simple python scripting for configuring simulations and different treatments

* A sensible hierarchy of output for the different treatments, and for each replicates

* A plugin framework for gathering information as the simulations run.

* Gather history as you go and analyse it all after the simulations have finished.

## Test Usage

Try typing in the following

    python run_experiment.py script1.py
    python run_experiment.py script2.py

## Where it is being used:

<https://github.com/brettc/epistemic-landscapes>

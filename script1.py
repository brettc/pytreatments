# This should be invoked by python run_experiment.py <script>

t1 = parameters(name='bob', cycles=10)
t2 = parameters(name='jim', cycles=10)

add_treatment('treatment1', replicates=5, params=t1)
add_treatment('treatment2', replicates=5, params=t2)

load_plugin(simple_capture)


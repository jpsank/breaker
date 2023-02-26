from itertools import count
from statistics import mean

# Population parameters
population_size: int = 100
reset_on_extinction: bool = True

# Rule parameters
rule_alphabet = lambda: "AUGC" + ''.join(map(str, range(0, last_rule_id))) + "|"

# Genome parameters
seq_max_length: int = 100
seq_pipe_rate = 0.1
seq_nucl_rate = 0.6
seq_nonterm_rate = 0.3
seq_insert_prob: float = 0.1
seq_delete_prob: float = 0.1
seq_swap_prob: float = 0.1
rule_mutate_replace_prob: float = 0.1
rule_add_prob: float = 0.1
rule_del_prob: float = 0.1

# Compatibility threshold
compat_threshold_init: float = 3.0
compat_threshold_modifier: float = 0.1
compat_threshold_min: float = 0.5

# Species parameters
target_num_species: int = 20
species_fitness_func = mean
num_elite_species: int = 1
stagnation_threshold: int = 15

# ID counters
last_rule_id: int = 0
last_genome_id: int = 0
last_spieces_id: int = 0


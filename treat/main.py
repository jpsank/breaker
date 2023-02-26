# Author: Julian Sanker
# Date: 2022-12-26
# Description: Genetic algorithm for grammar induction

from dataclasses import dataclass, field
from datetime import datetime
import random
import config


############################################################################################################
########################################## Data Classes ####################################################
############################################################################################################

@dataclass
class Rule:
    id: int
    seq: str

    def mutate(self):
        seq = ""
        for ch in self.seq:
            if random.random() < config.rule_mutate_insert_prob:
                seq += random.choice(config.rule_alphabet())
            if random.random() < config.rule_mutate_delete_prob:
                continue
            if random.random() < config.rule_mutate_swap_prob:
                seq += random.choice(config.rule_alphabet())
            if random.random() < config.rule_mutate_replace_prob:
                seq += random.choice(config.rule_alphabet())
        self.seq = seq

    @staticmethod
    def crossover(a: 'Rule', b: 'Rule') -> 'Rule':
        i = 0
        seq = ""
        while i < len(a.seq) and i < len(b.seq):
            seq += a.seq[i] if random.random() > 0.5 else b.seq[i]
            i += 1
        if i < len(a.seq):
            seq += a.seq[i:]
        elif i < len(b.seq):
            seq += b.seq[i:]
        config.last_rule_id += 1
        return Rule(id=config.last_rule_id, seq=seq)
    
    @staticmethod
    def distance(a: 'Rule', b: 'Rule') -> float:
        assert a.id == b.id, "Cannot compare non-homologous rules"
        maxlen, minlen = (len(a.seq), len(b.seq)) if len(a.seq) > len(b.seq) else (len(b.seq), len(a.seq))
        d = 0
        for i in range(minlen):
            d += 1 if a.seq[i] != b.seq[i] else 0
        d += maxlen - minlen
        return d / maxlen


@dataclass
class Genome:
    id: int
    rules: 'dict[int, Rule]'
    
    def __mutate_add_rule(self):
        rule = Rule.new()
        self.rules[rule.id] = rule
    
    def __mutate_del_rule(self):
        if len(self.rules) > 0:
            del self.rules[random.choice(list(self.rules.keys()))]
    
    def mutate(self):
        # "Structural" mutations
        if random.random() < config.rule_add_prob:
            self.__mutate_add_rule()
        if random.random() < config.rule_del_prob:
            self.__mutate_del_rule()

        # Pointwise mutations
        for rule in self.rules.values():
            rule.mutate()
    
    @staticmethod
    def crossover(a: 'Genome', b: 'Genome') -> 'Genome':
        rules = {}
        for id in set(a.rules.keys()).union(b.rules.keys()):
            if id in a.rules and id in b.rules:
                rules[id] = Rule.crossover(a.rules[id], b.rules[id])
            elif id in a.rules:
                rules[id] = a.rules[id]
            elif id in b.rules:
                rules[id] = b.rules[id]
        config.last_genome_id += 1
        return Genome(id=config.last_genome_id, rules=rules)

    @staticmethod
    def distance(a: 'Genome', b: 'Genome') -> float:
        d = 0
        ids = set(a.rules.keys()).union(b.rules.keys())
        for id in ids:
            if id in a.rules and id in b.rules:
                d += Rule.distance(a.rules[id], b.rules[id])
            else:
                d += 1
        return d / len(ids)

@dataclass  
class Organism:
    genome: Genome
    fitness: float = None
    species_id: int = None

    @staticmethod
    def crossover(a: 'Organism', b: 'Organism') -> 'Organism':
        return Organism(genome=Genome.crossover(a.genome, b.genome))


@dataclass
class Species:
    id: int
    mascot: Organism
    representatives: 'set[Organism]' = field(default_factory=set)

    # Statistics
    created_at: int = 0
    last_improved: int = 0
    fitness: float = 0
    best_fitness: float = 0
    fitness_history: 'list[float]' = field(default_factory=list)

    def get_fitness(self) -> float:
        return config.species_fitness_func([o.fitness for o in self.representatives])

    def __post_init__(self):
        self.add(self.mascot)

    def add(self, organism: Organism):
        assert organism.species_id is None, "Cannot add organism to multiple species"
        organism.species_id = self.id
        self.representatives.add(organism)
    
    def remove(self, organism: Organism):
        assert organism != self.mascot, "Cannot remove mascot from species"
        organism.species_id = None
        self.representatives.remove(organism)

    def set_mascot(self, organism: Organism):
        assert organism.species_id == None or organism.species_id == self.id, "Cannot set mascot to organism in another species"
        if organism.species_id == None:
            self.add(organism)
        self.mascot = organism
    
    def reset(self):
        for organism in self.representatives:
            organism.species_id = None
        self.mascot = None
        self.representatives.clear()


def __get_dist_w_cache(a: Genome, b: Genome, cache: 'dict[tuple[int, int], float]') -> float:
    """ Get the distance between two genomes, using cache for efficiency. """
    dist = cache.get((a.id, b.id))
    if dist is None:
        # Distance is not already computed.
        dist = Genome.distance(a, b)
        cache[a.id, b.id] = dist
        cache[b.id, a.id] = dist
    return dist

@dataclass
class Population:
    organisms: 'dict[int, Organism]'
    species: 'dict[int, Species]' = field(default_factory=dict)
    step: int = 0
    compat_threshold: float = config.compat_threshold_init

    # Statistics
    fittest: Organism = None

    def speciate(self):
        # Create a cache for efficiency
        distance_cache = {}
        distance = lambda a, b: __get_dist_w_cache(a.genome, b.genome, cache=distance_cache)

        # Reset species and assign new mascots
        unspeciated = list(self.organisms.values())
        for species in self.species.values():
            # The new mascot is the genome closest to the current mascot.
            unspeciated.remove(new_mascot := min(unspeciated, key=lambda a: distance(species.mascot, a)))
            species.reset()
            species.set_mascot(new_mascot)

        # Assign each organism to a species
        for organism in unspeciated:
            # Find the closest species
            closest_species = min(self.species.values(), key=lambda species: distance(organism, species.mascot))

            # If the organism is close enough to the species, add it to the species.
            if distance(organism, closest_species.mascot) < self.compat_threshold:
                closest_species.add(organism)
            else:
                # Otherwise, create a new species.
                config.last_spieces_id += 1
                self.species[organism.species_id] = Species(id=config.last_spieces_id, mascot=organism)

    def update_species_stats(self):
        # Update species statistics
        for s in self.species.values():
            s.fitness = s.get_fitness()
            s.fitness_history.append(s.fitness)
            if s.fitness > s.best_fitness:
                s.best_fitness = s.fitness
                s.last_improved = self.step

    def check_stagnation(self):
        # Update species statistics
        self.update_species_stats()

        # Sort species by ascending fitness
        species = sorted(self.species.values(), key=lambda s: s.fitness)

        # Save the best species
        if config.num_elite_species > 0:
            species = species[:-config.num_elite_species]

        # Remove the worst species
        for s in species:
            if self.step - s.last_improved > config.stagnation_threshold:
                for o in s.representatives:
                    del self.organisms[o.genome.id]
                del self.species[s.id]

    def adjust_compat_threshold(self):
        diff = len(self.species) - config.target_num_species
        self.compat_threshold += (diff / config.population_size) * config.compat_threshold_modifier
        self.compat_threshold = max(self.compat_threshold, config.compat_threshold_min)


############################################################################################################
####################################### Random Initializers ################################################
############################################################################################################

def random_seq(length: int = 8) -> str:
    return ''.join(random.choices(config.rule_alphabet(), k=length))

def random_rule() -> Rule:
    config.last_rule_id += 1
    return Rule(id=config.last_rule_id, seq=random_seq())

def random_genome() -> Genome:
    config.last_genome_id += 1
    return Genome(
        id=config.last_genome_id,
        rules={rule.id: rule for rule in (random_rule() for _ in range(random.randint(1, 8)))}
        )

def random_organism() -> Organism:
    return Organism(genome=random_genome())

def random_population() -> Population:
    return Population(
        organisms={organism.genome.id: organism for organism in (random_organism() for _ in range(config.population_size))},
        )


############################################################################################################
############################################# Simulation ###################################################
############################################################################################################

@dataclass
class Simulation:
    population: Population

    def evaluate(self, fitness_func):
        for organism in self.population.organisms.values():
            organism.fitness = fitness_func(organism.genome)
            if self.population.fittest is None or organism.fitness > self.population.fittest.fitness:
                self.population.fittest = organism

    def reproduce(self):
        # Pre-condition: Species have been speciated and statistics updated.

        species = list(self.population.species.values())
        total_fitness = sum(s.fitness for s in species)

        next_gen_organisms = {}
        for s in species:
            # Compute spawn amount
            num_offspring = round(s.fitness / total_fitness * config.population_size)
            for _ in range(num_offspring):
                # Select parents
                parent1, parent2 = random.choices(s.representatives, weights=[o.fitness for o in s.representatives], k=2)

                # Create child
                child = Organism.crossover(parent1, parent2)
                child.genome.mutate()

                # Add child to population
                next_gen_organisms[child.genome.id] = child
        
        self.population.organisms = next_gen_organisms

    def next_generation(self):
        self.population.check_stagnation()
        if len(self.population.species) == 0:
            # If all species have gone extinct, randomly initialize a new population.
            self.population = random_population()
            return
        self.reproduce()
        self.population.adjust_compat_threshold()
        self.population.speciate()
        self.population.step += 1
    
    def run(self, fitness_func, num_generations: int = 10000):
        for _ in range(num_generations):
            self.evaluate(fitness_func)
            print(self.population.fittest.genome.rules)
            self.next_generation()


############################################################################################################
################################################ Main ######################################################
############################################################################################################

if __name__ == '__main__':
    sim = Simulation(random_population())
    sim.run(fitness_func=lambda genome: 1 / len(genome.rules), num_generations=10000)
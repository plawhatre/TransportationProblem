from random import choice, choices, random
from typing import List, Tuple
import numpy as np
from data_container import DataContainer, DataObj

class GeneticAlgorithm:
    """ Class for Genetic Algorithm
    """
    def __init__(self, n_chromo: int, data_container: DataContainer, limit:float, cross: int=1, mutation_prob=0.05) -> None:
        """ Constructor for Genetic Algorithm
        Args
        ----
        n_chromo : Number of chromosomes
        data_container :  data in DataContainer object 
        limit : space constraint
        cross : crossover points
        mutation_prob :  Probability of mutation
        """
        self.n_obj = len(data_container)
        self.n_chromo = n_chromo
        self.data_container = data_container
        self.limit = limit
        self.cross = cross
        self.mutation_prob = mutation_prob
        self.generate_population()

    def is_constrained(self, chromosome: List[int]) -> bool:
        """ Check whether the population respects constraint or not
        Returns
        -------
        boolean value if the constraint is respected
        """
        if self.limit < sum(chromosome):
            return True
        else:
            return False   

    def generate_chromosome(self) -> List[int]:
        """ Generate Chromosomes
        Returns
        -------
        Chromosome
        """
        return choices([0,1], k=self.n_obj)

    def generate_population(self) -> None:
        """ Generate population of chromosomes that are space constrained
        """
        self.population = []
        for _ in range(self.n_chromo):
            while True:
                chromosome = self.generate_chromosome()
                if self.is_constrained(chromosome):
                    self.population.append(chromosome)
                    break  

    @property
    def selected_names(self) -> List[List[str]] :
        """
        Returns
        -------
        names: It returns the names of the products for each chromosome
        """
        names = [[data_obj.name for data_obj in self.data_container.get_val_bindices(chromo)] 
        for chromo in self.population]
        return names

    @property
    def selected_profits(self) -> List[List[int]] :
        """
        Returns
        -------
        profits: It returns the profits on the products for each chromosome
        """
        profits = [[data_obj.profit for data_obj in self.data_container.get_val_bindices(chromo)] 
        for chromo in self.population]
        return profits

    @property
    def selected_spaces(self) -> List[List[float]] :
        """
        Returns
        -------
        spaces: It returns the spaces occupied by the products for each chromosome
        """
        spaces = [[data_obj.space for data_obj in self.data_container.get_val_bindices(chromo)] 
        for chromo in self.population]
        return spaces

    @property
    def selected_items(self) -> List[List[DataObj]] :
        """
        Returns
        -------
        items: It returns the items of the products for each chromosome
        """
        items = [[data_obj for data_obj in self.data_container.get_val_bindices(chromo)] 
        for chromo in self.population]
        return items
 
    def __fitness(self) -> List[int]:
        """ Computes the fitness of each chromosome in population
        Note
        ----
        Fitness means collective profit for each chromosome in our problem
        """
        return [sum(chromo_profit_list) 
        for chromo_profit_list in self.selected_profits]

    def __sort(self, lst_fit: List[int]) -> None:
        """ Sort Chromosomes based on fitness
        """
        self.population = [self.population[i]
        for i in np.argsort(lst_fit)[::-1]]

    def __cross(self, p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
        """ N point crossover
        Args
        ----
        p1 : Parent Chromosome 1
        p2 : Parent Chromosome 2

        Returns
        ----
        c1 : Child Chromosome 1
        c2 : Child Chromosome 2
        """
        mutation_point = 0
        c1 = [0 for _ in range(self.n_obj)]
        c2 = [0 for _ in range(self.n_obj)]

        try : 
            for i in range(self.cross):
                mutation_point_new = choice(range(mutation_point, self.n_obj))
                if i%2 == 1:
                    c1[mutation_point:mutation_point_new] = p1[mutation_point:mutation_point_new]
                    c2[mutation_point:mutation_point_new] = p2[mutation_point:mutation_point_new]
                else:
                    c2[mutation_point:mutation_point_new] = p1[mutation_point:mutation_point_new]
                    c1[mutation_point:mutation_point_new] = p2[mutation_point:mutation_point_new]
                
                mutation_point_new = mutation_point
        except:
            mutation_point = choice(range(mutation_point, self.n_obj))
            c1[0:mutation_point] = p1[0:mutation_point]
            c2[0:mutation_point] = p2[0:mutation_point]   

            c1[mutation_point:] = p2[mutation_point:]
            c2[mutation_point:] = p1[mutation_point:]  

        return c1, c2

    def __flip(self,c: List[int]) -> List[int]:
        """ Flip the gene in the chromosome with prob.
        Args
        ----
        c: Chromosome
        
        Returns
        -------
        flip_c : Flipped Chromosome
        """
        flip_c = [i if self.mutation_prob < random() else not(i) for i in c]
        return flip_c

    def selection_ops(self) -> List[float]:
        """ Select the strongest chromosomes
        Returns
        -------
        population_fitness : individual chromo's probability 
        """
        fit = self.__fitness()
        prob_i = [f/sum(fit) if sum(fit) !=0 else 0 for f in fit]
        population_fitness = list(map(lambda x: x*self.n_chromo, prob_i))
        return population_fitness

    def crossover_ops(self, population_fitness: List[int]) -> None:
        """ Crossover of the chromosomes as per their fitness
        Args
        ----
        population_fitness  : fitness of individual chromo
        """
        self.__sort(population_fitness)

        # kill weak chromosomes
        self.population = self.population[:self.n_chromo]
        
        n_pairs = self.n_chromo // 2
        for pair in range(n_pairs):
            while True:
                c1, c2 = self.__cross(self.population[2*pair], self.population[2*pair+1])
                if self.is_constrained(c1) and self.is_constrained(c2):
                    self.population.append(c1)
                    self.population.append(c2)
                    break

    def mutation_ops(self) -> None:
        """ Mutate chromosomes in population
        """
        for i, chromo in enumerate(self.population):
            while True:
                chromosome = self.__flip(chromo)
                if self.is_constrained(chromosome):
                    self.population[i] = chromosome
                    break 

    def population_cleanup(self) -> None:
        """
        Final evaluation after mutation in last generation 
        """
        self.__sort(self.selection_ops())
        self.population = self.population[:self.n_chromo]

    @staticmethod
    def can_terminate(scores: List, eps: float=0.1, eps_count: int=5) -> bool:
        """ Boolean ouput to terminiate algo based on epsilon and eps_count
        Args
        ----
        score: list of scores for generations so far
        eps: tolerance for difference in score
        eps_count: minimum count of generations for which fitness diff is small
        """
        diff = np.diff(scores)
        count = sum(diff > eps)
        return True if count>eps_count else False

    def generation(self, i: int) -> int:
        """ Single pass in Genetic algorithm
        Args
        ----
        i: generation number
        Returns
        -------
        Total Fitness of the chromosomes of current generation
        """
        print('-'*80)
        # Stage 1
        print(f"\t\tGeneration {i}, Stage 1: Selection in progress")
        population_fitness = self.selection_ops()
        # Stage 2
        print(f"\t\tGeneration {i}, Stage 2: Crossover in progress")
        self.crossover_ops(population_fitness)
        # Stage 3
        print(f"\t\tGeneration {i}, Stage 3: Mutation in progress")
        # self.mutation_ops()
        print('-'*80)

        return sum(population_fitness)

    def start_simutation(self, n_gens: int, eps: float=0.1, eps_count: int=5) -> List[int]:
        """ Run simulation for n_gens
        Args
        ----
        n_gens : Number of generations
        eps: tolerance for difference in score
        eps_count: minimum count of generations for which fitness diff is small
        
        Returns
        -------
        scores: List of score for each generation
        """
        scores = [] 
        for i in range(n_gens):
            print(f"Generation {i} in progress......") 
            score = self.generation(i)
            print('\n')
            print('*-'*25, '*')
            print(f"Generation {i} scored {score}") 
            print('*-'*25, '*\n')
            scores.append(score)

            if GeneticAlgorithm.can_terminate(scores, eps, eps_count):
                break
        
        self.population_cleanup()
        print('\nAlgorithm has terminated !!')
        
        print('OPTIMAL SOL\n')
        self.print_optimal_solution()
        return scores

    def print_optimal_solution(self) -> None:
        """
        Print optimal solutions
        """
        for data_obj in self.data_container.get_val_bindices(self.population[0]):
            print(data_obj)
        
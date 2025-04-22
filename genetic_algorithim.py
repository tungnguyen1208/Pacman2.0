import pygame as pyg
import pacman
from pacman import Game_Setup, Game, Player, Pacman, Ghost, Maze, Pacman_Game, Genetic_Game
import time
import random
import matplotlib.pyplot as plt


pyg.init()

#contain all the functions related to dealing with the genetic algorithm
class Genetics():

    def __init__(self):
        #basic setup needed to run the visuals for the game
        self.clock = pyg.time.Clock()
        self.SETUP = Game_Setup()
        self.test_gene = 'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD'
        self.population_size = 100
        self.gene_length = 10000
        self.mutation_rate = 0.02
        self.generations = 100




    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            gene = ''.join(random.choice('LRUD') for _ in range(self.gene_length))
            population.append(gene)
        return population
    
    def select_parents(self, population, fitness_scores):
        sorted_population = [gene for _, gene in sorted(zip(fitness_scores, population), reverse=True)]
        return sorted_population[:2]
    
    def mutate(self, gene):
        gene_list = list(gene)
        for i in range(len(gene_list)):
            if random.random() < self.mutation_rate:
                gene_list[i] = random.choice('LRUD')
        return ''.join(gene_list)
    
    def crossover(self, parent1, parent2):
        crossover_point = random.randint(0, self.gene_length - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    

    def run_genetic_algorithm(self):
        start_time = time.time()

        population = self.initialize_population()
        best_fitness_scores = []
        average_fitness_scores = []

        plt.ion()
        fig, ax = plt.subplots()
        line1, = ax.plot(best_fitness_scores, label='Best Fitness')
        line2, = ax.plot(average_fitness_scores, label='Average Fitness')
        ax.legend()

        best_all_time_score = 0
        best_all_time_gene = ''

        for generation in range(self.generations):
            fitness_scores = [self.fitness(self.run_game(gene, is_displaying=False)) for gene in population]
            
            best_fitness = max(fitness_scores)
            average_fitness = sum(fitness_scores) / len(fitness_scores)
            best_fitness_scores.append(best_fitness)
            average_fitness_scores.append(average_fitness)

            # new best move found
            if best_fitness > best_all_time_score:
                best_all_time_score = best_fitness
                best_all_time_gene = population[fitness_scores.index(max(fitness_scores))]
                with open('best_gene.txt', 'a') as file:
                    file.write(f'Score: {best_fitness}, NEW BEST GENE: {best_all_time_gene} \n')

            # Elitism: carry the best genes to the next generation
            elite_size = 2
            sorted_population = [gene for _, gene in sorted(zip(fitness_scores, population), reverse=True)]
            new_population = sorted_population[:elite_size]

            while len(new_population) < self.population_size:
                parent1, parent2 = self.select_parents(population, fitness_scores)
                child1, child2 = self.crossover(parent1, parent2)
                new_population.append(self.mutate(child1))
                if len(new_population) < self.population_size:
                    new_population.append(self.mutate(child2))
            
            population = new_population

            line1.set_ydata(best_fitness_scores)
            line1.set_xdata(range(len(best_fitness_scores)))
            line2.set_ydata(average_fitness_scores)
            line2.set_xdata(range(len(average_fitness_scores)))
            ax.relim()
            ax.autoscale_view()
            ax.set_xlabel('Generation')
            ax.set_ylabel('Fitness Score')
            plt.draw()
            plt.pause(0.0001)
            elapsed_time = time.time() - start_time
            print(f'Generation: {generation}, Best Fitness: {best_fitness}, Average Fitness: {average_fitness}, Elapsed Time: {elapsed_time:.2f} seconds')
            # Display elapsed time on the graph
            if 'elapsed_time_text' not in locals():
                elapsed_time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
            elapsed_time_text.set_text(f'Elapsed Time: {elapsed_time:.2f} seconds')

        plt.ioff()
        plt.show()

        best_gene = population[fitness_scores.index(max(fitness_scores))]
        
        return best_gene




    #run a game with a gene and return the end game object after game is over
    def run_game(self, gene, is_displaying):
        game = Genetic_Game(self.SETUP, self.clock, gene, is_displaying)

        #max time to run in secoonds
        # Main game loop
        while game.game_over_bool != True and game.ticks['game'] < len(gene):
            # Update the game
            game.update()
            #update the display
            if is_displaying:
                pyg.display.flip()
                self.clock.tick(60)
        
        return game
    
    #run a game with a premade game object
    def run_specific_game(self, game,  gene, is_displaying):
        game.complete_restart(gene)
        #max time to run in secoonds
        # Main game loop
        while game.game_over_bool != True and game.ticks['game'] < len(gene):
            # Update the game
            game.update()
            #update the display
            if is_displaying:
                pyg.display.flip()
                self.clock.tick(60)
        
        return game
    
    def run_many_games(self, gene, num_games, is_displaying):
        game = Genetic_Game(self.SETUP, self.clock, gene, is_displaying)

        for _ in range(num_games):
            #max time to run in secoonds
            # Main game loop
            while game.game_over_bool != True and game.ticks['game'] < len(gene):
                # Update the game
                game.update()
                #update the display
                if is_displaying:
                    pyg.display.flip()
                    self.clock.tick(60)

            #reset the game
            game.complete_restart(gene)
        
        return game

    #fitness function which takes in a pacman game and uses the end state of the game to determine how well the pacman did
    def fitness(self, game):
        #constants for tuning weight of parameters
        k_score = 0
        k_time = 0.2
        k_pellets = 10
        #wins are highly desired especially in the beginning where all I really want is a pacman that wins
        k_win = 100000000000

        #collect info from the game
        #final pacman score
        score = game.player.score
        #time alive
        time = game.ticks['game']
        #pellets eaten
        pellets = game.maze.pellets_eaten()
        #win or loss
        win = 1 if game.won else 0

        return k_score * score + k_time * time + k_pellets * pellets + k_win * win
    


    '''
    
    DEBUGGING AND TEST FUNCTIONS FOR THE GA
    
    '''
    def genetic_test(self, gene):
        # Create the game
        clock = pyg.time.Clock()
        best_score = 0
        is_displaying = False
        for i in range(100):
            game = Genetic_Game(self.SETUP, clock, gene, is_displaying)
            # Main game loop
            while game.game_over_bool != True:

                # Update the game
                game.update()

                #update the display
                if is_displaying:
                    pyg.display.flip()
                    clock.tick(60)

            if game.player.score > best_score:
                best_score = game.player.score

        return game.player.score

    def speed_test(self, gene):
        game = Genetic_Game(self.SETUP, self.clock, self.test_gene, is_displaying=False)
        fitness_scores = [self.fitness(self.run_specific_game(game, gene, is_displaying=False)) for _ in range(200)]



    @staticmethod
    def read_genes(score):
        with open('best_gene.txt', 'r') as file:
            for line in file:
                if 'NEW BEST GENE' in line:
                    parts = line.strip().split(', NEW BEST GENE: ')
                    gene_score = float(parts[0].split('Score: ')[1])
                    gene_string = parts[1]
                    if gene_score > score:
                        return gene_string
        return None



#unit tests
def test_1():
    pg = Pacman_Game()
    gen = Genetics()
    pg.genetic_test(gen.test_gene)

def test_2():
    gen = Genetics()
    gen.genetic_test(gen.test_gene)

def test_3():
    gen_alg = Genetics()
    print(gen_alg.fitness(gen_alg.run_game(gen_alg.test_gene, is_displaying=False)))

def test_4():
    gen_alg = Genetics()
    print(gen_alg.run_genetic_algorithm())

def test_5(gene_score):
    gen_alg = Genetics()
    gene = gen_alg.read_genes(gene_score)
    game = gen_alg.run_game(gene, is_displaying=True)
    print(f'FINAL SCORE: {game.player.score}')
    print(f'FINAL TIME: {game.ticks["game"]}')

    print(f'FITNESS: {gen_alg.fitness(game)}')

#test the speed of running a generation without mutating
def test_6():
    gen_alg = Genetics()
    gene = gen_alg.read_genes(770)
    for _ in range(200):
        game = gen_alg.run_game(gene, is_displaying=False)

def test_7():
    gen_alg = Genetics()
    gen_alg.run_many_games(gen_alg.test_gene, 200, is_displaying=False)

def test_8():
    gen_alg = Genetics()
    gene = gen_alg.read_genes(770)

    gen_alg.speed_test(gene)


#PROBLEMS WITH COLLISIONS NEED TO BE FIXED LATER RUN THIS AGAIN TO SEE WHAT I MEAN

def main():
    start_time = time.time()
    #test_1()
    #test_2()
    #test_3()
    #training
    #test_4()
    #display result
    test_5(2000)
    #test_6()
    #test_7()
    #test_8()
    
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")

if __name__ == '__main__':
    main()

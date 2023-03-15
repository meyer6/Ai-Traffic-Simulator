import os
import neat
import Traffic2 
import pickle
import pyglet
import multiprocessing

def main(genome, config):
    global window
    # Loads the current ai
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    if window == 0:
        window = Traffic2.Window(net)
    else:
        window.simulation = Traffic2.Simulation(net, window.trafficLights)

    # Runs the simulation
    pyglet.app.run()

    # Returns the fitness score (reciprocal of average waiting time)
    print(window.simulation.waitingTime[1] / window.simulation.waitingTime[0] * 10000)
    return window.simulation.waitingTime[1] / window.simulation.waitingTime[0] * 10000

def run(config_file):
    # Loads configuration options
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Creates population
    p = neat.Population(config)

    # Adds statistics reporter to report data about the training
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Trains the model and produces an object which contains the best ai produced
    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), main)
    winner = p.run(pe.evaluate, 300)

    # Saves winner to file
    with open("winner.bin", "wb") as f:
        pickle.dump(winner, f)
    print('\nBest genome:\n{!s}'.format(winner))

window = 0
if __name__ == '__main__':
    # Loads config file and begins training
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
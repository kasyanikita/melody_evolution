import argparse
from generator import BaseMelodyGenerator, MelodyGenerator, SimulatedAnnealingGA
from heuristics import Heuristic
from utils import play_melody

def print_best_score(gen: BaseMelodyGenerator, play: bool = False):
    """
    Prints the best melody score and optionally plays the melody.

    :param gen: The melody generator instance.
    :param play: Whether to play the best melody.
    """
    print(f"{type(gen).__name__} score: ", gen.evaluate(gen.best_melody))
    if play:
        play_melody(gen.best_melody)

def main():
    parser = argparse.ArgumentParser(description="Melody Generator CLI")
    parser.add_argument("-m", "--melodies", type=int, default=6, help="Number of melodies to generate")
    parser.add_argument("-n", "--notes", type=int, default=8, help="Number of notes per melody")
    parser.add_argument("-g", "--generations", type=int, default=1000, help="Number of generations to evolve")
    parser.add_argument("-s", "--save", type=str, default="melodies.json", help="Path to save generated melodies")
    parser.add_argument("-p", "--play", action="store_true", help="Play the best melody")
    parser.add_argument("-a", "--algorithm", choices=["melody", "annealing"], default="melody", help="Select the algorithm: melody (default) or simulated annealing")
    parser.add_argument("-hc", "--heuristic-config", type=str, default='configs/patterns/monotonic.json', help="Path to heuristic configuration file")
    
    args = parser.parse_args()
    
    heuristic = Heuristic(args.heuristic_config)
    
    if args.algorithm == "melody":
        generator = MelodyGenerator(args.melodies, args.notes, heuristic)
    else:
        generator = SimulatedAnnealingGA(args.melodies, args.notes, heuristic)
    
    generator.run(generations=args.generations).save_melodies(args.save)
    print_best_score(generator, play=args.play)

if __name__ == "__main__":
    main()

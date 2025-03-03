import time
import random
import json

import pygame
import numpy as np
from mido import MidiFile, MidiTrack, Message

from heuristics import Heuristic

USE_HEURISTICS = True
HEURISTIC_CONFIG_PATH = 'configs/patterns/arpeggio.json'

code2name = {
    48: "C3",
    49: "C#3",
    50: "D3",
    51: "D#3",
    52: "E3",
    53: "F3",
    54: "F#3",
    55: "G3",
    56: "G#3",
    57: "A3",
    58: "A#3",
    59: "B3",
    60: "C4",
    61: "C#4",
    62: "D4",
    63: "D#4",
    64: "E4",
    65: "F4",
    66: "F#4",
    67: "G4",
    68: "G#4",
    69: "A4",
    70: "A#4",
    71: "B4",
    72: "C5",
    73: "C#5",
    74: "D5",
    75: "D#5",
    76: "E5",
    77: "F5",
    78: "F#5",
    79: "G5",
    80: "G#5",
    81: "A5",
    82: "A#5",
    83: "B5",
}


def generate_random_melodies(n=10):
    melodies = {}
    for i in range(n):
        notes = [random.randint(48, 83) for _ in range(n_melody_notes)]
        durations = random.choices([240, 480, 960, 1920], k=n_melody_notes)

        melodies[i] = {
            'notes': notes,
            'durations': durations
        }

    return melodies


def save_melodies(melodies):
    """ Saves melodies as MIDI and JSON files. """
    for i in range(len(melodies)):
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        
        notes, durations = melodies[i]['notes'], melodies[i]['durations']
        for note, duration in zip(notes, durations):
            track.append(Message('note_on', note=note, velocity=64, time=0))
            track.append(Message('note_off', note=note, velocity=64, time=duration))
            
            mid.save(f'melody_{i}.mid')
        
    with open(f'melodies.json', 'w') as f:
        json.dump(melodies, f, indent=4)


def play_melody(index):
    """ Plays a generated melody using pygame. """
    pygame.init()

    pygame.mixer.init()
    pygame.mixer.music.load(f'melody_{index}.mid')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def random_pairs(n):
    """ Generates random pairs of melodies for tournament selection. """
    numbers = list(range(n))
    random.shuffle(numbers)

    pairs = list(zip(numbers[::2], numbers[1::2]))

    return pairs


def chance(percent):
    """ Returns True with the given probability in percent. """
    return random.random() < percent / 100


def pair_round(idx, pair):
    """ Handles human-based melody selection. """
    print(f"Pair #{idx + 1}")
    print("Choose the action: \n1.Play the first melody\n2.Play the second melody\n3.Choose the winner")
    action = -1
    while action != 3:
        action = int(input("Action: "))
        if action <= 0 or action > 3:
            print("Choose action between 1 and 3")
        elif action == 1:
            play_melody(pair[0])
        elif action == 2:
            play_melody(pair[1])
            
    winner = int(input("Choose winner(1 or 2): "))
    return pair[winner - 1]


def heuristic_selection(melodies):
    """ Uses heuristics to automatically rank melodies and select the best ones. """
    heuristic = Heuristic(HEURISTIC_CONFIG_PATH)
    sorted_melodies = sorted(melodies.keys(), key=lambda i: heuristic.evaluate(melodies[i]['notes']), reverse=True)
    print(heuristic.evaluate(melodies[0]['notes']))
    return sorted_melodies[:len(sorted_melodies) // 2]  # Select top 50%


def crossover(melodies, winners):
    """ Creates a new generation using crossover of winners. """
    new_generation = {}
    for i in range(len(melodies)):
        first_parent, second_parent = random.sample(winners, 2)
        split_index = random.randint(1, n_melody_notes - 1)

        new_generation[i] = {
            "notes": melodies[first_parent]['notes'][:split_index] + melodies[second_parent]['notes'][split_index:],
            "durations": melodies[first_parent]['durations'][:split_index] + melodies[second_parent]['durations'][split_index:]
        }
        
    return new_generation


# def mutation(melodies):
#     for i in range(len(melodies)):
#         for j in range(len(melodies[i]['notes'])):
#             if (chance(15)):
#                 melodies[i]['notes'][j] = min(melodies[i]['notes'][j] + random.randint(1, 2), 83)
#             if (chance(15)):
#                 melodies[i]['notes'][j] = max(melodies[i]['notes'][j] - random.randint(1, 2), 48)
#             if (chance(5)):
#                 melodies[i]['durations'][j] = min(melodies[i]['durations'][j]*2, 1920)
#             if (chance(5)):
#                 melodies[i]['durations'][j] = max(melodies[i]['durations'][j]//2, 240)
                
#     return melodies


def mutation(melodies):
    """ Introduces random mutations to the melodies. """
    for i in range(len(melodies)):
        for j in range(len(melodies[i]['notes'])):
            if (chance(5)):
                p_dist = [0.45, 0.2, 0.1, 0.05, 0.05, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01]
                sign = random.choice([-1, 1])
                change_note_number = np.random.choice(list(range(1, 12 + 1)), p=p_dist)
                melodies[i]['notes'][j] = int(melodies[i]['notes'][j] + sign*change_note_number)
                melodies[i]['notes'][j] = min(max(melodies[i]['notes'][j], 48), 83)
            if (chance(5)):
                scalar = random.choice([2, 0.5])
                melodies[i]['durations'][j] = int(melodies[i]['durations'][j]*scalar)
                melodies[i]['durations'][j] = min(max(melodies[i]['durations'][j], 240), 1920)
                
    return melodies


def load_melodies_data():
    """ Loads melodies from a JSON file. """
    with open("melodies.json") as f:
        melodies = json.load(f)
    
    keys = list(melodies.keys())
    for key in keys:
        melodies[int(key)] = melodies[key]
    
    for key in keys:
        del melodies[key]
        
    return melodies 


if __name__ == "__main__":
    n_melodies = 6
    n_melody_notes = 8

    melodies = generate_random_melodies(n_melodies)
    save_melodies(melodies)
    # melodies = load_melodies_data()

    for _ in range(1000):
        winners = []

        if USE_HEURISTICS:
            winners = heuristic_selection(melodies)
        else:
            pairs = random_pairs(n_melodies)
            for i, pair in enumerate(pairs):
                winners.append(pair_round(i, pair))
        
        melodies = crossover(melodies, winners)
        melodies = mutation(melodies)
        save_melodies(melodies)
    
    play_melody(0)

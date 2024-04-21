# EXCERSIZE 2c
# Estimate the mean and median number of plays you can expect to make until
# you go broke, if you start with 10 coins. Run a simulation in Python to
# estimate this. Add your results to your PDF report.

import statistics
import random


SIMULATION_NUMBER = 10000
MACHINE = ['Bar', "Bell", "Lemon", 'Cherry']
WINNERS = [['Bar', "Bar", "Bar"], ['Bell', "Bell", "Bell"],
           ['Lemon', "Lemon", "Lemon"], ['Cherry', "Cherry", 'Cherry']]
WINNERS_PAYBACKS = [20, 15, 5, 3, 2, 1]


def mean_median_of_plays():
    plays = []

    for number in range(SIMULATION_NUMBER):
        plays_number = 0
        coins = 10
        while coins > 0:
            coins -= 1
            elements = random.choices(MACHINE,  k=3)

            if elements in WINNERS:
                index = next((index for index, sublist in enumerate(WINNERS) if sublist == elements), None)
                coins += WINNERS_PAYBACKS[index]
            elif elements[:2] == WINNERS[3][:2]:
                coins += WINNERS_PAYBACKS[4]
            elif elements[0] == WINNERS[3][0]:
                coins += WINNERS_PAYBACKS[5]

            plays_number += 1

        plays.append(plays_number)

    mean = statistics.mean(plays)
    median = statistics.median(plays)

    print(f'The mean of plays made before going broke: {mean}, the median {median}, by {SIMULATION_NUMBER} simulations run')


def main():
    mean_median_of_plays()


if __name__ == '__main__':
    main()

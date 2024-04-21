import statistics
import random
import math


# Exercise 2c


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
    print("Exercise 2: \n")
    mean_median_of_plays()
    print("\n")


if __name__ == '__main__':
    main()


# Exercise 3 Part One


def prob_of_same_birth_day(N):
    return 1 - (math.factorial(365)/(pow(365, N) * math.factorial(365 - N)))


def main():
    print("Exercise 3 Part One: \n")
    more_than_50 = []
    for N in range(10, 51):
        same_birth_date = prob_of_same_birth_day(N)
        if same_birth_date >= 0.5:
            more_than_50.append(same_birth_date)
        print(f'The probabilty that at least 2 people out of {N} have the same birth date is: {same_birth_date}')

    print(f'The proportion of N where the event happens with at least 50% chance {len(more_than_50)/41}')
    print("\n")


if __name__ == '__main__':
    main()


# Exercise 3 Part Two


SIMULATIONS_NUMBER = 100


def number_of_people():
    dates = {i: 0 for i in range(1, 366)}
    while 0 in dates.values():
        dates[random.randint(1, 365)] += 1
    return sum(dates.values())


def main():
    print("Exercise 3 Part TWo: \n")
    people_number = []
    for number in range(SIMULATIONS_NUMBER):
        people_number.append(number_of_people())

    print(f'For simulations number {SIMULATIONS_NUMBER} Peter is expected to form a group of {statistics.mean(people_number)} people')
    print("\n")


if __name__ == '__main__':
    main()

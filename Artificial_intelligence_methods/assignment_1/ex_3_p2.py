import statistics
import random
SIMULATIONS_NUMBER = 100


def number_of_people():
    dates = {i: 0 for i in range(1, 366)}
    while 0 in dates.values():
        dates[random.randint(1, 365)] += 1
    return sum(dates.values())


def main():
    people_number = []
    for number in range(SIMULATIONS_NUMBER):
        people_number.append(number_of_people())

    print(f'For simulations number {SIMULATIONS_NUMBER} Peter is expected to form a group of {statistics.mean(people_number)} people')


if __name__ == '__main__':
    main()

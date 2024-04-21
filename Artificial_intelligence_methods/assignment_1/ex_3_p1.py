import math


def prob_of_same_birth_day(N):
    """Calcualtes the probabilty that at least 2 out of N given people have the same birth date"""
    return 1 - (math.factorial(365)/(pow(365, N) * math.factorial(365 - N)))


def main():
    more_than_50 = []
    for N in range(10, 51):
        same_birth_date = prob_of_same_birth_day(N)
        if same_birth_date >= 0.5:
            more_than_50.append(same_birth_date)
        print(f'The probabilty that at least 2 people out of {N} have the same birth date is: {same_birth_date}')

    print(f'The proportion of N where the event appens with the least 50% chance {len(more_than_50)/41}')


if __name__ == '__main__':
    main()

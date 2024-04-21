import numpy as np


weather_probabilities = np.array([[0.7, 0.3],
                                  [0.3, 0.7]])

umbrella_probabilities = np.array([[0.9, 0],
                                   [0, 0.2]])

no_umbrella_probabilities = np.array([[0.1, 0],
                                      [0, 0.8]])


def forward(observations):
    # Setting initial probabilties - 0.5 for rain and 0.5 for sunshine
    init_prob_rain_sun = np.array([0.5, 0.5])
    forward_list = [init_prob_rain_sun]
    yesterday = init_prob_rain_sun

    # Looping through days
    day = 1
    for observation in observations:

        # Dootiing - element-wise multiplication and sum of the results
        weather_today = np.dot(weather_probabilities, yesterday)

        # If umbrella is observed
        if observation:
            today = np.dot(umbrella_probabilities, weather_today)
        # If umbrella is not observed
        else:
            today = np.dot(no_umbrella_probabilities, weather_today)

        # Normalizing result
        today = today / today.sum()

        # Display todays weather probabilities
        print(f'P(X{day}|e1:{day}) = rain: {today[0]}, sun: {today[1]}')

        forward_list.append(today)
        # Today becomes yester before the beginning of the next day
        yesterday = today

        # Incrementation of the day number
        day += 1

    return forward_list


if __name__ == '__main__':
    observations_1 = [True, True]
    print("Exercise 2.1:\n")
    forward_1 = forward(observations_1)

    observations_2 = [True, True, False, True, True]
    print("\nExercise 2.2:\n")
    forward_2 = forward(observations_2)

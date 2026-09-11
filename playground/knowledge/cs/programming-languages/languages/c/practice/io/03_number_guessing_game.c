#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    int secretNumber, guess, guessCount = 0;
    int maxGuesses = 5;

    srand(time(NULL));
    secretNumber = rand() % 100 + 1;
    printf("I have chosen a number between 1 and 100. You have %d attempts to guess it.\n", maxGuesses);

    while (guess != secretNumber && guessCount <= maxGuesses)
    {
        if (guessCount > 0)
        {
            printf("Wrong! Guess again:");
        }
        else
        {
            printf("Enter your guess:");
        }

        char userInput[256];
        fgets(userInput, sizeof(userInput), stdin);
        guess = atoi(userInput);

        guessCount++;
    }

    if (guessCount <= maxGuesses && guess == secretNumber)
    {

        printf("Conguratulations! You have guessed correct. The secret number is %d", secretNumber);
    }
    else
    {
        printf("Guess limit is reached. Unfortunately you are out of luck this time :/");
    }

    return 0;
}
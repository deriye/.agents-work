#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include <stdbool.h>

#define ATTEMPTS 10

struct GAME_STATE
{
    bool won;
    int attemptNumber;
};

char *words[] = {
    "apple",
    "banana",
    "computer",
    "dinosaur",
    "elephant",
    "football",
    "guitar",
    "hangman",
    "internet",
    "jazz",
    "kangaroo",
    "lemon",
    "mountain",
    "notebook",
    "octopus",
    "penguin",
    "quasar",
    "rainbow",
    "software",
    "trumpet"
};

int getRandomIndex()
{
    srand(time(NULL));
    int max = sizeof(words) / sizeof(words[0]);
    return rand() % (max);
}

char *previewWord(char *word, char *usedChars)
{
    char *wordToPreview = malloc(strlen(word) * word[0]);

    for (int i = 0; i < strlen(word); i++)
    {
        char wordChar = word[i];
        wordToPreview[i] = strchr(usedChars, wordChar) != NULL ? wordChar : 95;
        // printf("%c", 95);
    }

    return wordToPreview;
}

int main()
{
    struct GAME_STATE state = {false, 0};
    int randomIndex = getRandomIndex();
    char *chosenWord = words[randomIndex];
    char usedChars[10] = {' '};

    while (state.attemptNumber < ATTEMPTS)
    {
        char *wordToPreview = previewWord(chosenWord, usedChars);
        printf("\n%s\n", wordToPreview);
        printf("Used: %s\n\n", usedChars);

        char tempUsedChars[10];
        strcpy(tempUsedChars, usedChars);

        char c;
        while ((c = getchar()) == '\n' || c == ' ')
            ;

        tempUsedChars[state.attemptNumber] = c;
        wordToPreview = previewWord(chosenWord, tempUsedChars);

        if (strcmp(chosenWord, wordToPreview) == 0)
        {
            state.won = 1;
            usedChars[state.attemptNumber] = c;
            break;
        }

        if (strchr(usedChars, c) != NULL)
        {
            printf("Letter already used, try another one!\n");
            continue;
        }

        printf("Try again!\n");

        usedChars[state.attemptNumber] = c;
        state.attemptNumber++;
    }

    if (state.won)
    {
        printf("\nCongratulations! You guessed \"%s\" right.\n", chosenWord);
        printf("Used chars: %s", usedChars);
    }
    else
    {
        printf("\nBetter luck next time");
    }

    // char input[100];

    // if (strchr(chosenWord, 'l')) {
    //     printf("Correct!");
    //     scanf("%s", input);
    // printf("%c", chosenWord[0]);
    // printf("%s", input);
    // }

    return 0;
}
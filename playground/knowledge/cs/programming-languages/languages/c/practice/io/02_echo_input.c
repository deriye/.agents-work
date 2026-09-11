#include <stdio.h>

int main()
{
    char userInput[256];

    printf("Please enter something: ");

    fgets(userInput, sizeof(userInput), stdin);

    printf("You entered: %s", userInput);

    return 0;
}
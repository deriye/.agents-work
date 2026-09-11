#include <stdio.h>
#include <stdbool.h>
#include <string.h>

enum States
{
    MAIN
};

struct State
{
    enum States state;
    bool active;
};

int handleMain(char *input, int size, bool *active)
{
    if (strcmp(input, "hej") == 0) {
        printf("hallo!");
    }

    *active = 0;
}

int main()
{
    struct State s = {MAIN, true};
    char input[256];

    while (s.active)
    {
        scanf("%s", input);

        if (s.state == MAIN)
        {
            handleMain(input, sizeof(input), &s.active);
        }
    }

    return 0;
}
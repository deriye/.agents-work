#include <stdlib.h>
#include <stdio.h>

struct Tuple
{
    int *lhs;
    int *rhs;
} typedef tuple;

int *divide(int *arr, int size)
{
    int *lhs = malloc(size / 2 * sizeof(int));
    int *rhs = malloc(size / 2 * sizeof(int));
    int *result = malloc(sizeof(char));

    for (int i = 0; i < 5; i++)
    {
        result[i] = i + 1;
    }

    return result;
}

int main()
{
    int numbers[] = {4, 3, 2, 1};
    int *result = divide(numbers, sizeof(numbers) / sizeof(numbers[0]));

    for (int i = 0; i < 10; i++)
    {
        printf("r: %d\n", result[i]);
    }

    free(result);

    return 0;
}
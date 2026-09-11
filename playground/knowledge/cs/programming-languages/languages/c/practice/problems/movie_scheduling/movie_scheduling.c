#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h> // For boolean data type (bool, true, false)

// how to represent an interval, start and end time?
typedef struct Interval
{
    int start;
    int end;
} interval;

typedef struct Tuple
{
    interval *lhs;
    interval *rhs;
} tuple;

bool moviesCollide(interval i1, interval i2)
{
    if (i1.start < i2.start)
    {
        return i1.end > i2.start;
    }

    return i1.start < i2.end;
}

// find earliest ending movie that is still considered (trivial if movies are sorted by first ending)
int findEarliestEnding(bool notConsidered[], int size)
{
    for (int i = 0; i < size; i++)
    {
        if (notConsidered[i] == true)
        {
            continue;
        }
    }

    return -1;
}

// divide to left and right until there is 1 element

/*
                                [10,9,8,7,6,5,4,3,2,1]
                                [10,9,8,7,6]  [5,4,3,2,1]
                                [10,9,8] [7,6] [5,4,3] [2,1]
                                [10,9] [8] [7] [6] [5,4] [3] [2] [1]
                                [10] [9] [8] [7] [6] [5] [4] [3] [2] [1]
                                [9,10] [8] [7,6] [4,5] [3] [1, 2]
                                [8,9,10] [7,6] [4, 5] [3] [1, 2]
                                [7,8,9,10] [3,4,5,6] [1,2]
*/

tuple divide(interval movies[], int size)
{
    interval *lhs = malloc(size / 2);
    interval *rhs = malloc(size / 2);

    tuple result = {lhs, rhs};

    return result;
}

int mergeSortByEarliestEnding(interval movies[], int size)
{
    // divide, divide until list is 1 item, then merge but how
    if (size == 1)
    {
    }

    tuple result = divide(movies);

    interval *lhs = result.lhs;
    interval *rhs = result.rhs;

    
}

interval *findOptimalMovies(interval movies[], int size)
{
    bool *notConsidered = malloc(size);
    interval *selected = malloc(size);

    for (int i = 0; i < size; i++)
    {
        for (int j = i + 1; j < size; j++)
        {
            bool collide = moviesCollide(movies[i], movies[j]);
        }
    }
}

int main()
{
    interval movies[4] = {{1, 6}, {3, 7}, {6, 9}, {0, 10}};
    interval *optimalMovies = findOptimalMovies(movies, sizeof(movies) / sizeof(interval));

    return 0;
}
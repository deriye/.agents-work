/*
Write a function that takes an array of integers and returns the sum of all the even numbers in the array. Test it with a few different arrays (one with all even numbers, one with all odd numbers, and one with mixed numbers).
*/

#include <stdio.h>

int sumOfEvens(int integers[], int length) {
    int sum = 0;

    for (int i = 0; i < length; ++i) {
        int current = integers[i];

        if (current % 2 == 0) {
            sum += current;
        }
    }

    return sum;
}

int main() {
    int numbers[] = {1,2,3,4,5,6,7,8,9,10};
    int numbersP[] = {1,2,3,4,5,6,7,8,9,10};

    int sum = sumOfEvens(numbers, sizeof(numbers) / sizeof(numbers[0]));
    printf("Sum of all the even numbers: %d\n", sum);
    
    return 0;
}
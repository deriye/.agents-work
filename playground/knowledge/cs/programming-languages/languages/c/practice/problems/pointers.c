#include <stdio.h>
#include <stdlib.h>

int main() {
    int numbers[] = {1,2,3,4};
    int* numbersP = numbers;

    int num = 5;
    int* numP = &num;
    *numP = 6;

    char letter = 'a';
    printf("Letter: %d", letter);
    
    return 0;
}
//    n = 0 | 1 | 2 | 3 | 4 | 5 |  6
// f(n) = 0 | 1 | 2 | 3 | 5 | 8 | 13

#include <stdio.h>

long fib(long n) {
    if (n == 0) return 0;
    if (n == 1) return 1;
    
    return fib(n-1) + fib(n-2);
}

int main() {
    int n = 46;
    long result = fib(n);
    printf("fib(%d): %d", n, result);

    return 0;
}
#include <stdio.h>

long arr[100] = {0};

long fib(long n) {
    if (n <= 1) {
        return n;
    }

    long f_n_1 = arr[n-1];
    long f_n_2 = arr[n-2];

    if (!f_n_1) {
        f_n_1 = fib(n-1);
        arr[n-1] = f_n_1;
    }

    if (!f_n_2) {
        f_n_2 = fib(n-2);
        arr[n-2] = f_n_2;
    }

    return f_n_1 + f_n_2;
}

int main() {
    int n = 46;
    long result = fib(n);
    printf("fib(%d): %d", n, result);

    return 0;
}
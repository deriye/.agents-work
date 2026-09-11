#include <iostream>
#include <cstdlib> // for rand() and srand()
#include <ctime>   // for time()

int main()
{
    srand(time(0));
    // Generate random number between 0 and 100
    int randomNumber = rand() % 101;
    int attemptsLeft = 6;

    std::cout << "Guess the number between 0 and 100\n";

    while (attemptsLeft > 0) {
        int guess;
        std::cin >> guess;

        if (guess == randomNumber) {
            std::cout << "Congratulations, you guess correctly!";
            break;
        }

        if (guess < randomNumber) {
            std::cout << "Too low...\n";
        } else {
            std::cout << "Too high...\n";
        }

        attemptsLeft--;
    } 

    return 0;
}
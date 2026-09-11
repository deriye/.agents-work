/*
Leetcode
2. Add Two Numbers

You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.


Example 1:
Input: l1 = [2,4,3], l2 = [5,6,4]
Output: [7,0,8]
Explanation: 342 + 465 = 807.

342 = 300 + 40 + 2
455 = 400 + 50 + 5
---> 807 = [8, 0, 7]

Example 2:
Input: l1 = [0], l2 = [0]
Output: [0]

Example 3:
Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
Output: [8,9,9,9,0,0,0,1]
 
9999999 = 9000000 + 900000 + 90000 + 9000 + 900 + 90 + 9
   9999 =                            9000 + 900 + 90 + 9
---> 

Constraints:
The number of nodes in each linked list is in the range [1, 100].
0 <= Node.val <= 9
It is guaranteed that the list represents a number that does not have leading zeros.

*/

// int myAge = 43;     // Variable declaration
// int* ptr = &myAge;  // Pointer declaration

// Reference: Output the memory address of myAge with the pointer (0x7ffe5367e044)
// printf("%p\n", ptr);

// Dereference: Output the value of myAge with the pointer (43)
// printf("%d\n", *ptr);

#include <stdio.h>
#include <stdlib.h>

// Definition for singly-linked list.
struct ListNode {
    int val;
    struct ListNode *next;
};

// 1. Calculate number of l1
// 2. Calulcate number of l2
// 3. Calculate sum of the two numbers
// 4. Parse number as linked list in a reverse order


long long calculateNumber(struct ListNode *l1) {
    struct ListNode* nextNode = l1;
    long long decimalPosition = 1;
    long long number = 0;

    while (nextNode != NULL) {
        // printf("%d + %d * %d = ", number, decimalPosition, nextNode->val);
        number = number + decimalPosition * nextNode->val;
        // printf("%d\n", number);
        decimalPosition *= 10;
        nextNode = nextNode->next;
    }

    return number;
}

// Ex.
// 9999
// (integer div) 9999 / 10  => 9990
// (modulos) 9999 % 10      => 9
struct ListNode* numberToListNode(long long number) {
    struct ListNode* firstNode = NULL;
    struct ListNode* previousNode = NULL;
    long long numberLeft = number;

    int counter = 0;
    while (numberLeft > 0) {
        struct ListNode *node = malloc(sizeof(struct ListNode));

        if (previousNode == NULL) {
            firstNode = node;
        } else {
            previousNode->next = node;
        }

        node->val = numberLeft % 10;
        node->next = NULL;
        
        // prepare for next round
        numberLeft = numberLeft / 10;
        previousNode = node;
    }
    
    if (number == 0) {
        firstNode = malloc(sizeof(struct ListNode));
        firstNode->val = 0;
        firstNode->next = NULL;
    }

    return firstNode;
}

struct ListNode* addTwoNumbers(struct ListNode* l1, struct ListNode* l2) {
    long long number1 = calculateNumber(l1);
    long long number2 = calculateNumber(l2);
    long long sum = number1 + number2;

    struct ListNode *list = numberToListNode(sum);

    return list;
}

int main() {
    struct ListNode* l1 = numberToListNode(9999999991);
    struct ListNode* l2 = numberToListNode(9);
    struct ListNode* sum = addTwoNumbers(l1, l2);

    // printf("-------------------------\n");

    struct ListNode* nextNode = sum;
    while(nextNode != NULL) {
        printf("val: %d\n", nextNode->val);

        // pre next round
        nextNode = nextNode->next;
    }

    return 0;
}


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
    struct ListNode dummy;
    struct ListNode* tail = &dummy;
    int carry = 0;
    
    while (l1 != NULL || l2 != NULL || carry != 0) {
        int val1 = (l1 != NULL) ? l1->val : 0;
        int val2 = (l2 != NULL) ? l2->val : 0;
        
        int sum = val1 + val2 + carry;
        carry = sum / 10;
        
        struct ListNode* newNode = malloc(sizeof(struct ListNode));
        newNode->val = sum % 10;
        newNode->next = NULL;
        
        tail->next = newNode;
        tail = newNode;
        
        if (l1 != NULL) l1 = l1->next;
        if (l2 != NULL) l2 = l2->next;
    }
    
    return dummy.next;
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


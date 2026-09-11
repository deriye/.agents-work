#include <stdio.h>
#include <stdlib.h>

struct ListNode
{
    int val;
    struct ListNode *previous;
    struct ListNode *next;
};

int main()
{
    int numbers[] = {1,2,3,4,5,6};
    int length = sizeof(numbers) / sizeof(numbers[0]);

    struct ListNode *firstNode = NULL;
    struct ListNode *previousNode = NULL;

    for (int i = 0; i < length; i++) {
        struct ListNode *node = malloc(sizeof(struct ListNode));

        if (node == NULL) {
            printf("Memory allocation failed\n");
            return 1;
        }

        node->val = numbers[i];
        node->previous = previousNode;
        node->next = NULL;
        
        if (previousNode != NULL) {
            previousNode->next = node;
        } else {
            firstNode = node;
        }

        previousNode = node;
    }
    
    struct ListNode *nextNode = firstNode;
    int counter = 0;

    while (nextNode != NULL) {
        counter++;
        nextNode = nextNode->next;
    }
    
    printf("Length of nodes is: %d\n", counter);

    // Free allocated memory
    nextNode = firstNode;
    while (nextNode != NULL) {
        struct ListNode *temp = nextNode;
        nextNode = nextNode->next;
        free(temp);
    }

    return 0;
}
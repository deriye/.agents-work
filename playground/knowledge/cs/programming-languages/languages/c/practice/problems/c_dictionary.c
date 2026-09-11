#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Size of the hash table
#define TABLE_SIZE 100

// Node structure to store key-value pairs
typedef struct Node {
    char* key;
    char* value;
    struct Node* next;
} Node;

// Dictionary structure (hash table)
typedef struct {
    Node* table[TABLE_SIZE];
} Dictionary;

// Hash function
unsigned int hash(const char* key) {
    unsigned int hash_value = 0;
    for (int i = 0; key[i] != '\0'; i++) {
        hash_value = hash_value * 31 + key[i];
    }
    return hash_value % TABLE_SIZE;
}

// Create a new dictionary
Dictionary* dict_create() {
    Dictionary* dict = malloc(sizeof(Dictionary));
    if (dict == NULL) {
        return NULL;
    }
    
    // Initialize all buckets to NULL
    for (int i = 0; i < TABLE_SIZE; i++) {
        dict->table[i] = NULL;
    }
    
    return dict;
}

// Insert or update a key-value pair
void dict_set(Dictionary* dict, const char* key, const char* value) {
    unsigned int index = hash(key);
    
    // Check if key already exists
    Node* current = dict->table[index];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            // Key exists, update value
            free(current->value);
            current->value = strdup(value);
            return;
        }
        current = current->next;
    }
    
    // Key doesn't exist, create new node
    Node* new_node = malloc(sizeof(Node));
    if (new_node == NULL) {
        return;
    }
    
    new_node->key = strdup(key);
    new_node->value = strdup(value);
    new_node->next = dict->table[index];
    dict->table[index] = new_node;
}

// Get a value by key
char* dict_get(Dictionary* dict, const char* key) {
    unsigned int index = hash(key);
    
    Node* current = dict->table[index];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    
    return NULL; // Key not found
}

// Remove a key-value pair
int dict_remove(Dictionary* dict, const char* key) {
    unsigned int index = hash(key);
    
    Node* current = dict->table[index];
    Node* prev = NULL;
    
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            // Found the key
            if (prev == NULL) {
                // First node in the bucket
                dict->table[index] = current->next;
            } else {
                // Not the first node
                prev->next = current->next;
            }
            
            free(current->key);
            free(current->value);
            free(current);
            return 1;
        }
        
        prev = current;
        current = current->next;
    }
    
    return 0; // Key not found
}

// Free all memory used by the dictionary
void dict_free(Dictionary* dict) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        Node* current = dict->table[i];
        while (current != NULL) {
            Node* temp = current;
            current = current->next;
            
            free(temp->key);
            free(temp->value);
            free(temp);
        }
    }
    
    free(dict);
}

// Example usage
int main() {
    Dictionary* dict = dict_create();
    
    dict_set(dict, "name", "John");
    dict_set(dict, "age", "30");
    dict_set(dict, "city", "New York");
    
    printf("Name: %s\n", dict_get(dict, "name"));
    printf("Age: %s\n", dict_get(dict, "age"));
    printf("City: %s\n", dict_get(dict, "city"));
    
    // Update a value
    dict_set(dict, "age", "31");
    printf("Updated age: %s\n", dict_get(dict, "age"));
    
    // Remove a key
    dict_remove(dict, "city");
    printf("City after removal: %s\n", dict_get(dict, "city") ? dict_get(dict, "city") : "Not found");
    
    dict_free(dict);
    return 0;
}

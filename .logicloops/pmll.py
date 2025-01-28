#!/bin/bash
#
# pmll.sh
#
# Shell script wrapper for pmll.py to manage persistent key-value memory.

# Path to pmll.py
PMLL_PY="pmll.py"

# Function to display usage
usage() {
    echo "Usage:"
    echo "  $0 add <key> <value>       # Add or update a key-value pair"
    echo "  $0 get <key>               # Retrieve a value by key"
    echo "  $0 remove <key>            # Remove a key-value pair"
    echo "  $0 list                    # List all keys"
    echo "  $0 clear                   # Clear all memory"
    echo "  $0 display                 # Display all memory (debugging)"
    exit 1
}

# Check if pmll.py exists
if [ ! -f "$PMLL_PY" ]; then
    echo "[pmll.sh] Error: '$PMLL_PY' not found in the current directory."
    exit 1
fi

# Check for at least one argument
if [ $# -lt 1 ]; then
    echo "[pmll.sh] Error: No command provided."
    usage
fi

# Parse command
COMMAND="$1"
shift

case "$COMMAND" in
    add)
        if [ $# -ne 2 ]; then
            echo "[pmll.sh] Error: 'add' requires <key> and <value>."
            usage
        fi
        KEY="$1"
        VALUE="$2"
        python3 "$PMLL_PY" add "$KEY" "$VALUE"
        ;;
    get)
        if [ $# -ne 1 ]; then
            echo "[pmll.sh] Error: 'get' requires <key>."
            usage
        fi
        KEY="$1"
        python3 "$PMLL_PY" get "$KEY"
        ;;
    remove)
        if [ $# -ne 1 ]; then
            echo "[pmll.sh] Error: 'remove' requires <key>."
            usage
        fi
        KEY="$1"
        python3 "$PMLL_PY" remove "$KEY"
        ;;
    list)
        if [ $# -ne 0 ]; then
            echo "[pmll.sh] Error: 'list' does not take any arguments."
            usage
        fi
        python3 "$PMLL_PY" list
        ;;
    clear)
        if [ $# -ne 0 ]; then
            echo "[pmll.sh] Error: 'clear' does not take any arguments."
            usage
        fi
        python3 "$PMLL_PY" clear
        ;;
    display)
        if [ $# -ne 0 ]; then
            echo "[pmll.sh] Error: 'display' does not take any arguments."
            usage
        fi
        python3 "$PMLL_PY" display
        ;;
    *)
        echo "[pmll.sh] Error: Unknown command '$COMMAND'."
        usage
        ;;
esac

// PMLL.h
#ifndef PMLL_H
#define PMLL_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initializes the persistent memory system.
 * @param file_name The file to store persistent memory.
 * @return 0 on success, non-zero on failure.
 */
int pmll_init(const char* file_name);

/**
 * Adds or updates a key-value pair.
 * @param key The key string.
 * @param value The value string.
 * @return 0 on success, non-zero on failure.
 */
int pmll_add(const char* key, const char* value);

/**
 * Retrieves the value associated with a key.
 * @param key The key string.
 * @param value_buffer Buffer to store the retrieved value.
 * @param buffer_size Size of the value_buffer.
 * @return 0 on success, non-zero on failure or key not found.
 */
int pmll_get(const char* key, char* value_buffer, int buffer_size);

/**
 * Removes a key-value pair.
 * @param key The key string.
 * @return 0 on success, non-zero on failure or key not found.
 */
int pmll_remove(const char* key);

/**
 * Lists all keys in the memory.
 * @param keys_buffer Buffer to store the list of keys.
 * @param buffer_size Size of the keys_buffer.
 * @return 0 on success, non-zero on failure.
 */
int pmll_list(char* keys_buffer, int buffer_size);

/**
 * Clears all memory.
 * @return 0 on success, non-zero on failure.
 */
int pmll_clear();

/**
 * Displays all key-value pairs (for debugging).
 * @return 0 on success, non-zero on failure.
 */
int pmll_display();

#ifdef __cplusplus
}
#endif

#endif // PMLL_H // PMLL.c
#include "PMLL.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#define MAX_LINE_LENGTH 1024
#define MAX_KEY_LENGTH 256
#define MAX_VALUE_LENGTH 768
#define MAX_KEYS 1000

typedef struct {
    char key[MAX_KEY_LENGTH];
    char value[MAX_VALUE_LENGTH];
} KeyValuePair;

typedef struct {
    KeyValuePair pairs[MAX_KEYS];
    int count;
    char memory_file[256];
    pthread_mutex_t lock;
} PMLL;

static PMLL pmll;

// Helper function to trim newline and carriage return characters
void trim_newline(char* str) {
    size_t len = strlen(str);
    while(len > 0 && (str[len-1] == '\n' || str[len-1] == '\r')) {
        str[len-1] = '\0';
        len--;
    }
}

// Initializes the PMLL system
int pmll_init(const char* file_name) {
    if (file_name == NULL) {
        fprintf(stderr, "[PMLL] Error: Memory file name is NULL.\n");
        return -1;
    }

    strncpy(pmll.memory_file, file_name, sizeof(pmll.memory_file)-1);
    pmll.memory_file[sizeof(pmll.memory_file)-1] = '\0';
    pmll.count = 0;

    if (pthread_mutex_init(&pmll.lock, NULL) != 0) {
        fprintf(stderr, "[PMLL] Error: Mutex initialization failed.\n");
        return -1;
    }

    // Load existing memory from file
    FILE* file = fopen(pmll.memory_file, "r");
    if (file == NULL) {
        // If file doesn't exist, it's not an error; start fresh
        printf("[PMLL] Info: Memory file '%s' not found. Starting fresh.\n", pmll.memory_file);
        return 0;
    }

    char line[MAX_LINE_LENGTH];
    while (fgets(line, sizeof(line), file)) {
        trim_newline(line);
        char* delimiter = strchr(line, ':');
        if (delimiter == NULL) {
            continue; // Invalid line format
        }
        *delimiter = '\0';
        char* key = line;
        char* value = delimiter + 1;

        if (pmll.count < MAX_KEYS) {
            strncpy(pmll.pairs[pmll.count].key, key, MAX_KEY_LENGTH-1);
            pmll.pairs[pmll.count].key[MAX_KEY_LENGTH-1] = '\0';
            strncpy(pmll.pairs[pmll.count].value, value, MAX_VALUE_LENGTH-1);
            pmll.pairs[pmll.count].value[MAX_VALUE_LENGTH-1] = '\0';
            pmll.count++;
        } else {
            fprintf(stderr, "[PMLL] Warning: Maximum key-value pairs reached. Some entries may be skipped.\n");
            break;
        }
    }

    fclose(file);
    printf("[PMLL] Info: Loaded %d key-value pairs from '%s'.\n", pmll.count, pmll.memory_file);
    return 0;
}

// Adds or updates a key-value pair
int pmll_add(const char* key, const char* value) {
    if (key == NULL || value == NULL) {
        fprintf(stderr, "[PMLL] Error: Key or value is NULL.\n");
        return -1;
    }

    pthread_mutex_lock(&pmll.lock);

    // Check if key exists; if so, update
    for(int i = 0; i < pmll.count; i++) {
        if(strcmp(pmll.pairs[i].key, key) == 0) {
            strncpy(pmll.pairs[i].value, value, MAX_VALUE_LENGTH-1);
            pmll.pairs[i].value[MAX_VALUE_LENGTH-1] = '\0';
            pthread_mutex_unlock(&pmll.lock);
            printf("[PMLL] Added/Updated memory: '%s' -> '%s'\n", key, value);
            return 0;
        }
    }

    // If key doesn't exist, add new pair
    if(pmll.count < MAX_KEYS) {
        strncpy(pmll.pairs[pmll.count].key, key, MAX_KEY_LENGTH-1);
        pmll.pairs[pmll.count].key[MAX_KEY_LENGTH-1] = '\0';
        strncpy(pmll.pairs[pmll.count].value, value, MAX_VALUE_LENGTH-1);
        pmll.pairs[pmll.count].value[MAX_VALUE_LENGTH-1] = '\0';
        pmll.count++;
        pthread_mutex_unlock(&pmll.lock);
        printf("[PMLL] Added/Updated memory: '%s' -> '%s'\n", key, value);
        return 0;
    } else {
        pthread_mutex_unlock(&pmll.lock);
        fprintf(stderr, "[PMLL] Error: Maximum key-value pairs reached. Cannot add '%s'.\n", key);
        return -1;
    }
}

// Retrieves the value associated with a key
int pmll_get(const char* key, char* value_buffer, int buffer_size) {
    if (key == NULL || value_buffer == NULL) {
        fprintf(stderr, "[PMLL] Error: Key or value_buffer is NULL.\n");
        return -1;
    }

    pthread_mutex_lock(&pmll.lock);

    for(int i = 0; i < pmll.count; i++) {
        if(strcmp(pmll.pairs[i].key, key) == 0) {
            strncpy(value_buffer, pmll.pairs[i].value, buffer_size-1);
            value_buffer[buffer_size-1] = '\0';
            pthread_mutex_unlock(&pmll.lock);
            printf("[PMLL] Retrieved: '%s' -> '%s'\n", key, value_buffer);
            return 0;
        }
    }

    pthread_mutex_unlock(&pmll.lock);
    printf("[PMLL] No memory found for key: '%s'\n", key);
    return -1;
}

// Removes a key-value pair
int pmll_remove(const char* key) {
    if (key == NULL) {
        fprintf(stderr, "[PMLL] Error: Key is NULL.\n");
        return -1;
    }

    pthread_mutex_lock(&pmll.lock);

    for(int i = 0; i < pmll.count; i++) {
        if(strcmp(pmll.pairs[i].key, key) == 0) {
            // Shift remaining pairs
            for(int j = i; j < pmll.count -1; j++) {
                pmll.pairs[j] = pmll.pairs[j+1];
            }
            pmll.count--;
            pthread_mutex_unlock(&pmll.lock);
            printf("[PMLL] Removed memory for key: '%s'\n", key);
            return 0;
        }
    }

    pthread_mutex_unlock(&pmll.lock);
    printf("[PMLL] No memory found for key: '%s'\n", key);
    return -1;
}

// Lists all keys
int pmll_list(char* keys_buffer, int buffer_size) {
    if (keys_buffer == NULL) {
        fprintf(stderr, "[PMLL] Error: keys_buffer is NULL.\n");
        return -1;
    }

    pthread_mutex_lock(&pmll.lock);

    if(pmll.count == 0) {
        strncpy(keys_buffer, "No keys found.", buffer_size-1);
        keys_buffer[buffer_size-1] = '\0';
        pthread_mutex_unlock(&pmll.lock);
        printf("[PMLL] No keys found in memory.\n");
        return 0;
    }

    keys_buffer[0] = '\0';
    for(int i = 0; i < pmll.count; i++) {
        strncat(keys_buffer, pmll.pairs[i].key, buffer_size - strlen(keys_buffer) - 1);
        if(i < pmll.count -1) {
            strncat(keys_buffer, ", ", buffer_size - strlen(keys_buffer) - 1);
        }
    }

    pthread_mutex_unlock(&pmll.lock);
    printf("[PMLL] Listing all keys:\n");
    for(int i = 0; i < pmll.count; i++) {
        printf("  %s\n", pmll.pairs[i].key);
    }
    return 0;
}

// Clears all memory
int pmll_clear() {
    pthread_mutex_lock(&pmll.lock);
    pmll.count = 0;
    pthread_mutex_unlock(&pmll.lock);
    // Truncate the memory file
    FILE* file = fopen(pmll.memory_file, "w");
    if(file == NULL) {
        fprintf(stderr, "[PMLL] Error: Could not open file '%s' for clearing.\n", pmll.memory_file);
        return -1;
    }
    fclose(file);
    printf("[PMLL] All memory has been cleared.\n");
    return 0;
}

// Displays all key-value pairs (for debugging)
int pmll_display() {
    pthread_mutex_lock(&pmll.lock);
    if(pmll.count == 0) {
        printf("[PMLL] Memory is empty.\n");
        pthread_mutex_unlock(&pmll.lock);
        return 0;
    }

    printf("[PMLL] Current Memory State:\n");
    for(int i = 0; i < pmll.count; i++) {
        printf("  %s : %s\n", pmll.pairs[i].key, pmll.pairs[i].value);
    }
    pthread_mutex_unlock(&pmll.lock);
    return 0;
}

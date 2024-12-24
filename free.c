#include "free.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Internal helper functions
static bool attemptPrimaryFree(void* ptr);
static bool attemptAlternateFree(void* ptr);
static void efllErrorHandling(int errorFlag);

/**
 * Attempts to free memory with PMLL-ARLL-EFLL logic.
 */
bool dynamicFree(void* ptr) {
    if (!ptr) {
        logFreeError(EFLL_ERROR_NULL_POINTER);
        efllErrorHandling(EFLL_ERROR_NULL_POINTER);
        return false;
    }

    int retryCount = 0;
    bool success = false;

    // PMLL: Primary Memory Logic Loop
    while (retryCount < RETRY_LIMIT && !success) {
        success = attemptPrimaryFree(ptr);
        if (!success) {
            retryCount++;
            logFreeError(EFLL_ERROR_MEMORY_LEAK);
        }
    }

    // ARLL: Alternate Retry Logic Loop
    if (!success) {
        retryCount = 0;  // Reset retry count
        while (retryCount < RETRY_LIMIT && !success) {
            success = attemptAlternateFree(ptr);
            if (!success) {
                retryCount++;
                logFreeError(EFLL_ERROR_DOUBLE_FREE);
            }
        }
    }

    // EFLL: Error Flag Logic Loop
    if (!success) {
        efllErrorHandling(EFLL_ERROR_MEMORY_LEAK);
        return false;
    }

    return true;
}

/**
 * Attempts primary free logic.
 */
static bool attemptPrimaryFree(void* ptr) {
    if (!ptr) {
        return false;
    }

    free(ptr);
    ptr = NULL;  // Nullify pointer after free
    return true;
}

/**
 * Attempts alternate free logic.
 */
static bool attemptAlternateFree(void* ptr) {
    if (!ptr) {
        return false;
    }

    // Alternate cleanup mechanism (e.g., custom allocators, backup systems)
    memset(ptr, 0, sizeof(ptr));  // Clear memory as a fallback
    free(ptr);
    ptr = NULL;
    return true;
}

/**
 * Logs errors encountered during the free process.
 */
void logFreeError(int errorFlag) {
    const char* errorMessage;

    switch (errorFlag) {
        case EFLL_ERROR_MEMORY_LEAK:
            errorMessage = "Memory leak detected.";
            break;
        case EFLL_ERROR_DOUBLE_FREE:
            errorMessage = "Double free attempt detected.";
            break;
        case EFLL_ERROR_NULL_POINTER:
            errorMessage = "Null pointer passed to free.";
            break;
        default:
            errorMessage = "Unknown error during free.";
            break;
    }

    fprintf(stderr, "Error: %s\n", errorMessage);
}

/**
 * Handles errors based on EFLL logic.
 */
static void efllErrorHandling(int errorFlag) {
    switch (errorFlag) {
        case EFLL_ERROR_MEMORY_LEAK:
            fprintf(stderr, "Fatal: Unable to resolve memory leak after retries.\n");
            exit(EXIT_FAILURE);
        case EFLL_ERROR_DOUBLE_FREE:
            fprintf(stderr, "Fatal: Double free detected. Investigate memory logic.\n");
            exit(EXIT_FAILURE);
        case EFLL_ERROR_NULL_POINTER:
            fprintf(stderr, "Warning: Null pointer encountered. Skipping free.\n");
            break;
        default:
            fprintf(stderr, "Unknown error encountered. Debug required.\n");
            exit(EXIT_FAILURE);
    }
}

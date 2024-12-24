#ifndef FREE_H
#define FREE_H

#include <stdbool.h>

// Maximum retry attempts
#define RETRY_LIMIT 3

// Error flags for EFLL
#define EFLL_ERROR_NONE 0
#define EFLL_ERROR_MEMORY_LEAK 1
#define EFLL_ERROR_DOUBLE_FREE 2
#define EFLL_ERROR_NULL_POINTER 3

// Function Declarations

/**
 * Attempts to free memory with PMLL-ARLL-EFLL logic.
 * Uses primary memory cleanup strategies and dynamically retries with alternates.
 * @param ptr A pointer to the memory to be freed.
 * @return True if the memory was successfully freed, false otherwise.
 */
bool dynamicFree(void* ptr);

/**
 * Logs any errors encountered during the free process.
 * @param errorFlag The error flag to log.
 */
void logFreeError(int errorFlag);

#endif // FREE_H

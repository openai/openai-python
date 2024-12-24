#ifndef PMLL_ARLL_EFLL_H
#define PMLL_ARLL_EFLL_H

#include <jansson.h> // JSON library for data handling
#include <stdbool.h> // For boolean operations
#include "PMLL_ARLL.h" // Base PMLL_ARLL functionality

// Structure for EFLL (External Feedback Logic Loop)
typedef struct {
    bool is_active;               // Indicates if EFLL is enabled
    int feedback_threshold;       // Number of retries before EFLL activation
    int current_retries;          // Current retry count
} EFLL_State;

// Combined PMLL-ARLL-EFLL State
typedef struct {
    PMLL_ARLL_State pmll_arll;    // PMLL_ARLL state
    EFLL_State efll;              // EFLL state
} PMLL_ARLL_EFLL_State;

// Initialization function for the combined state
void pmll_arll_efll_init(PMLL_ARLL_EFLL_State *state, int max_retries, int feedback_threshold);

// Process a chunk of data with PMLL and optionally EFLL
int pmll_arll_efll_process(PMLL_ARLL_EFLL_State *state, const char *chunk, size_t chunk_size);

// Trigger EFLL when necessary
void trigger_efll(PMLL_ARLL_EFLL_State *state);

// Write to the knowledge graph
void pmll_arll_efll_write_to_knowledge_graph(PMLL_ARLL_EFLL_State *state);

// Cleanup resources
void pmll_arll_efll_cleanup(PMLL_ARLL_EFLL_State *state);

// Log utility function
void log_message(const char *level, const char *message);

#endif // PMLL_ARLL_EFLL_H

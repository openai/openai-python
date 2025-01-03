#ifndef PMLL_ARLL_H
#define PMLL_ARLL_H

#include <jansson.h> // JSON processing library
#include <time.h>    // For timestamp functionality

// Constants
#define RETRY_LIMIT 5
#define CHUNK_SIZE 256
#define BUFFER_SIZE 1024

// Struct for logic loop state
typedef struct {
    int retries;            // Current retry count
    int max_retries;        // Maximum allowed retries
    char buffer[BUFFER_SIZE]; // Buffer to store incoming data
    json_t *json;           // Parsed JSON object
} PMLL_ARLL_State;

// Function prototypes
void pmll_arll_init(PMLL_ARLL_State *state, int max_retries);
int pmll_arll_process_chunk(PMLL_ARLL_State *state, const char *chunk, size_t chunk_size);
void pmll_arll_write_to_knowledge_graph(PMLL_ARLL_State *state);
void pmll_arll_cleanup(PMLL_ARLL_State *state);
void log_message(const char *level, const char *message);

#endif // PMLL_ARLL_H

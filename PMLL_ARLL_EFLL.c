#include "PMLL_ARLL_EFLL.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void pmll_arll_efll_init(PMLL_ARLL_EFLL_State *state, int max_retries, int feedback_threshold) {
    if (!state) {
        fprintf(stderr, "Error: PMLL_ARLL_EFLL_State is NULL during initialization.\n");
        exit(EXIT_FAILURE);
    }

    // Initialize PMLL_ARLL
    pmll_arll_init(&state->pmll_arll, max_retries);

    // Initialize EFLL
    state->efll.is_active = false;
    state->efll.feedback_threshold = feedback_threshold;
    state->efll.current_retries = 0;

    log_message("INFO", "PMLL_ARLL_EFLL initialized successfully.");
}

int pmll_arll_efll_process(PMLL_ARLL_EFLL_State *state, const char *chunk, size_t chunk_size) {
    if (!state || !chunk || chunk_size == 0) {
        log_message("ERROR", "Invalid parameters in PMLL_ARLL_EFLL process.");
        return -1;
    }

    int result = pmll_arll_process_chunk(&state->pmll_arll, chunk, chunk_size);

    if (result == 1) {
        // Successful processing, reset EFLL retry count
        state->efll.current_retries = 0;
        return 1; // Success
    } else {
        // Increment retries and check EFLL activation
        state->efll.current_retries++;
        if (state->efll.current_retries >= state->efll.feedback_threshold) {
            trigger_efll(state);
        }
        return 0; // Retry
    }
}

void trigger_efll(PMLL_ARLL_EFLL_State *state) {
    if (!state) {
        log_message("ERROR", "State is NULL in trigger_efll.");
        return;
    }

    if (!state->efll.is_active) {
        log_message("INFO", "EFLL activated due to retry threshold.");
        state->efll.is_active = true;

        // Example external feedback logic
        printf("[EFLL] Gathering external feedback...\n");
        printf("[EFLL] Performing external diagnostics...\n");
        printf("[EFLL] Adjusting knowledge graph parameters...\n");

        // Reset retry count after EFLL activation
        state->efll.current_retries = 0;
    }
}

void pmll_arll_efll_write_to_knowledge_graph(PMLL_ARLL_EFLL_State *state) {
    if (!state) {
        log_message("ERROR", "State is NULL in knowledge graph writing.");
        return;
    }

    if (state->efll.is_active) {
        printf("[EFLL] Writing external feedback data to the knowledge graph...\n");
    }

    pmll_arll_write_to_knowledge_graph(&state->pmll_arll);
}

void pmll_arll_efll_cleanup(PMLL_ARLL_EFLL_State *state) {
    if (!state) return;

    // Cleanup PMLL_ARLL resources
    pmll_arll_cleanup(&state->pmll_arll);

    // Reset EFLL state
    state->efll.is_active = false;
    state->efll.current_retries = 0;

    log_message("INFO", "PMLL_ARLL_EFLL resources cleaned up.");
}

void log_message(const char *level, const char *message) {
    time_t now = time(NULL);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    printf("[%s] [%s] %s\n", level, timestamp, message);
}

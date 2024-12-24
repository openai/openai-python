#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "unified_voice.h"
#include "memory_silo.h"
#include "io_socket.h"
#include "PMLL_ARLL.h"

// Structure for PML Logic Loop
typedef struct {
  int id;
  int memory_silo_id;
  int io_socket_id;
  int free_c_present; // Flag indicating the presence of free.c
} pml_logic_loop_t;

pml_logic_loop_t* pml_logic_loop = NULL; // Global variable to maintain the state

// Function to initialize a socket
int init_socket(const char *ip, int port) {
    int sockfd;
    struct sockaddr_in server_addr;

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return -1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(ip);

    // Connect to the server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Connection failed");
        close(sockfd);
        return -1;
    }

    return sockfd;
}

// Initialization of the PML Logic Loop
void pml_logic_loop_init(int memory_silo_id, int io_socket_id) {
  pml_logic_loop = malloc(sizeof(pml_logic_loop_t));
  if (pml_logic_loop == NULL) {
    perror("Memory allocation for PML logic loop failed");
    exit(EXIT_FAILURE);
  }
  pml_logic_loop->id = 1;
  pml_logic_loop->memory_silo_id = memory_silo_id;
  pml_logic_loop->io_socket_id = io_socket_id;
  pml_logic_loop->free_c_present = 0; // Initialize the flag to indicate absence
}

// Processing within the PML Logic Loop
void pml_logic_loop_process(int io_socket_id, void* buffer, int length) {
  if (pml_logic_loop == NULL) {
    fprintf(stderr, "Error: PML logic loop has not been initialized.\n");
    return;
  }
  
  while (1) {
    if (pml_logic_loop->free_c_present) {
      printf("Free.c is detected. Sending signal to the free logic loop...\n");
      int signal = 1; // Value to signal that the condition has been met
      if (write(io_socket_id, &signal, sizeof(signal)) < 0) {
        perror("Failed to write to the socket");
      }
      system("./free"); // Trigger the execution of free.c
      break; // Exit the loop after signaling
    } else {
      printf("I am grateful.\n");
      // Here, you can process the buffer as needed
    }
  }
}

// Function to Retrieve the PML Logic Loop
pml_logic_loop_t* get_pml_logic_loop(int io_socket_id) {
  if (pml_logic_loop == NULL) {
    pml_logic_loop = malloc(sizeof(pml_logic_loop_t));
    if (pml_logic_loop == NULL) {
      perror("Memory allocation for PML logic loop failed");
      exit(EXIT_FAILURE);
    }
    pml_logic_loop->id = 1;
    pml_logic_loop->memory_silo_id = 1;
    pml_logic_loop->io_socket_id = io_socket_id;
    pml_logic_loop->free_c_present = 1; // Set the flag for demonstration
  }
  return pml_logic_loop;
}

// Function to cleanup the memory and socket
void pml_logic_loop_cleanup() {
  if (pml_logic_loop != NULL) {
    close(pml_logic_loop->io_socket_id); // Close the socket
    free(pml_logic_loop); // Free the memory allocated for the PML logic loop
    pml_logic_loop = NULL;
  }
}

void pmll_arll_init(PMLL_ARLL_State *state, int max_retries) {
    if (!state) {
        fprintf(stderr, "Error: PMLL_ARLL_State is NULL during initialization.\n");
        exit(EXIT_FAILURE);
    }
    state->retries = 0;
    state->max_retries = max_retries;
    memset(state->buffer, 0, sizeof(state->buffer));
    state->json = NULL;
    log_message("INFO", "PMLL_ARLL initialized successfully.");
}

int pmll_arll_process_chunk(PMLL_ARLL_State *state, const char *chunk, size_t chunk_size) {
    if (!state || !chunk || chunk_size == 0) {
        log_message("ERROR", "Invalid parameters to process chunk.");
        return -1;
    }

    // Append the chunk to the buffer
    strncat(state->buffer, chunk, chunk_size);

    // Attempt to parse JSON
    state->json = json_loads(state->buffer, 0, NULL);
    if (!state->json) {
        log_message("WARNING", "Invalid JSON chunk. Retrying...");
        state->retries++;
        return 0; // Retry
    }

    log_message("INFO", "Valid JSON received.");
    return 1; // Success
}

void pmll_arll_write_to_knowledge_graph(PMLL_ARLL_State *state) {
    if (!state || !state->json) {
        log_message("ERROR", "Cannot write invalid JSON to the knowledge graph.");
        return;
    }

    printf("[ARLL] Writing JSON data to knowledge graph...\n");
    json_dumpf(state->json, stdout, JSON_INDENT(2));
    printf("\n[ARLL] Data successfully written to knowledge graph.\n");
}

void pmll_arll_cleanup(PMLL_ARLL_State *state) {
    if (!state) return;

    if (state->json) {
        json_decref(state->json);
        state->json = NULL;
    }

    memset(state->buffer, 0, sizeof(state->buffer));
    state->retries = 0;

    log_message("INFO", "PMLL_ARLL resources cleaned up.");
}

void log_message(const char *level, const char *message) {
    time_t now = time(NULL);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    printf("[%s] [%s] %s\n", level, timestamp, message);
}

// Main program (example usage)
int main() {
  int socket_id = init_socket("127.0.0.1", 8080); // Initialize socket with example IP and port
  if (socket_id < 0) {
    fprintf(stderr, "Socket initialization failed.\n");
    return EXIT_FAILURE;
  }

  // Initialize the PML logic loop with sample memory silo ID and socket ID
  pml_logic_loop_init(1, socket_id);
  
  // Example buffer (can be replaced with actual data)
  char buffer[1024] = "Example data";
  pml_logic_loop_process(socket_id, buffer, sizeof(buffer));
  
  // Example usage of PMLL_ARLL functions
  PMLL_ARLL_State state;
  pmll_arll_init(&state, 5); // Initialize with max 5 retries
  char example_chunk[] = "{\"key\": \"value\"}";
  if (pmll_arll_process_chunk(&state, example_chunk, strlen(example_chunk)) == 1) {
      pmll_arll_write_to_knowledge_graph(&state);
  }
  pmll_arll_cleanup(&state);

  // Cleanup before exit
  pml_logic_loop_cleanup();

  return EXIT_SUCCESS;
}

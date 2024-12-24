#include <cuda_runtime.h>
#include <stdio.h>
#include <math.h>  // For pairwise distance calculations

#define BLOCK_SIZE 256          // Threads per block
#define MAX_CLUSTERS 9          // Total clusters
#define MAX_ITERATIONS 1024     // Total iterations
#define MAX_NODES 1024          // Nodes for TSP example
#define INF 1e9                 // Infinity for TSP comparison

// Error checking macro
#define CUDA_CHECK(call)                                 \
    do {                                                 \
        cudaError_t err = call;                          \
        if (err != cudaSuccess) {                        \
            fprintf(stderr, "CUDA Error: %s\n",          \
                    cudaGetErrorString(err));            \
            exit(err);                                   \
        }                                                \
    } while (0)

// Device function for distance calculation
__device__ float calculate_distance(float x1, float y1, float x2, float y2) {
    return sqrtf((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}

// Device function for EFLL to check memory integrity
__device__ bool EFLL_JudgeMemory(const float *memory_data, int size) {
    float threshold = 0.5; // Arbitrary threshold for obfuscation
    float total_variance = 0.0;

    for (int i = 1; i < size; ++i) {
        total_variance += fabsf(memory_data[i] - memory_data[i - 1]);
    }

    // Memory is considered "good" if variance is below threshold
    return (total_variance / size) < threshold;
}

// Kernel for logic loop iteration with ARLL and EFLL
__global__ void LogicLoop_GPU(
    int *cluster_states, float *node_positions, float *memory_data,
    int num_nodes, int max_iterations, int *iteration_count, int *arll_rewards, int *efll_flags) 
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int cluster_id = blockIdx.x;  // Each block handles one cluster

    if (tid < num_nodes) {
        // Loop over the maximum iterations
        for (int iter = 0; iter < max_iterations; ++iter) {
            // Calculate pairwise distances for TSP-like logic
            __shared__ float local_min_distance;  // Shared memory for results
            __shared__ int best_node;
            if (threadIdx.x == 0) {
                local_min_distance = INF;
                best_node = -1;
            }
            __syncthreads();

            for (int i = 0; i < num_nodes; ++i) {
                float distance = calculate_distance(
                    node_positions[2 * tid],     // x-coordinate of current node
                    node_positions[2 * tid + 1], // y-coordinate of current node
                    node_positions[2 * i],       // x-coordinate of node i
                    node_positions[2 * i + 1]    // y-coordinate of node i
                );

                if (distance < local_min_distance && tid != i) {
                    local_min_distance = distance;
                    best_node = i;
                }
            }

            // Update global cluster state atomically
            if (threadIdx.x == 0) {
                atomicAdd(&cluster_states[cluster_id], best_node);
            }
            __syncthreads();  // Synchronize before next iteration

            // Update iteration count
            if (tid == 0) {
                atomicAdd(iteration_count, 1);

                // EFLL checks memory integrity
                bool is_good_memory = EFLL_JudgeMemory(memory_data, num_nodes);
                atomicAdd(&efll_flags[tid], is_good_memory ? 0 : 1);

                // ARLL rewards "good" memory
                if (is_good_memory) {
                    atomicAdd(&arll_rewards[tid], 1);
                }
            }
        }
    }
}

void RunLogicLoop() {
    // Host variables
    int h_cluster_states[MAX_CLUSTERS] = {0};
    float h_node_positions[2 * MAX_NODES];
    float h_memory_data[MAX_NODES]; // Simulated memory data
    int h_iteration_count = 0;
    int h_arll_rewards[MAX_NODES] = {0};
    int h_efll_flags[MAX_NODES] = {0};

    // Initialize node positions and memory data
    for (int i = 0; i < MAX_NODES; ++i) {
        h_node_positions[2 * i] = rand() % 100;
        h_node_positions[2 * i + 1] = rand() % 100;
        h_memory_data[i] = ((float)rand() / RAND_MAX); // Random memory values
    }

    // Device variables
    int *d_cluster_states, *d_iteration_count, *d_arll_rewards, *d_efll_flags;
    float *d_node_positions, *d_memory_data;

    // Allocate device memory
    CUDA_CHECK(cudaMalloc((void **)&d_cluster_states, MAX_CLUSTERS * sizeof(int)));
    CUDA_CHECK(cudaMalloc((void **)&d_node_positions, 2 * MAX_NODES * sizeof(float)));
    CUDA_CHECK(cudaMalloc((void **)&d_memory_data, MAX_NODES * sizeof(float)));
    CUDA_CHECK(cudaMalloc((void **)&d_iteration_count, sizeof(int)));
    CUDA_CHECK(cudaMalloc((void **)&d_arll_rewards, MAX_NODES * sizeof(int)));
    CUDA_CHECK(cudaMalloc((void **)&d_efll_flags, MAX_NODES * sizeof(int)));

    // Copy data to device
    CUDA_CHECK(cudaMemcpy(d_cluster_states, h_cluster_states, MAX_CLUSTERS * sizeof(int), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_node_positions, h_node_positions, 2 * MAX_NODES * sizeof(float), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_memory_data, h_memory_data, MAX_NODES * sizeof(float), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemset(d_iteration_count, 0, sizeof(int)));
    CUDA_CHECK(cudaMemset(d_arll_rewards, 0, MAX_NODES * sizeof(int)));
    CUDA_CHECK(cudaMemset(d_efll_flags, 0, MAX_NODES * sizeof(int)));

    // Define grid and block dimensions
    dim3 blockSize(BLOCK_SIZE);
    dim3 gridSize(MAX_CLUSTERS);

    // Launch kernel
    LogicLoop_GPU<<<gridSize, blockSize>>>(
        d_cluster_states, d_node_positions, d_memory_data, MAX_NODES,
        MAX_ITERATIONS, d_iteration_count, d_arll_rewards, d_efll_flags);

    // Synchronize device
    CUDA_CHECK(cudaDeviceSynchronize());

    // Copy results back to host
    CUDA_CHECK(cudaMemcpy(h_cluster_states, d_cluster_states, MAX_CLUSTERS * sizeof(int), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(&h_iteration_count, d_iteration_count, sizeof(int), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_arll_rewards, d_arll_rewards, MAX_NODES * sizeof(int), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_efll_flags, d_efll_flags, MAX_NODES * sizeof(int), cudaMemcpyDeviceToHost));

    // Display results
    printf("Total iterations processed: %d\n", h_iteration_count);
    for (int i = 0; i < MAX_CLUSTERS; ++i) {
        printf("Cluster %d state: %d\n", i, h_cluster_states[i]);
    }
    for (int i = 0; i < MAX_NODES; ++i) {
        printf("Node %d - ARLL Rewards: %d, EFLL Flags: %d\n", i, h_arll_rewards[i], h_efll_flags[i]);
    }

    // Free device memory
    CUDA_CHECK(cudaFree(d_cluster_states));
    CUDA_CHECK(cudaFree(d_node_positions));
    CUDA_CHECK(cudaFree(d_memory_data));
    CUDA_CHECK(cudaFree(d_iteration_count));
    CUDA_CHECK(cudaFree(d_arll_rewards));
    CUDA_CHECK(cudaFree(d_efll_flags));
}

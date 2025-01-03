#ifndef GPU_H
#define GPU_H

#include <cuda_runtime.h>

#define BLOCK_SIZE 256          // Threads per block
#define MAX_CLUSTERS 9          // Total clusters
#define MAX_ITERATIONS 1024     // Total iterations
#define MAX_NODES 1024          // Nodes for TSP example
#define INF 1e9                 // Infinity for TSP comparison

// Function prototypes

/**
 * @brief Runs the complete logic loop on the GPU, integrating PMLL, ARLL, and EFLL logic.
 */
void RunLogicLoop();

/**
 * @brief CUDA device function to calculate pairwise Euclidean distance.
 * @param x1 X-coordinate of the first point.
 * @param y1 Y-coordinate of the first point.
 * @param x2 X-coordinate of the second point.
 * @param y2 Y-coordinate of the second point.
 * @return Euclidean distance between the two points.
 */
__device__ float calculate_distance(float x1, float y1, float x2, float y2);

/**
 * @brief CUDA device function for EFLL to judge memory integrity.
 * @param memory_data Pointer to the memory data array.
 * @param size Number of memory elements.
 * @return True if memory is judged as "good," false otherwise.
 */
__device__ bool EFLL_JudgeMemory(const float *memory_data, int size);

/**
 * @brief CUDA kernel to run logic loops with PMLL, ARLL, and EFLL.
 * @param cluster_states Array to store the state of each cluster.
 * @param node_positions Array of node positions (x, y for each node).
 * @param memory_data Array representing memory state for EFLL.
 * @param num_nodes Number of nodes.
 * @param max_iterations Maximum number of iterations to process.
 * @param iteration_count Pointer to the total iteration count.
 * @param arll_rewards Array to store ARLL rewards for each node.
 * @param efll_flags Array to store EFLL flags indicating "bad" memory.
 */
__global__ void LogicLoop_GPU(
    int *cluster_states, float *node_positions, float *memory_data,
    int num_nodes, int max_iterations, int *iteration_count, 
    int *arll_rewards, int *efll_flags);

#endif // GPU_Ho

#include <stdio.h>

// Define the dimensions of the 3D space
#define DEPTH  3 // z-axis
#define HEIGHT 3 // y-axis
#define WIDTH  4 // x-axis

int main() {
    printf("Iterating with a perfectly nested 3D loop:\n");

    // The loops are nested directly inside one another.
    // The outer loop iterates through the depth (z-axis).
    for (int i = 0; i < DEPTH; i++) {
        // The middle loop iterates through the height (y-axis).
        for (int j = 0; j < HEIGHT; j++) {
            // The inner loop iterates through the width (x-axis).
            for (int k = 0; k < WIDTH; k++) {
                // The work is done only in the innermost loop.
                printf("  (i=%d, j=%d, k=%d)\n", i, j, k);
            }
        }
    }

    return 0;
}
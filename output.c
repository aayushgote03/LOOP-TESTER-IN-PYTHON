#include <stdio.h>
#define DEPTH 3
#define HEIGHT 4
#define WIDTH 5
int main() {
    int i, j, k;
    int result[DEPTH][HEIGHT][WIDTH];
    // Loop through 3D space
    for (i = 0; i < DEPTH; i++) {
        for (j = 0; j < HEIGHT; j++) {
            for (k = 0; k < WIDTH; k++) {
                // Perform some operation - e.g., a simple formula
                result[i][j][k] = i * 100 + j * 10 + k;
                // Print the value
                printf("result[%d][%d][%d] = %d\n", i, j, k, result[i][j][k]);
            }
        }
    }
    return 0;
}

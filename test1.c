// --- 2. Processing Phase ---
#include <stdio.h>

#define DEPTH  1024  // z-axis
#define HEIGHT 1024   // y-axis
#define WIDTH  1024   // x-axis

#define FD 3   // filter depth
#define FH 3   // filter height
#define FW 3   // filter width

// 3D tensors
static float input[DEPTH][HEIGHT][WIDTH];
static float output[DEPTH][HEIGHT][WIDTH];
static float filter[FD][FH][FW];

int main() {
    // --- 1. Initialization ---
    for (int i = 0; i < DEPTH; i++) {
        for (int j = 0; j < HEIGHT; j++) {
            for (int k = 0; k < WIDTH; k++) {
                input[i][j][k] = (i + j + k) % 11 * 0.1f;
                output[i][j][k] = 0.0f;
            }
        }
    }
    for (int d = 0; d < FD; d++) {
        for (int h = 0; h < FH; h++) {
            for (int w = 0; w < FW; w++) {
                filter[d][h][w] = (d + h + w) % 5 * 0.05f;
            }
        }
    }

    // --- 2. Processing Phase ---
    for (int i = 0; i < DEPTH; i++) {
        for (int j = 0; j < HEIGHT; j++) {
            for (int k = 0; k < WIDTH; k++) {
                float acc = 0.0f;

                // Sliding window with boundary check
                for (int fd = 0; fd < FD; fd++) {
                    for (int fh = 0; fh < FH; fh++) {
                        for (int fw = 0; fw < FW; fw++) {
                            int zz = i + fd - 1;
                            int yy = j + fh - 1;
                            int xx = k + fw - 1;

                            if (zz >= 0 && zz < DEPTH &&
                                yy >= 0 && yy < HEIGHT &&
                                xx >= 0 && xx < WIDTH) {
                                acc += input[zz][yy][xx] * filter[fd][fh][fw];
                            }
                        }
                    }
                }

                // ReLU activation
                output[i][j][k] = acc > 0 ? acc : 0;

                // Residual connection
                output[i][j][k] += input[i][j][k] * 0.1f;
            }
        }
    }

    // --- 3. Verification ---
    printf("Sample outputs:\n");
    printf("  out[0][0][0] = %.3f\n", output[0][0][0]);
    printf("  out[10][10][10] = %.3f\n", output[10][10][10]);
    printf("  out[%d][%d][%d] = %.3f\n",
           DEPTH-1, HEIGHT-1, WIDTH-1,
           output[DEPTH-1][HEIGHT-1][WIDTH-1]);

    return 0;
}

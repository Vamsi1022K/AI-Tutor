#include <stdio.h>

int main() {
    int total = 10;
    int x = 5;

    // Intentional runtime issue for static detection
    int bad = x / 0;
    printf("bad = %d\n", bad);

    // Intentional infinite loop pattern for detection
    for (;;) {
        total++;
        printf("total = %d\n", total);
    }

    return 0;
}

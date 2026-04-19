// Error ID: E016 – Array Out of Bounds Access
// Category: Memory Error
// GCC sees this with -Wall -Warray-bounds
// To force the warning: compile with -O2 -Warray-bounds

#include <stdio.h>

int main() {
    int numbers[3] = {10, 20, 30};  // indices: 0, 1, 2 only
    int x = numbers[5];             // <-- index 5 does NOT exist!
    printf("%d\n", x);
    return 0;
}

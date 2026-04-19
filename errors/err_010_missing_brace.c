// Week 6 – Error Collection
// Error ID: E015 – Missing Closing Brace
// Category: Syntax Error
// Expected GCC Error: error: expected '}' at end of input

#include <stdio.h>

int main() {
    int x = 5;
    printf("%d\n", x);
    return 0;
// <-- closing '}' for main() is intentionally missing

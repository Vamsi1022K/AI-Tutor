// Error ID: E025 – Integer Overflow
// Category: Overflow Error
// GCC warning: warning: integer overflow in expression

#include <stdio.h>
#include <limits.h>

int main() {
    int result = INT_MAX + 1;   // <-- INT_MAX = 2147483647, +1 overflows!
    printf("%d\n", result);
    return 0;
}

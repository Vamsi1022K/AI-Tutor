// Error ID: E021 – Non-void Function Missing Return
// Category: Scope Error
// Expected GCC Warning: warning: control reaches end of non-void function

#include <stdio.h>

int square(int n) {
    int result = n * n;
    // <-- forgot to write: return result;
}

int main() {
    printf("%d\n", square(5));
    return 0;
}

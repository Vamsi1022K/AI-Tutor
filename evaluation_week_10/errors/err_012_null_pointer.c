// Error ID: E017 – Null Pointer Dereference
// Category: Pointer Error
// GCC error: error: indirection requires pointer operand

#include <stdio.h>

int main() {
    int *ptr = 0;    // 0 = NULL — points to nothing
    int val  = *ptr; // <-- cannot dereference a null pointer!
    printf("%d\n", val);
    return 0;
}

// Error ID: E029 – Array Initializer Has Too Many Elements
// Category: Syntax Error
// Expected GCC Warning: warning: excess elements in array initializer

#include <stdio.h>

int main() {
    int arr[3] = {1, 2, 3, 4, 5};  // <-- declared size 3 but 5 values given!
    printf("%d\n", arr[0]);
    return 0;
}

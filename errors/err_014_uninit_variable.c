// Error ID: E019 – Uninitialized Variable
// Category: Logic Error
// Expected GCC Warning: warning: 'x' is used uninitialized

#include <stdio.h>

int main() {
    int x;              // <-- declared but never given a value!
    printf("%d\n", x);  // using x here gives garbage / random number
    return 0;
}

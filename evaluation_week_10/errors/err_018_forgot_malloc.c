// Error ID: E023 – Using Pointer Without malloc
// Category: Memory Error
// Expected GCC Warning: warning: 'ptr' is used uninitialized

#include <stdio.h>

int main() {
    int *ptr;       // <-- pointer declared but no memory allocated!
    *ptr = 100;     // writing to unallocated memory — crashes!
    printf("%d\n", *ptr);
    return 0;
}

// Week 6 – Error Collection
// Error ID: E003 – Incompatible Types
// Category: Type Error
// Expected GCC Error: error: incompatible types when assigning to type 'int'

#include <stdio.h>

int main() {
    int x;
    x = "hello";  // <-- cannot assign string to int
    printf("%d\n", x);
    return 0;
}

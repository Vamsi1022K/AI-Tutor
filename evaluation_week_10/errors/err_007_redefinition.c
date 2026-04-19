// Week 6 – Error Collection
// Error ID: E009 – Redefinition of Variable
// Category: Declaration Error
// Expected GCC Error: error: redefinition of 'x'

#include <stdio.h>

int main() {
    int x = 5;
    int x = 10;  // <-- 'x' already declared above
    printf("%d\n", x);
    return 0;
}

// Week 6 – Error Collection
// Error ID: E002 – Undeclared Variable
// Category: Declaration Error
// Expected GCC Error: error: 'y' undeclared (first use in this function)

#include <stdio.h>

int main() {
    printf("%d\n", y);  // <-- 'y' was never declared
    return 0;
}

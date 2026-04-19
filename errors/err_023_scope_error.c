// Error ID: E028 – Variable Used Outside Its Scope
// Category: Scope Error
// Expected GCC Error: error: 'total' undeclared (first use in this function)

#include <stdio.h>

int main() {
    if (1) {
        int total = 100;   // total exists only inside this { } block
    }
    printf("%d\n", total); // <-- total is out of scope here!
    return 0;
}

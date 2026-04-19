// Week 6 – Error Collection
// Error ID: E006 – Too Few Arguments
// Category: Syntax Error
// Expected GCC Error: error: too few arguments to function 'add'

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(5);  // <-- add() requires 2 arguments, only 1 given
    printf("%d\n", result);
    return 0;
}

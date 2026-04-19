// Week 6 – Error Collection
// Error ID: E005 – Missing Closing Parenthesis
// Category: Syntax Error
// Expected GCC Error: error: expected ')' before ';' token

#include <stdio.h>

int main() {
    int x = (5 + 3;  // <-- missing closing parenthesis ')'
    printf("%d\n", x);
    return 0;
}

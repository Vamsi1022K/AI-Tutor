// Week 6 – Error Collection
// Error ID: E001 – Missing Semicolon
// Category: Syntax Error
// Expected GCC Error: error: expected ';' before 'printf'

#include <stdio.h>

int main() {
    int x = 5   // <-- missing semicolon here
    printf("%d\n", x);
    return 0;
}

// Week 6 – Error Collection
// Error ID: E010 – Return Value in Void Function
// Category: Scope Error
// Expected GCC Error: error: return with a value, in function returning void

#include <stdio.h>

void greet() {
    printf("Hello!\n");
    return 42;  // <-- void function cannot return a value
}

int main() {
    greet();
    return 0;
}

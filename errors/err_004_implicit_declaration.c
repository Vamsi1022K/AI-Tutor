// Week 6 – Error Collection
// Error ID: E004 – Implicit Function Declaration
// Category: Declaration Error
// Expected GCC Warning: implicit declaration of function 'printf'
// Note: No #include <stdio.h> is intentionally missing

int main() {
    printf("Hello, World!\n");  // <-- printf used without #include <stdio.h>
    return 0;
}

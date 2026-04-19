// Error ID: E024 – Missing math.h Header
// Category: Declaration Error
// Expected GCC Error: warning: implicit declaration of function 'sqrt'

#include <stdio.h>
// <-- missing: #include <math.h>

int main() {
    double result = sqrt(16.0);   // sqrt is in math.h — not included!
    printf("%.2f\n", result);
    return 0;
}

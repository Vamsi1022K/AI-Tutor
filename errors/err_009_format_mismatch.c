// Week 6 – Error Collection
// Error ID: E011 – Format String Mismatch
// Category: Type Error
// Expected GCC Warning: format '%d' expects int but argument has type 'double'

#include <stdio.h>

int main() {
    double x = 3.14;
    printf("%d\n", x);  // <-- %d is for int, but x is double (use %f or %lf)
    return 0;
}

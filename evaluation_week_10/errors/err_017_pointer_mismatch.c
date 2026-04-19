// Error ID: E022 – Pointer Type Mismatch
// Category: Pointer Error
// Expected GCC Warning: warning: assignment from incompatible pointer type

#include <stdio.h>

int main() {
    int  num = 42;
    int  *int_ptr  = &num;
    double *dbl_ptr = int_ptr;  // <-- int* assigned to double* — wrong types!
    printf("%f\n", *dbl_ptr);
    return 0;
}

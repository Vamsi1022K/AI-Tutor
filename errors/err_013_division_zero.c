// Error ID: E018 – Division by Zero
// Category: Logic Error
// GCC warning: warning: division by zero [-Wdiv-by-zero]

#include <stdio.h>

int main() {
    int numerator   = 10;
    int denominator = 0;
    int result = numerator / 0;   // <-- literal 0 triggers GCC warning
    printf("Result: %d\n", result);
    return 0;
}

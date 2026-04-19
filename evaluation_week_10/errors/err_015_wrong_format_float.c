// Error ID: E020 – Wrong Format Specifier for Float
// Category: Type Error
// Expected GCC Warning: format '%d' expects type 'int' but argument has type 'float'

#include <stdio.h>

int main() {
    float temperature = 36.6;
    printf("Temp: %d\n", temperature);  // <-- %d is for int, not float!
    return 0;
}

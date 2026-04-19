// Error ID: E026 – Char Arithmetic Misuse
// Category: Type Error
// Expected GCC Warning: warning: overflow in conversion from 'int' to 'char'

#include <stdio.h>

int main() {
    char c = 300;   // <-- char can hold -128 to 127, 300 overflows!
    printf("%d\n", c);
    return 0;
}

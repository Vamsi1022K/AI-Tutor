// Week 11 – Security Demo
// Error ID: SECURITY – Unsafe C Functions Demo
// Category: Security / Buffer Overflow Risks
// Purpose: Demonstrates ALL unsafe C functions caught by the Security Scanner

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
    char buffer[64];
    char dest[32];
    char name[50];

    // UNSAFE: gets() — no length limit, causes buffer overflow
    gets(buffer);

    // UNSAFE: strcpy() — doesn't check destination size
    strcpy(dest, buffer);

    // UNSAFE: scanf("%s") — unlimited input, overflow possible
    scanf("%s", name);

    // UNSAFE: strcat() — doesn't check destination size
    strcat(dest, name);

    // UNSAFE: sprintf() — can overflow the output buffer
    char msg[32];
    sprintf(msg, "Hello, %s!", name);

    // UNSAFE: system() — shell injection risk
    system("ls");

    // UNSAFE: malloc without NULL check
    int *ptr = malloc(100 * sizeof(int));
    ptr[0] = 42;

    // UNSAFE: free without setting NULL — potential use-after-free
    free(ptr);
    printf("Value: %d\n", ptr[0]);  // BUG: use after free

    return 0;
}

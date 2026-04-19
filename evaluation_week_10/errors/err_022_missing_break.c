// Error ID: E027 – Missing break in switch
// Category: Logic Error
// GCC warning: warning: this statement may fall through [-Wimplicit-fallthrough]

#include <stdio.h>

int main() {
    int day = 1;
    switch (day) {
        case 1:
            printf("Monday\n");
            /* no break here — falls through to Tuesday! */
        case 2:
            printf("Tuesday\n");
            break;
        default:
            printf("Other day\n");
    }
    return 0;
}

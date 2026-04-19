// Error ID: E030 – Accessing Undefined Struct Field
// Category: Struct Error
// Expected GCC Error: error: 'struct Person' has no member named 'salary'

#include <stdio.h>

struct Person {
    char name[50];
    int  age;
    // no 'salary' field defined here
};

int main() {
    struct Person p;
    p.age    = 25;
    p.salary = 50000;  // <-- 'salary' field doesn't exist in struct!
    printf("%d\n", p.age);
    return 0;
}

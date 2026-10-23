
#include <stdio.h>

int main(void)
{
    const unsigned char bytes[] = {
        0x46, 0x47, 0x41, 0x31, 0x00
    };

    size_t count = sizeof bytes / sizeof bytes[0];

    for (size_t i = 0; i < count; i++) {
        printf(
            "Byte %zu: decimal=%u, hexadecimal=%02X\n",
            i,
            (unsigned int)bytes[i],
            (unsigned int)bytes[i]
        );
    }

    return 0;
}

#include "net/gcoap.h"
#include "shell.h"

#define ENABLE_DEBUG 0
#include "debug.h"

int main(void)
{
    puts("Start AIT CoAP Application");

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);

    return 0;
}
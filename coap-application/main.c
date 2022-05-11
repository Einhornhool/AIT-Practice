#include "net/gcoap.h"
#include "shell.h"
#include "coap_app.h"

#define ENABLE_DEBUG 0
#include "debug.h"

#define MAIN_QUEUE_SIZE (4)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

static const shell_command_t shell_commands[] = {
    { "saul-coap", "Control Sensors and LEDs via CoAP and SAUL", coap_saul_cli_cmd },
    { NULL, NULL, NULL }
};


int main(void)
{
    puts("Start AIT CoAP Application");

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    return 0;
}
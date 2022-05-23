#include "net/gcoap.h"
#include "shell.h"
#include "coap_app.h"

#define MAIN_QUEUE_SIZE (4)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

// static const shell_command_t shell_commands[] = {
//     { "saul-coap", "Control Sensors and LEDs via CoAP and SAUL", coap_saul_cli_cmd },
//     { NULL, NULL, NULL }
// };


int main(void)
{
    puts("Start AIT CoAP Application");

    /* for the thread running the shell */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    server_init();

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);

    return 0;
}
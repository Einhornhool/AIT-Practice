#include "net/gcoap.h"
#include "shell.h"
#include "coap_app.h"
#include "net/cord/common.h"
#include "net/cord/ep_standalone.h"

#define MAIN_QUEUE_SIZE (4)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

/* we will use a custom event handler for dumping cord_ep events */
static void _on_ep_event(cord_ep_standalone_event_t event)
{
    switch (event) {
        case CORD_EP_REGISTERED:
            puts("RD endpoint event: now registered with a RD");
            break;
        case CORD_EP_DEREGISTERED:
            puts("RD endpoint event: dropped client registration");
            break;
        case CORD_EP_UPDATED:
            puts("RD endpoint event: successfully updated client registration");
            break;
    }
}

int main(void)
{
    puts("Start AIT CoAP Application");

    /* for the thread running the shell */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    /* register event callback with cord_ep_standalone */
    cord_ep_standalone_reg_cb(_on_ep_event);

    server_init();

    puts("Client information:");
    printf("  ep: %s\n", cord_common_get_ep());
    printf("  lt: %is\n", (int)CONFIG_CORD_LT);

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);

    return 0;
}
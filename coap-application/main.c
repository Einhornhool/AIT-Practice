#include "net/gcoap.h"
#include "shell.h"
#include "coap_app.h"
#include "net/sock/util.h"
#include "net/cord/common.h"
#include "net/cord/ep_standalone.h"
#include "net/cord/ep.h"
#include "net/gnrc/ipv6/nib.h"
#include "net/gnrc/ipv6/nib/abr.h"
#include "net/ipv6/addr.h"

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

static int make_sock_ep(sock_udp_ep_t *ep, const char *addr)
{
    ep->port = 0;
    if (sock_udp_name2ep(ep, addr) < 0) {
        return -1;
    }
    /* if netif not specified in addr */
    if ((ep->netif == SOCK_ADDR_ANY_NETIF) && (gnrc_netif_numof() == 1)) {
        /* assign the single interface found in gnrc_netif_numof() */
        ep->netif = (uint16_t)gnrc_netif_iter(NULL)->pid;
    }
    ep->family  = AF_INET6;
    if (ep->port == 0) {
        ep->port = COAP_PORT;
    }
    return 0;
}

static void _connect_to_abr(void)
{
    gnrc_ipv6_nib_abr_t entry;
    void * state = NULL;
    char ipv6_addr[IPV6_ADDR_MAX_STR_LEN];
    char fmt_addr[IPV6_ADDR_MAX_STR_LEN + 2];

    while (gnrc_ipv6_nib_abr_iter(&state, &entry)) {
        gnrc_ipv6_nib_abr_print(&entry);
    }

    if (gnrc_ipv6_nib_abr_iter(&state, &entry)) {
        sock_udp_ep_t remote;

        ipv6_addr_to_str(ipv6_addr, (ipv6_addr_t *)&entry.addr, sizeof(ipv6_addr));
        sprintf(fmt_addr, "[%s]", ipv6_addr);
        printf("%s\n", fmt_addr);

        if (make_sock_ep(&remote, fmt_addr) < 0) {
            puts("Could not parse address.");
        }

        if (cord_ep_register(&remote, NULL) != CORD_EP_OK) {
            puts("Registration failed");
        }
        else {
            puts("registration successful\n");
            cord_ep_dump_status();
        }
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
    _connect_to_abr();

    puts("Client information:");
    printf("  ep: %s\n", cord_common_get_ep());
    printf("  lt: %is\n", (int)CONFIG_CORD_LT);

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);

    return 0;
}
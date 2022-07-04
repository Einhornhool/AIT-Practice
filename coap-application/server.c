#include "coap_app.h"
#include "net/gcoap.h"
#include "net/utils.h"
#include "saul_reg.h"
#include "saul/periph.h"
#include "od.h"

#define ENABLE_DEBUG 0
#include "debug.h"

#define GCOAP_RES_MAX 16
#define GCOAP_PATH_LEN 32

static ssize_t _saul_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx);

saul_reg_t * available_devs;
static coap_resource_t _resources[GCOAP_RES_MAX];
static char _paths[GCOAP_RES_MAX][GCOAP_PATH_LEN];

static gcoap_listener_t _listener = {
    _resources,
    ARRAY_SIZE(_resources),
    GCOAP_SOCKET_TYPE_UNDEF,
    NULL,
    NULL,
    NULL
};

static void _probe(int num, char * val, size_t * len)
{
    size_t dim;
    phydat_t res;

    saul_reg_t * dev = saul_reg_find_nth(num);
    if (dev == NULL) {
        printf("error: undefined device id given: %d", num);
        return;
    }

    dim = saul_reg_read(dev, &res);
    if (dim <= 0) {
        printf("error: failed to read from device #%i\n", num);
        return;
    }

    *len = phydat_to_json(&res, dim, val);
}

static void _write(int num, char *val, size_t len)
{
    int dim;
    phydat_t data;

    saul_reg_t * dev = saul_reg_find_nth(num);
    if (dev == NULL) {
        puts("error: undefined device id given");
        return;
    }

    for (size_t i = 0; i < len; i++) {
        data.val[i] = atoi(&val[i]);
    }

    dim = saul_reg_write(dev, &data);
    if (dim <= 0) {
        if (dim == -ENOTSUP) {
            printf("error: device #%i is not writable\n", num);
        }
        else {
            printf("error: failure to write to device #%i\n", num);
        }
        return;
    }
}

static ssize_t _saul_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx)
{
    /* read coap method type in packet */
    unsigned method_flag = coap_method2flag(coap_get_code_detail(pdu));

    switch(method_flag) {
        case COAP_GET:
            gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
            coap_opt_add_format(pdu, COAP_FORMAT_TEXT);
            size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);
            /* TODO: Read Saul LED value and write into payload buffer */
            char led_value[64] = {0};
            size_t length = 0;
            _probe((int *) ctx, led_value, &length);
            memcpy((char *)pdu->payload, led_value, length);
            resp_len += length;
            return resp_len;
        case COAP_PUT:
            if (pdu->payload_len <= 5) {
                char payload[6] = { 0 };
                memcpy(payload, (char *)pdu->payload, pdu->payload_len);
                _write((int *) ctx, payload, pdu->payload_len);
                return gcoap_response(pdu, buf, len, COAP_CODE_CHANGED);
            }
            else {
                return gcoap_response(pdu, buf, len, COAP_CODE_BAD_REQUEST);
            }
    }

    return 0;
}

static void _generate_path(char *buffer, int id, saul_reg_t *reg)
{
    printf("Resource ID: %d\n", id);
    snprintf(buffer, GCOAP_PATH_LEN, "/saul/%s/%s",
             reg->name,
             saul_class_to_str(reg->driver->type));
}

static int _compare_path(const void *a, const void *b) {
    return strcmp(((coap_resource_t*)a)->path, ((coap_resource_t*)b)->path);
}

static void _generate_resource_paths(void)
{
    int dev_count = 0;

    for (
        available_devs = saul_reg_find_nth(0);
        dev_count < GCOAP_RES_MAX && available_devs != NULL;
        available_devs = saul_reg_find_nth(++dev_count)) {
            _generate_path(_paths[dev_count], dev_count, available_devs);
            _resources[dev_count] = (coap_resource_t) {
                .path = _paths[dev_count],
                .methods = COAP_GET | COAP_PUT,
                .handler = _saul_handler,
                .context = available_devs
            };
    }
    qsort(_resources, dev_count, sizeof(coap_resource_t), _compare_path);
    _listener.resources_len = dev_count;
}

void server_init(void)
{
    _generate_resource_paths();
    gcoap_register_listener(&_listener);
}
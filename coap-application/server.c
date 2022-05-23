#include "coap_app.h"
#include "net/gcoap.h"
#include "net/utils.h"
#include "saul.h"
#include "saul/periph.h"
#include "od.h"

#define ENABLE_DEBUG 0
#include "debug.h"

// static ssize_t _encode_link(const coap_resource_t *resource, char *buf,
                            // size_t maxlen, coap_link_encoder_ctx_t *context);
static ssize_t _sensor_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx);
static ssize_t _led_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx);

/* Define available resources and callback functions */
static const coap_resource_t _resources[] = {
    { "/saul/leds", COAP_GET | COAP_PUT, _led_handler, NULL},
    { "/saul/sensors", COAP_GET, _sensor_handler, NULL }
};

// static const char *_link_params[] = {
//     ";ct=0;rt=\"count\";obs",
//     NULL
// };

static gcoap_listener_t _listener = {
    _resources,
    ARRAY_SIZE(_resources),
    GCOAP_SOCKET_TYPE_UNDEF,
    NULL,
    NULL,
    NULL
};

// static ssize_t _encode_link(const coap_resource_t *resource, char *buf,
//                             size_t maxlen, coap_link_encoder_ctx_t *context)
// {
//     ssize_t res = gcoap_encode_link(resource, buf, maxlen, context);
//     if (res > 0) {
//         if (_link_params[context->link_pos]
//                 && (strlen(_link_params[context->link_pos]) < (maxlen - res))) {
//             if (buf) {
//                 memcpy(buf+res, _link_params[context->link_pos],
//                        strlen(_link_params[context->link_pos]));
//             }
//             return res + strlen(_link_params[context->link_pos]);
//         }
//     }

//     return res;
// }

static ssize_t _sensor_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx)
{
    (void) ctx;
    gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
    coap_opt_add_format(pdu, COAP_FORMAT_TEXT);
    size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);

    /* TODO: Read Saul Sensors */
    int sensor_value = 42;
    resp_len += fmt_u16_dec((char *)pdu->payload, sensor_value);
    return resp_len;
}

static ssize_t _led_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx)
{
    (void)ctx;

    /* read coap method type in packet */
    unsigned method_flag = coap_method2flag(coap_get_code_detail(pdu));

    switch(method_flag) {
        case COAP_GET:
            gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
            coap_opt_add_format(pdu, COAP_FORMAT_TEXT);
            size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);
            /* TODO: Read Saul LED value and write into payload buffer */
            int led_value = 0;
            resp_len += fmt_u16_dec((char *)pdu->payload, led_value);
            return resp_len;
        case COAP_PUT:
            if (pdu->payload_len <= 5) {
                char payload[6] = { 0 };
                memcpy(payload, (char *)pdu->payload, pdu->payload_len);
                uint16_t value = (uint16_t)strtoul(payload, NULL, 10);
                /* TODO: Set Saul LED to new value */
                return gcoap_response(pdu, buf, len, COAP_CODE_CHANGED);
            }
            else {
                return gcoap_response(pdu, buf, len, COAP_CODE_BAD_REQUEST);
            }
    }
}


void server_init(void)
{
    gcoap_register_listener(&_listener);
}
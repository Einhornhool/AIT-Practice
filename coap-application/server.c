#include "coap_app.h"
#include "net/gcoap.h"
#include "net/utils.h"
#include "saul_reg.h"
#include "saul/periph.h"
#include "od.h"

#define ENABLE_DEBUG 0
#include "debug.h"

// #0	ACT_SWITCH      LED(red)
// #1	ACT_SWITCH      LED(green)
// #2	ACT_SWITCH      LED(blue)
// #3	SENSE_BTN       Button(SW0)
// #4	SENSE_BTN       Button(CS0)
// #5	SENSE_TEMP      hdc1000
// #6	SENSE_HUM       hdc1000
// #7	SENSE_MAG       mag3110
// #8	SENSE_ACCE      mma8x5x
// #9	SENSE_TEMP      mpl3115a2
// #10	SENSE_PRES      mpl3115a2
// #11	SENSE_COLO      tcs37727
// #12	SENSE_OBJTEMP	tmp00x

#define LED_RED     0
#define LED_GREEN   1
#define LED_BLUE    2

#define BTN_0       3
#define BTN_1       4

#define SENS_TEMP_HDC   5
#define SENS_HUM        6
#define SENS_MAG        7
#define SENS_ACCE       8
#define SENS_TEMP_MPL   9
#define SENS_PRES       10
#define SENS_COLO       11
#define SENS_OBJTEMP    12

int devs[] = {  LED_RED,
                LED_GREEN,
                LED_BLUE,
                BTN_0,
                BTN_1,
                SENS_TEMP_HDC,
                SENS_HUM,
                SENS_MAG,
                SENS_ACCE,
                SENS_TEMP_MPL,
                SENS_PRES,
                SENS_COLO,
                SENS_OBJTEMP
            };

static ssize_t _sensor_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx);
static ssize_t _led_btn_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx);

/* Define available resources and callback functions */
static const coap_resource_t _resources[] = {
    { "/btn/0", COAP_GET | COAP_PUT, _led_btn_handler, &devs[BTN_0] },
    { "/btn/1", COAP_GET | COAP_PUT, _led_btn_handler, &devs[BTN_1] },
    { "/led/blue", COAP_GET | COAP_PUT, _led_btn_handler, &devs[LED_BLUE] },
    { "/led/green", COAP_GET | COAP_PUT, _led_btn_handler, &devs[LED_GREEN]},
    { "/led/red", COAP_GET | COAP_PUT, _led_btn_handler, &devs[LED_RED]},
    { "/sensor/acce", COAP_GET, _sensor_handler, &devs[SENS_ACCE] },
    { "/sensor/colo", COAP_GET, _sensor_handler, &devs[SENS_COLO] },
    { "/sensor/hum", COAP_GET, _sensor_handler, &devs[SENS_HUM] },
    { "/sensor/mag", COAP_GET, _sensor_handler, &devs[SENS_MAG] },
    { "/sensor/objtemp", COAP_GET, _sensor_handler, &devs[SENS_OBJTEMP] },
    { "/sensor/pres", COAP_GET, _sensor_handler, &devs[SENS_PRES] },
    { "/sensor/temp/hdc", COAP_GET, _sensor_handler, &devs[SENS_TEMP_HDC] },
    { "/sensor/temp/mpl", COAP_GET, _sensor_handler, &devs[SENS_TEMP_MPL] },
};

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
        puts("error: undefined device id given");
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

static ssize_t _sensor_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx)
{
    char sensor_value[64];
    size_t length = 0;
    _probe((*(int *) ctx), sensor_value, &length);

    gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
    coap_opt_add_format(pdu, COAP_FORMAT_TEXT);
    size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);

    memcpy((char *)pdu->payload, sensor_value, length);
    resp_len += length;
    return resp_len;
}

static ssize_t _led_btn_handler(coap_pkt_t * pdu, uint8_t * buf, size_t len, void * ctx)
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
            size_t length;
            _probe((*(int *) ctx), led_value, &length);
            memcpy((char *)pdu->payload, led_value, length);
            resp_len += length;
            return resp_len;
        case COAP_PUT:
            if (pdu->payload_len <= 5) {
                char payload[6] = { 0 };
                memcpy(payload, (char *)pdu->payload, pdu->payload_len);
                _write(*((int *) ctx), payload, pdu->payload_len);
                return gcoap_response(pdu, buf, len, COAP_CODE_CHANGED);
            }
            else {
                return gcoap_response(pdu, buf, len, COAP_CODE_BAD_REQUEST);
            }
    }

    return 0;
}


void server_init(void)
{
    gcoap_register_listener(&_listener);
}
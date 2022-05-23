#ifndef COAP_APP_H
#define COAP_APP_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fmt.h"
#include "net/gcoap.h"
#include "net/utils.h"


// /**
//  * @brief   Shell interface exposing the client side features of gcoap
//  * @param   argc    Number of shell arguments (including shell command name)
//  * @param   argv    Shell argument values (including shell command name)
//  * @return  Exit status of the shell command
//  */
// int coap_saul_cli_cmd(int argc, char **argv);

/**
 * @brief   Registers the CoAP resources exposed in the example app
 *
 * Run this exactly one during startup.
 */
void server_init(void);

#endif
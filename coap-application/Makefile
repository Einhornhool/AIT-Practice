APPLICATION = ait-coap
BOARD = pba-d-01-kw2x

RIOTBASE = $(CURDIR)/../RIOT

CFLAGS += -DCONFIG_IEEE802154_DEFAULT_CHANNEL=26
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_SLAAC=1

USEMODULE += gcoap
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6_default
USEMODULE += gnrc_icmpv6_echo

USEMODULE += saul_default

USEMODULE += shell
USEMODULE += shell_commands
USEMODULE += ps

DEVELHELP ?= 1

include $(RIOTBASE)/Makefile.include
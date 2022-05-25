APPLICATION = ait-coap
BOARD = pba-d-01-kw2x

RIOTBASE = $(CURDIR)/../RIOT

CFLAGS += -DCONFIG_IEEE802154_DEFAULT_CHANNEL=26
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_SLAAC=1
CFLAGS += -DCONFIG_GCOAP_PDU_BUF_SIZE=512

# Include packages that pull up and auto-init the link layer.
# NOTE: 6LoWPAN will be included if IEEE802.15.4 devices are present
USEMODULE += netdev_default

USEMODULE += gcoap
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6_default
USEMODULE += gnrc_icmpv6_echo

USEMODULE += saul_default

USEMODULE += shell
USEMODULE += shell_commands
USEMODULE += fmt
USEMODULE += netutils
USEMODULE += ps

DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1


include $(RIOTBASE)/Makefile.include
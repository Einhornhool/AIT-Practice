APPLICATION = ait-coap
BOARD = pba-d-01-kw2x

RIOTBASE = $(CURDIR)/../RIOT

# Default to using ethos for providing the uplink when not on native
UPLINK ?= ethos

CFLAGS += -DCONFIG_IEEE802154_DEFAULT_CHANNEL=26
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_SLAAC=1
CFLAGS += -DCONFIG_GCOAP_PDU_BUF_SIZE=512

# Include packages that pull up and auto-init the link layer.
# NOTE: 6LoWPAN will be included if IEEE802.15.4 devices are present
USEMODULE += netdev_default

USEMODULE += gcoap
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6_default
USEMODULE += gnrc_sixlowpan_border_router_default
USEMODULE += gnrc_icmpv6_echo
USEMODULE += cord_ep_standalone

# include UHCP client
USEMODULE += gnrc_uhcpc
USEMODULE += gnrc_sixlowpan_border_router_default

USEMODULE += saul_default

USEMODULE += shell
USEMODULE += shell_commands
USEMODULE += fmt
USEMODULE += netutils
USEMODULE += ps

DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1

TAP ?= tap0
# IPV6_PREFIX ?= 2001:db8::/64
IPV6_PREFIX ?= 2001:67c:254:b0b2:affe:4000:0:1/84

ETHOS_BAUDRATE ?= 115200
include $(CURDIR)/Makefile.ethos.conf

include $(RIOTBASE)/Makefile.include

# For debugging and demonstration purposes, we limit the lifetime to 60s
# Set CONFIG_CORD_LT only if not being set via Kconfig
ifndef CONFIG_CORD_LT
CFLAGS += -DCONFIG_CORD_LT=60
endif

.PHONY: host-tools

host-tools:
	$(Q)env -u CC -u CFLAGS $(MAKE) -C $(RIOTTOOLS)

# define native specific targets to only run UHCP daemon when required
ifneq (,$(filter native,$(BOARD)))
ifneq (1,$(USE_DHCPV6))
.PHONY: uhcpd-daemon

uhcpd-daemon: host-tools
	$(RIOTTOOLS)/uhcpd/bin/uhcpd $(TAP) $(IPV6_PREFIX) &
endif
endif
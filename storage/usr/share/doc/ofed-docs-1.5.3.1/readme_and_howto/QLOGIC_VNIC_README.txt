This is a release of the QLogic VNIC driver on OFED 1.4.  This driver is 
currently supported on Intel x86 32 and 64 bit machines. 
Supported OS are: 
-  RHEL 4 Update 4.
-  RHEL 4 Update 5.
-  RHEL 4 Update 6.
-  SLES 10.
-  SLES 10 Service Pack 1.
-  SLES 10 Service Pack 1 Update 1.
-  SLES 10 Service Pack 2.
-  RHEL 5.
-  RHEL 5 Update 1.
-  RHEL 5 Update 2.
-  vanilla 2.6.27 kernel.

The VNIC driver in conjunction with the QLogic Ethernet Virtual I/O Controller
(EVIC) provides Ethernet interfaces on a host with IB HCA(s) without the need
for any physical Ethernet NIC.

This file describes the use of the QLogic VNIC ULP service on an OFED stack
and covers the following points:

A) Creating QLogic VNIC interfaces
B) Discovering VEx/EVIC IOCs present on the fabric using ib_qlgc_vnic_query
C) Starting the QLogic VNIC driver and the VNIC interfaces
D) Assigning IP addresses etc for the QLogic VNIC interfaces
E) Information about the QLogic VNIC interfaces
F) Deleting a specific QLogic VNIC interface
G) Forced Failover feature for QLogic VNIC.
H) Infiniband Quality of Service for VNIC.
I) QLogic VNIC Dynamic Update Daemon Tool and Hot Swap support
J) Information about creating VLAN interfaces
K) Information about enabling IB Multicast for QLogic VNIC interface
L) Basic Troubleshooting

A) Creating QLogic VNIC interfaces

The VNIC interfaces can be created with the help of
the configuration file which must be placed at /etc/infiniband/qlgc_vnic.cfg.

Please take a look at /etc/infiniband/qlgc_vnic.cfg.sample file (available also
as part of the documentation) to see how VNIC configuration files are written.
You can use this configuration file as the basis for creating a VNIC configuration
file by copying it to /etc/infiniband/qlgc_vnic.cfg. Of course you will have to
replace the IOCGUID, IOCSTRING values etc in the sample configuration file
with those of the EVIC IOCs present on your fabric.

(For backward compatibilty, if this file is missing, 
/etc/infiniband/qlogic_vnic.cfg or /etc/sysconfig/ics_inic.cfg
will be used for configuration)

Please note that using DGID of the EVIC/VEx IOC is
recommended as it will ensure the quickest startup of the
VNIC service. If DGID is specified then you must also
specify the IOCGUID. More details can be found in
the qlgc_vnic.cfg.sample file.

In case of a host consisting of more than 1 HCAs plugged in, VNIC
interfaces can be configured based on HCA no and Port No or PORTGUID.

B) Discovering EVIC/VEx IOCs present on the fabric using ib_qlgc_vnic_query

For writing the configuration file, you will need information
about the EVIC/VEx IOCs present on the fabric like their IOCGUID,
IOCSTRING etc. The ib_qlgc_vnic_query tool should be used to get this
information. 

When ib_qlgc_vnic_query is executed without any options, it scans through ALL
active IB ports on the host and obtains the detailed information about all the
EVIC/VEx IOCs reachable through each active IB port:

# ib_qlgc_vnic_query

HCA No = 0, HCA = mlx4_0, Port = 1, Port GUID = 0x0002c903000010f5, State = Active

        IO Unit Info:
            port LID:        0008
            port GID:        fe8000000000000000066a11de000070
            change ID:       0003
            max controllers: 0x02


            controller[  1]
                GUID:      00066a01de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1
                service entries: 2
                    service[  0]: 1000066a00000001 / InfiniNIC.InfiniConSys.Control:01
                    service[  1]: 1000066a00000101 / InfiniNIC.InfiniConSys.Data:01

        IO Unit Info:
            port LID:        0009
            port GID:        fe8000000000000000066a21de000070
            change ID:       0003
            max controllers: 0x02


            controller[  2]
                GUID:      00066a02de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2
                service entries: 2
                    service[  0]: 1000066a00000002 / InfiniNIC.InfiniConSys.Control:02
                    service[  1]: 1000066a00000102 / InfiniNIC.InfiniConSys.Data:02

HCA No = 0, HCA = mlx4_0, Port = 2, Port GUID = 0x0002c903000010f6, State = Active

        IO Unit Info:
            port LID:        0008
            port GID:        fe8000000000000000066a11de000070
            change ID:       0003
            max controllers: 0x02


            controller[  1]
                GUID:      00066a01de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1
                service entries: 2
                    service[  0]: 1000066a00000001 / InfiniNIC.InfiniConSys.Control:01
                    service[  1]: 1000066a00000101 / InfiniNIC.InfiniConSys.Data:01

        IO Unit Info:
            port LID:        0009
            port GID:        fe8000000000000000066a21de000070
            change ID:       0003
            max controllers: 0x02


            controller[  2]
                GUID:      00066a02de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2
                service entries: 2
                    service[  0]: 1000066a00000002 / InfiniNIC.InfiniConSys.Control:02
                    service[  1]: 1000066a00000102 / InfiniNIC.InfiniConSys.Data:02

HCA No = 1, HCA = mlx4_1, Port = 1, Port GUID = 0x0002c90300000785, State = Down

        Port State is Down. Skipping search of DM nodes on this port.

HCA No = 1, HCA = mlx4_1, Port = 2, Port GUID = 0x0002c90300000786, State = Active

        IO Unit Info:
            port LID:        0008
            port GID:        fe8000000000000000066a11de000070
            change ID:       0003
            max controllers: 0x02


            controller[  1]
                GUID:      00066a01de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1
                service entries: 2
                    service[  0]: 1000066a00000001 / InfiniNIC.InfiniConSys.Control:01
                    service[  1]: 1000066a00000101 / InfiniNIC.InfiniConSys.Data:01

        IO Unit Info:
            port LID:        0009
            port GID:        fe8000000000000000066a21de000070
            change ID:       0003
            max controllers: 0x02


            controller[  2]
                GUID:      00066a02de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2
                service entries: 2
                    service[  0]: 1000066a00000002 / InfiniNIC.InfiniConSys.Control:02
                    service[  1]: 1000066a00000102 / InfiniNIC.InfiniConSys.Data:02

This is meant to help the network administrator to know about HCA/Port information 
on host along with EVIC IOCs reachable through given IB ports on fabric.  When 
ib_qlgc_vnic_query is run with -e option, it reports the IOCGUID information 
and with -s option it reports the IOCSTRING information for the EVIC/VEx IOCs
present on the fabric:

# ib_qlgc_vnic_query -e

HCA No = 0, HCA = mlx4_0, Port = 1, Port GUID = 0x0002c903000010f5, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff
HCA No = 0, HCA = mlx4_0, Port = 2, Port GUID = 0x0002c903000010f6, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff
HCA No = 1, HCA = mlx4_1, Port = 1, Port GUID = 0x0002c90300000785, State = Down

        Port State is Down. Skipping search of DM nodes on this port.

HCA No = 1, HCA = mlx4_1, Port = 2, Port GUID = 0x0002c90300000786, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff

# ib_qlgc_vnic_query -s

HCA No = 0, HCA = mlx4_0, Port = 1, Port GUID = 0x0002c903000010f5, State = Active

"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"
HCA No = 0, HCA = mlx4_0, Port = 2, Port GUID = 0x0002c903000010f6, State = Active

"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"
HCA No = 1, HCA = mlx4_1, Port = 1, Port GUID = 0x0002c90300000785, State = Down

        Port State is Down. Skipping search of DM nodes on this port.

HCA No = 1, HCA = mlx4_1, Port = 2, Port GUID = 0x0002c90300000786, State = Active

"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"

# ib_qlgc_vnic_query -es

HCA No = 0, HCA = mlx4_0, Port = 1, Port GUID = 0x0002c903000010f5, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"
HCA No = 0, HCA = mlx4_0, Port = 2, Port GUID = 0x0002c903000010f6, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"
HCA No = 1, HCA = mlx4_1, Port = 1, Port GUID = 0x0002c90300000785, State = Down

        Port State is Down. Skipping search of DM nodes on this port.

HCA No = 1, HCA = mlx4_1, Port = 2, Port GUID = 0x0002c90300000786, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"

ib_qlgc_vnic_query can be used to discover EVIC IOCs on the fabric based on 
umad device, HCA no/Port no and PORTGUID as follows:

For umad devices, it takes the name of the umad device mentioned with '-d'
option:

# ib_qlgc_vnic_query -es -d /dev/infiniband/umad0

HCA No = 0, HCA = mlx4_0, Port = 1

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"

If the name of the HCA and its port no is known, then ib_qlgc_vnic_query can
make use of this information to discover EVIC IOCs on the fabric.  HCA name 
and port no is specified with '-C' and '-P' options respectively.

# ib_qlgc_vnic_query -es -C mlx4_1 -P 2

	ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
	ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"

In case, if HCA name is not specified but port no is specified, HCA 0 is 
selected as default HCA to discover IOCs and if Port no is missing then,
Port 1 of HCA name mentioned is used to discover the IOCs.  If both are
missing, the behaviour is default and ib_qlgc_vnic_query will scan all the
IB ports on the host to discover IOCs reachable through each one of them.

PORTGUID information about the IB ports on given host can be obtained using
the option '-L':

# ib_qlgc_vnic_query -L

0,mlx4_0,1,0x0002c903000010f5
0,mlx4_0,2,0x0002c903000010f6
1,mlx4_1,1,0x0002c90300000785
1,mlx4_1,2,0x0002c90300000786

This actually lists different configurable parameters of IB ports present on
given host in the order: HCA No, HCA Name, Port No, PORTGUID separated by
commas. PORTGUID value obtained thus, can be used to discover EVIC IOCs
reachable through it using '-G' option as follows:

# ib_qlgc_vnic_query -es -G 0x0002c903000010f5

HCA No = 0, HCA = mlx4_0, Port = 1, Port GUID = 0x0002c903000010f5, State = Active

        ioc_guid=00066a01de000070,dgid=fe8000000000000000066a11de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1"
        ioc_guid=00066a02de000070,dgid=fe8000000000000000066a21de000070,pkey=ffff,"EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2"

C) Starting the QLogic VNIC driver and the QLogic VNIC interfaces

To start the QLogic VNIC service as a part of startup of OFED stack, set

QLGC_VNIC_LOAD=yes

in /etc/infiniband/openib.conf file. With this actually, the QLogic VNIC
service will also be stopped when the OFED stack is stopped.  Also, if OFED
stack has been marked to start on boot, QLogic VNIC service will also start
on boot.

The rest of the discussion in this subsection C) is valid only if

QLGC_VNIC_LOAD=no

is set into /etc/infiniband/openib.conf.

Once you have created a configuration file, you can start the VNIC driver
and create the VNIC interfaces specified in the configuration file with:

#/sbin/service qlgc_vnic start

You can stop the VNIC driver and bring down the VNIC interfaces with

#/sbin/service qlgc_vnic stop

To restart the QLogic VNIC driver, you can use

#/sbin/service qlgc_vnic restart

If you have not started the Infiniband network stack (Infinipath or OFED),
then running "/sbin/service qlgc_vnic start" command will also cause the
Infiniband network stack to be started since the QLogic VNIC service requires
the Infiniband stack.

On the other hand if you start the Infiniband network stack separately, then
the correct order of starting is:

-  Start the Infiniband stack
-  Start QLogic VNIC service

For example, if you use OFED, correct order of starting is:

/sbin/service openibd start
/sbin/service qlgc_vnic start

Correct order of stopping is:

- Stop QLogic VNIC service
- Stop the Infiniband stack

For example, if you use OFED, correct order of stopping is:

/sbin/service qlgc_vnic stop
/sbin/service openibd stop

If you try to stop the Infiniband stack when the QLogic VNIC service is
running,
you will get an error message that some of the modules of the Infiniband stack
are in use by the QLogic VNIC service. Also, any QLogic VNIC interfaces that
you
created are removed (because stopping the Infiniband network stack causes the
HCA
driver to be unloaded which is required for the VNIC interfaces to be
present).
In this case, do the following:

  1. Stop the QLogic VNIC service with "/sbin/service qlgc_vnic stop"

  2. Stop the Infiniband stack again.

  3. If you want to restart the QLogic VNIC interfaces, use
    "/sbin/service qlgc_vnic start".


D) Assigning IP addresses etc for the QLogic VNIC interfaces

This can be done with ifconfig or by setting up the ifcfg-XXX (ifcfg-veth0 for
an interface named veth0 etc) network files for the corresponding VNIC interfaces.

E) Information about the QLogic VNIC interfaces

Information about VNIC interfaces on a given host can be obtained using a 
script "ib_qlgc_vnic_info" :-

# ib_qlgc_vnic_info

VNIC Interface : eioc0
    VNIC State        : VNIC_REGISTERED
    Current Path      : primary path
    Receive Checksum  : true
    Transmit checksum : true
 
    Primary Path : 
        VIPORT State  : VIPORT_CONNECTED
        Link State    : LINK_IDLING
        HCA Info.     : vnic-mthca0-1
        Heartbeat     : 100
        IOC String    : EVIC in Chassis 0x00066a00db000010, Slot 4, Ioc 1
        IOC GUID      : 66a01de000037
        DGID          : fe8000000000000000066a11de000037
        P Key         : ffff
 
    Secondary Path : 
        VIPORT State  : VIPORT_DISCONNECTED
        Link State    : INVALID STATE
        HCA Info.     : vnic-mthca0-2
        Heartbeat     : 100
        IOC String    : 
        IOC GUID      : 66a01de000037
        DGID          : 00000000000000000000000000000000
        P Key         : 0

This information is collected from /sys/class/infiniband_qlgc_vnic/interfaces/
directory under which there is a separate directory corresponding to each
VNIC interface.

F) Deleting a specific QLogic VNIC interface

VNIC interfaces can be deleted by writing the name of the interface to 
the /sys/class/infiniband_qlgc_vnic/interfaces/delete_vnic file.

For example to delete interface veth0

echo -n veth0 > /sys/class/infiniband_qlgc_vnic/interfaces/delete_vnic

G) Forced Failover feature for QLogic VNIC.

VNIC interfaces, when configured with failover configuration, can be 
forced to failover to use other active path.  For example, if VNIC interface
"veth1" is configured with failover configuration, then to switch to other
path, use command:

echo -n veth1 > /sys/class/infiniband_qlgc_vnic/interfaces/force_failover

This will make VNIC interface veth1 to switch to other active path, even though
the path of VNIC interface, before the forced failover operation, is not in
disconnected state.

This feature allows the network administrator to control the path of the
VNIC traffic at run time and reconfiguration as well as restart of VNIC 
service is not required to achieve the same.

Once enabled as mentioned above, forced failover can be cleared with
the unfailover command:

echo -n veth1 > /sys/class/infiniband_qlgc_vnic/interfaces/unfailover

This clears the forced failover on VNIC interface "veth1".  Once cleared,
if module parameter "default_prefer_primary" is set to 1, then VNIC 
interface switches back to primary path.  If module parameter 
"default_prefer_primary" is set to 0, then VNIC interface continues to
use its current active path.

Forced failover, thus, takes priority over default_prefer_primary and the
default_prefer_primary feature will not be active unless the forced
failover is cleared through "unfailover".

Besides this forced failover, QLogic VNIC service does retain its 
original failover feature which gets triggered when current active
path gets disconnected.

H) Infiniband Quality of Service for VNIC:-

To enforce infiniband Quality of Service(QoS) for VNIC protocol, there
is no configuration required on host side.  The service level for the
VNIC protocol can be configured using service ID or target port guid
in the "qos-ulps" section of /etc/opensm/qos-policy.conf on the host
running OpenSM.

Service IDs for the EVIC IO controllers can be obtained from the output
of ib_qlgc_vnic_query:  

HCA No = 1, HCA = mlx4_1, Port = 2, Port GUID = 0x0002c90300000786, State = Active

        IO Unit Info:
            port LID:        0008
            port GID:        fe8000000000000000066a11de000070
            change ID:       0003
            max controllers: 0x02


            controller[  1]
                GUID:      00066a01de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 1
                service entries: 2
------>             service[  0]: 1000066a00000001 / InfiniNIC.InfiniConSys.Control:01
------>             service[  1]: 1000066a00000101 / InfiniNIC.InfiniConSys.Data:01

        IO Unit Info:
            port LID:        0009
            port GID:        fe8000000000000000066a21de000070
            change ID:       0003
            max controllers: 0x02


            controller[  2]
                GUID:      00066a02de000070
                vendor ID: 00066a
                device ID: 000030
                IO class : 2000
                ID:        EVIC in Chassis 0x00066a00db00001e, Slot 1, Ioc 2
                service entries: 2
------>             service[  0]: 1000066a00000002 / InfiniNIC.InfiniConSys.Control:02
------>             service[  1]: 1000066a00000102 / InfiniNIC.InfiniConSys.Data:02

Numbers 1000066a00000002, 1000066a00000102 are the required service IDs.

Finer control on quality of service for the VNIC protocol can be achieved by
configuring the service level using target port guid values of the EVIC IO
controllers.  Target port guid values for the EVIC IO controllers can be
obtained using "saquery" command supplied by OFED package.

I) QLogic VNIC Dynamic Update Daemon Tool and Hot Swap support:-

This tool is started and stopped as part of the QLogic VNIC service 
(refer to C above) and provides the following features:

1. Dynamic update of disconnected interfaces (which have been configured
WITHOUT using the DGID option in the configuration file) : 

At the start up of VNIC driver, if the HCA port through which a particular VNIC
interface path (primary or secondary) connects to target is down or the 
EVIC/VEx IOC is not available then all the required parameters (DGID etc) for connecting
with the EVIC/VEx cannot be determined. Hence the corresponding VNIC interface
path is not available at the start of the VNIC service. This daemon constantly
monitors the configured VNIC interfaces to check if any of them are disconnected.
If any of the interfaces are disconnected, it scans for available EVIC/VEx targets using
"ib_qlgc_vnic_query" tool. When daemon sees that for a given path of a VNIC interface, 
the configured EVIC/VEx IOC has become available, it dynamically updates the 
VNIC kernel driver with the required information to establish connection for 
that path of the interface. In this way, the interface gets connected with
the configured EVIC/VEx whenever it becomes available without any manual 
intervention.

2. Hot Swap support :

Hot swap is an operation in which an existing EVIC/VEx is replaced by another
EVIC/VEx (in the same slot of the switch chassis as the older one). In such a 
case, the current connection for the corresponding VNIC interface will have to
be re-established. The daemon detects this hot swap case and re-establishes
the connection automatically. To make use of this feature of the daemon, it is
recommended that IOCSTRING be used in the configuration file to configure the
VNIC interfaces.

This is because, after a hot swap though all other parameters like DGID, IOCGUID etc
of the EVIC/VEx change, the IOCSTRING remains the same. Thus the daemon monitors
for changes in IOCGUID and DGID of disconnected interfaces based on the IOCSTRING.
If these values have changed it updates the kernel driver so that the VNIC
interface can start using the new EVIC/VEx.

If in addition to IOCSTRING, DGID and IOCGUID have been used to configure
a VNIC interface, then on a hotswap the daemon will update the parameters as required.
But to have that VNIC interface available immediately on the next restart of the
QLogic VNIC service, please make sure to update the configuration file with the
new DGID and IOCGUID values. Otherwise, the creation of such interfaces will be
delayed till the daemon runs and updates the parameters.

J) Information about creating VLAN interfaces

The EVIC/VEx supports VLAN tagging without having to explicitly create VLAN
interfaces for the VNIC interface on the host. This is done by enabling
Egress/Ingress tagging on the EVIC/VEx and setting the "Host ignores VLAN"
option for the VNIC interface. The "Host ignores VLAN" option is enabled
by default due to which VLAN tags are ignored on the host by the QLogic
VNIC driver. Thus explicitly created VLAN interfaces (using vconfig command)
for a given VNIC interface will not be operational.

If you want to explicitly create a VLAN interface for a given VNIC interface,
then you will have to disable the "Host ignores VLAN" option for the
VNIC interface on the EVIC/VEx. The qlgc_vnic service must be restarted
on the host after disabling (or enabling) the "Host ignores VLAN" option.

Please refer to the EVIC/VEx documentation for more information on Egress/Ingress
port tagging feature and disabling the "Host ignores VLAN" option.

K) Information about enabling IB Multicast for QLogic VNIC interface

QLogic VNIC driver has been upgraded to support the IB Multicasting feature of 
EVIC/VEx. This feature enables the QLogic VNIC host driver to support the IP 
multicasting more efficiently. With this feature enabled, infiniband multicast 
group acts as a carrier of IP multicast traffic. EVIC will make use of such IB 
multicast groups for forwarding IP multicast traffic to VNIC interfaces which 
are member of given IP multicast group. In the older QLogic VNIC host driver, 
IB multicasting was not being used to carry IP multicast traffic.

By default, IB multicasting is disabled on EVIC/VEx; but it is enabled by
default at the QLogic VNIC host driver.

To disable IB multicast feature on the host driver, VNIC configuration file
needs to be modified by setting the parameter IB_MULTICAST=FALSE in the 
interface configuration. Please refer to the qlgc_vnic.cfg.sample for more 
details on configuration of VNIC interfaces for IB multicasting. 
IB multicasting also needs to be enabled over EVIC/VEx. Please refer to the 
EVIC/VEx documentation for more information on enabling IB multicast 
feature over EVIC/VEx.

L) Basic Troubleshooting

1. In case of any problems, make sure that:

   a) The HCA ports you are trying to use have IB cables connected and are in an
      active state. You can use the "ibv_devinfo" tool to check the state of
      your HCA ports.

   b) If your HCA ports are not active, check if an SM is running on the fabric
      where the HCA ports are connected. If you have done a full install of
      OFED, you can use the "sminfo" command ("sminfo -P 2" for port 2) to
      check SM information.

   c) Make sure that the EVIC/VEx is powered up and its Ethernet cables are connected
      properly.

   d) Check /var/log/messages for any error messages.

2. If some of your VNIC interfaces are not available:

   a) Use "ifconfig" tool  with -a option to see if all interfaces are created.
      It is possible that the interfaces are created but do not have an
      IP address. Make sure that you have setup a correct ifcfg-XXX file for your
      VNIC interfaces for automatic assignment of IP addresses.

      If the VNIC interface is created and the ifcfg file is also correct
      but the VNIC interface is not UP, make sure that the target EVIC/VEx
      IOC has an Ethernet cable properly connected.

   b) Make sure that the VNIC configuration file has been setup properly
      with correct EVIC/VEx target DGID/IOCGUID/IOCSTRING information and 
      instance numbers.

   c) Make sure that the EVIC/VEx target IOC specified for that interface is
      available. You can use the "ib_qlgc_vnic_query" tool to verify this. If it is not
      available when you started  the service, but it becomes available later
      on, then the QLogic VNIC dynamic update daemon  will  bring up the
      interface when the target becomes available. You will see messages in
      /var/log/messages when the corresponding interface is created.

   d) Make sure that you have not exceeded the total number of Virtual interfaces
      supported by the EVIC/VEx. You can check the total number of Virtual interfaces
      currently in use on the HTTP interface of the EVIC/VEx.


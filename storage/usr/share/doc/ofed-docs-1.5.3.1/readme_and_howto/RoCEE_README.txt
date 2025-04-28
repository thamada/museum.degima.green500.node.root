===============================================================================
                       OFED-1.5.3 RoCEE Support README
			        March 2011
===============================================================================

Contents:
=========
1. Overview
2. Software Dependencies
3. User Guidelines
4. Ported Applications
5. Gid tables
6. Using VLANs
7. Statistic counters
8. Firmware Requirements
9. Supported hardware
10. Added fearues
11. Known Issues


1. Overview
===========
RDMA over Converged Enhanced Ethernet (RoCEE) allows InfiniBand (IB) transport
over Ethernet networks. It encapsulates IB transport and GRH headers in
Ethernet packets bearing a dedicated ether type.
While the use of GRH is optional within IB subnets, it is mandatory when using
RoCEE. Verbs applications written over IB verbs should work seamlessly, but
they require provisioning of GRH information when creating address vectors. The
library and driver are modified to provide for mapping from GID to MAC
addresses required by the hardware.

2. Software Dependencies
========================
In order to use RoCEE over Mellanox ConnectX(R) hardware, the mlx4_en driver
must be loaded. Please refer to MLNX_EN_README.txt for further details.


3. User Guidelines
==================
Since RoCEE encapsulates InfiniBand traffic in Ethernet frames, the
corresponding net device must be up and running. In case of Mellanox
hardware, mlx4_en must be loaded and the corresponding interface configured.
- Make sure mlx4_en.ko is loaded
- Make sure an IP address has been configured to this interface
- Run "ibv_devinfo". There is a new field named "link_layer" which can be
  either "Ethernet" or "IB". If the value is IB, then you need to use
  connectx_port_config to change the ConnectX ports designation to eth (see
  mlx4_release_notes.txt for details)
- Configure the IP address of the interface so that the link will become
  active
- All IB verbs applications which run over IB verbs should work on RoCEE
  links as long as they use GRH headers (that is, as long as they specify use
  of GRH in their address vector)
- rdma_cm applications working over RoCEE will have the TOS field set to a
  default value of 3. The default value is given as a module paramter to
  rdma_cm:
   def_prec2sl:Default value for SL priority with RoCE. Valid values 0 - 7 (int).


4. Ported Applications
======================
- ibv_*_pingpong examples have been ported too. The user must specify the GID
  of the remote peer using the new '-g' option. The GID has the same format as
  that in /sys/class/infiniband/mlx4_0/ports/1/gids/0

- Note: Care should be taken when using ibv_ud_pingpong. The default message
  size is 2K, which is likely to exceed the MTU of the RoCEE link. Use 
  ibv_devinfo to inspect the link MTU and specify an appropriate message size

- All rdma_cm applications should work seamlessly without any change

- libsdp works without any change

- Performance tests have been ported


5. Gid tables
=============
With RoCEE, there may be several entries in a port's GID table. The first entry
always contains the IPv6 link local address of the corresponding ethernet
interface. The link local address is formed in the following way:

gid[0..7] = fe80000000000000
gid[8] = mac[0] ^ 2
gid[9] = mac[1]
gid[10] = mac[2]
gid[11] = ff
gid[12] = fe
gid[13] = mac[3]
gid[14] = mac[4]
gid[15] = mac[5]

If VLAN is supported by the kernel, and there are VLAN interfaces on the main
ethernet interface (the interface that the IB port is tied to), each such VLAN
will appear as a new GID in the port's GID table. The format of the GID entry
will be identical to the one decribed above with the following change:

gid[11] = VLAN ID high byte (4 MS bits).
gid[12] = VLAN ID low byte

Please note that VLAN ID is 12 bits.

Priority pause frames
---------------------
Tagged ethernet frames carry a 3 bit priority field. The value of this field is
derived from the IB SL field by taking the 3 LS bits of the SL field.


6. Using VLANs
==============
In order for RoCEE traffic to used VLAN tagged frames, the user has to specify
GID table entries that are derived from VLAN devices, when creating address
vectors. Consider the example bellow:

6.1 Make sure VLAN support is enabled by the kernel. Usually this requires
loading the 8021q module.
- modprobe 8021q

6.2 Add a VLAN device
- vconfig add eth2 7

6.3 Assign IP address to the VLAN interface
- ifconfig eth2.7 7.10.11.12
suppose this created a new entry in the GID table in index 1.

6.4 verbs test:
server: ibv_rc_pingpong -g 1 
client: ibv_rc_pingpongs -g 1 server

6.5 For rdma_cm applications, the user only needs to specify an IP address of a
VLAN device for the traffic to go with that VLAN tagged frames.

7. Statistic counters
=====================
RoCEE traffic is counted and can be read from the sysfs counters in the same
manner as it is done for regular Infiniband devices. Only the following
counters are supported:
- port_xmit_packets
- port_rcv_packets
- port_rcv_data
- port_xmit_data

For example, to read the number of transmitted packets on port 2 of device
mlx4_1, one needs to read the file:
/sys/class/infiniband/mlx4_1/ports/2/counters/port_xmit_packets

Note: RoCEE traffic will not show in the associated Etherent device's counters
since it is offloaded by the hardware and does not go through Ethernet network
driver.


8. Firmware Requirements
========================
RoCEE has limited support with firmware 2.7.700 and is fully supported
with firmware 2.8.000 and above.


9. Supported hardware
=====================
Currently, ConnectX B0 hardware is supported. A0 hardware may have issues.


10. Added fearues
=================
ibdev2netdev is a utility that displays the association between an HCA's port
and the network interface bound to it. Example run:

# ibdev2netdev 
mlx4_0 port 1 ==> ib0 (Down)
mlx4_0 port 2 ==> ib1 (Down)
mlx4_1 port 1 ==> eth2 (Up)
mlx4_1 port 2 ==> eth3 (Up)



11. Known Issues
===============
- PowerPC and ia64 architectures are not supported. x32 architectures were
  not tested.

- SRP is not supported.

- UD QPs that send traffic with VLAN tags (e.g. 802.1q tagged frames) do not
  work. This will be fixed in a subsequent release.

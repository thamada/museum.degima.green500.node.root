            Open Fabrics Enterprise Distribution (OFED)
                          Version 1.5.3
                             README

                          February 2011

==============================================================================
Table of contents
==============================================================================

 1.  Overview
 2.  Contents of the OFED Distribution
 3.  Hardware and Software Requirements
 4.  How to Download and Extract the OFED Distribution
 5.  Installing OFED Software
 6.  Building OFED RPMs
 7.  IPoIB Configuration
 8.  Using SDP
 9.  Uninstalling OFED
 10. Upgrading OFED
 11. Configuration
 12. Starting and Verifying the IB Fabric
 13. MPI (Message Passing Interface)
 14. Related Documentation


==============================================================================
1. Overview
==============================================================================

This is the OpenFabrics Enterprise Distribution (OFED) version 1.5.3
software package supporting InfiniBand and iWARP fabrics. It is composed
of several software modules intended for use on a computer cluster
constructed as an InfiniBand subnet or an iWARP network.

This document describes how to install the various modules and test them in
a Linux environment.

General Notes:
 1) The install script removes all previously installed OFED packages
    and re-installs from scratch. (Note: Configuration files will not
    be removed).  You will be prompted to acknowledge the deletion of
    the old packages.

 2) When installing OFED on an entire [homogeneous] cluster, a common
    strategy is to install the software on one of the cluster nodes
    (perhaps on a shared file system such as NFS). The resulting RPMs,
    created under OFED-X.X.X/RPMS directory, can then be installed on all
    nodes in the cluster using any cluster-aware tools (such as pdsh).

==============================================================================
2. OFED Package Contents
==============================================================================

The OFED Distribution package generates RPMs for installing the following:

  o   OpenFabrics core and ULPs:
        - HCA drivers (mthca, mlx4, qib, ehca)
        - iWARP driver (cxgb3, nes)
        - core
        - Upper Layer Protocols: IPoIB, SDP, SRP Initiator and target, iSER
          Initiator and target, RDS, qlgc_vnic, uDAPL and NFS-RDMA
  o   OpenFabrics utilities
        - OpenSM: InfiniBand Subnet Manager
        - Diagnostic tools
        - Performance tests
  o   MPI
        - OSU MVAPICH stack supporting the InfiniBand and iWARP interface
        - Open MPI stack supporting the InfiniBand and iWARP interface
        - OSU MVAPICH2 stack supporting the InfiniBand and iWARP interface
        - MPI benchmark tests (OSU BW/LAT, Intel MPI Benchmark, Presta)
  o   Extra packages
        - open-iscsi: open-iscsi initiator with iSER support
        - ib-bonding: Bonding driver for IPoIB interface
  o   Sources of all software modules (under conditions mentioned in the
      modules' LICENSE files)
  o   Documentation

==============================================================================
3. Hardware and Software Requirements
==============================================================================

1) Server platform with InfiniBand HCA or iWARP RNIC (see OFED Distribution
   Release Notes for details)

2) Linux operating system (see OFED Distribution Release Notes for details)

3) Administrator privileges on your machine(s)

4) Disk Space:  - For Build & Installation: 300MB
                - For Installation only:    200MB

5) For the OFED Distribution to compile on your machine, some software
   packages of your operating system (OS) distribution are required. These
   are listed here.

OS Distribution         Required Packages
---------------         ----------------------------------
General:
o  Common to all        gcc, glib, glib-devel, glibc, glibc-devel,
                        glibc-devel-32bit (to build 32-bit libraries on x86_86
                        and ppc64), zlib-devel, libstdc++-devel
o  RedHat, Fedora       kernel-devel, rpm-build, redhat-rpm-config
o  SLES                 kernel-source, rpm

Note:   To build 32-bit libraries on x86_64 and ppc64 platforms, the 32-bit
        glibc-devel should be installed.

Specific Component Requirements:
o  Mvapich              a Fortran Compiler (such as gcc-g77)
o  Mvapich2             libsysfs-devel
o  Open MPI             libsysfs-devel
o  ibutils              tcl-8.4, tcl-devel-8.4, tk, libstdc++-devel
o  mstflint             libstdc++-devel (32-bit on ppc64), gcc-c++
o  rnfs-utils           krb5-devel, krb5-libs, libevent-devel,
                        nfs-utils-lib-devel, openldap-devel,
                        e2fsprogs-devel (on RedHat)
                        krb5-devel, libevent-devel, nfsidmap-devel,
                        libopenssl-devel, libblkid-devel (on SLES11)
                        krb5-devel, libevent, nfsidmap, krb5, openldap2-devel,
                        cyrus-sasl-devel, e2fsprogs-devel (on SLES10)

Note:   The installer will warn you if you attempt to compile any of the
        above packages and do not have the prerequisites installed.
        On SLES, some of required RPMs can be found on SLES SDK DVD.
        E.g.: libgfortran43, kernel-source, ...

*** Important Note for open-iscsi users:
    Installing iSER as part of OFED installation will also install open-iscsi.
    Before installing OFED, please uninstall any open-iscsi version that may
    be installed on your machine. Installing OFED with iSER support while
    another open-iscsi version is already installed will cause the installation
    process to fail.

==============================================================================
4. How to Download and Extract the OFED Distribution
==============================================================================

1) Download the OFED-X.X.X.tgz file to your target Linux host.

   If this package is to be installed on a cluster, it is recommended to
   download it to an NFS shared directory.

2) Extract the package using:

     tar xzvf OFED-X.X.X.tgz

==============================================================================
5. Installing OFED Software
==============================================================================

1) Go to the directory into which the package was extracted:

     cd /..../OFED-X.X.X

2) Installing the OFED package must be done as root.  For a
   menu-driven first build and installation, run the installer
   script:

     ./install.pl

   Interactive menus will direct you through the install process.

   Note: After the installer completes, information about the OFED
         installation such as the prefix, the kernel version, and
         installation parameters can be found by running
         /etc/infiniband/info.

         Information on the driver version and source git trees can be found
         using the ofed_info utility


   During the interactive installation of OFED, two files are
   generated: ofed.conf and ofed_net.conf.
   ofed.conf holds the installed software modules and configuration settings
   chosen by the user. ofed_net.conf holds the IPoIB settings chosen by the
   user.

   If the package is installed on a cluster-shared directory, these
   files can then be used to perform an automatic, unattended
   installation of OFED on other machines in the cluster. The
   unattended installation will use the same choices as were selected
   in the interactive installation.

   For an automatic installation on any host, run the following:

     ./OFED-X.X.X/install.pl -c <path>/ofed.conf -n <path>/ofed_net.conf

3) Install script usage:

 Usage: ./install.pl [-c <packages config_file>|--all|--hpc|--basic]
                     [-n|--net <network config_file>]

           -c|--config <packages config_file>. Example of the config file can
                                be found under docs (ofed.conf-example)
           -n|--net <network config_file>      Example of the config file can be
                                found under docs (ofed_net.conf-example)
           -l|--prefix          Set installation prefix.
           -p|--print-available Print available packages for current platform.
                                And create corresponding ofed.conf file.
           -k|--kernel <kernel version>. Default on this system: $(uname -r)
           -s|--kernel-sources  <path to the kernel sources>. Default on this
                                system: /lib/modules/$(uname -r)/build
           --build32            Build 32-bit libraries. Relevant for x86_64 and
                                ppc64 platforms
           --without-depcheck   Skip Distro's libraries check
           -v|-vv|-vvv.         Set verbosity level
           -q.                  Set quiet - no messages will be printed
           --force              Force uninstall RPM coming with Distribution
           --builddir           Change build directory. Default: /var/tmp/

           --all|--hpc|--basic  Install all,hpc or basic packages
                                correspondingly

Notes:
------
a. It is possible to rename and/or edit the ofed.conf and ofed_net.conf files.
   Thus it is possible to change user choices (observing the original format).
   See examples of ofed.conf and ofed_net.conf under OFED-X.X.X/docs.
   Run './install.pl -p' to get ofed.conf with all available packages included.

b. Important note for open-iscsi users:
   Installing iSER as part of the OFED installation will also install
   open-iscsi. Before installing OFED, please uninstall any open-iscsi version
   that may be installed on your machine. Installing OFED with iSER support
   while another open-iscsi version is already installed will cause the
   installation process to fail.


Install Process Results:
------------------------

o The OFED package is installed under <prefix> directory. Default prefix is /usr
o The kernel modules are installed under:
  - Infiniband subsystem:
    /lib/modules/`uname -r`/updates/kernel/drivers/infiniband/
  - open-iscsi:
    /lib/modules/`uname -r`/updates/kernel/drivers/scsi/
  - Chelsio driver:
    /lib/modules/`uname -r`/updates/kernel/drivers/net/cxgb3/
  - ConnectX driver:
    /lib/modules/`uname -r`/updates/kernel/drivers/net/mlx4/
  - RDS:
    /lib/modules/`uname -r`/updates/kernel/net/rds/
  - NFSoRDMA:
    /lib/modules/`uname -r`/updates/kernel/fs/exportfs/
    /lib/modules/`uname -r`/updates/kernel/fs/lockd/
    /lib/modules/`uname -r`/updates/kernel/fs/nfs/
    /lib/modules/`uname -r`/updates/kernel/fs/nfs_common/
    /lib/modules/`uname -r`/updates/kernel/fs/nfsd/
    /lib/modules/`uname -r`/updates/kernel/net/sunrpc/
  - Bonding module:
    /lib/modules/`uname -r`/updates/kernel/drivers/net/bonding/bonding.ko
o The package kernel include files are placed under <prefix>/src/ofa_kernel/.
  These includes should be used when building kernel modules which use
  the Openfabrics stack. (Note that these includes, if needed, are
  "backported" to your kernel).
o The raw package (un-backported) source files are placed under
  <prefix>/src/ofa_kernel-x.x.x
o The script "openibd" is installed under /etc/init.d/. This script can
  be used to load and unload the software stack.
o The directory /etc/infiniband is created with the files "info" and
  "openib.conf". The "info" script can be used to retrieve OFED
  installation information. The "openib.conf" file contains the list of
  modules that are loaded when the "openibd" script is used.
o The file "90-ib.rules" is installed under /etc/udev/rules.d/
o If libibverbs-utils is installed, then ofed.sh and ofed.csh are
  installed under /etc/profile.d/. These automatically update the PATH
  environment variable with <prefix>/bin.  In addition, ofed.conf is
  installed under /etc/ld.so.conf.d/ to update the dynamic linker's
  run-time search path to find the InfiniBand shared libraries.
o The file /etc/modprobe.d/ib_ipoib.conf is updated to include the following:
  - "alias ib<n> ib_ipoib" for each ib<n> interface.
o The file /etc/modprobe.d/ib_sdp.conf is updated to include the following:
  - "alias net-pf-27 ib_sdp" for sdp.
o If opensm is installed, the daemon opensmd is installed under /etc/init.d/
o All verbs tests and examples are installed under <prefix>/bin and management
  utilities under <prefix>/sbin
o ofed_info script provides information on the OFED version and git repository.
o If iSER is included, open-iscsi user-space files will be also installed:
  - Configuration files will be installed at /etc/iscsi
  - Startup script will be installed at:
    - RedHat: /etc/init.d/iscsi
    - SuSE: /etc/init.d/open-iscsi
  - Other tools (iscsiadm, iscsid, iscsi_discovery, iscsi-iname, iscsistart)
    will be installed under /sbin.
  - Documentation will be installed under:
    - RedHat: /usr/share/doc/iscsi-initiator-utils-<version number>
    - SuSE: /usr/share/doc/packages/open-iscsi
o man pages will be installed under /usr/share/man/.

==============================================================================
6. Building OFED RPMs
==============================================================================

1) Go to the directory into which the package was extracted:

     cd /..../OFED-X.X.X

2) Run install.pl as explained above
   This script also builds OFED binary RPMs under OFED-X.X.X/RPMS; the sources
   are placed in OFED-X.X.X/SRPMS/.

   Once the install process has completed, the user may run ./install.pl on
   other machines that have the same operating system and kernel to
   install the new RPMs.

Note: Depending on your hardware, the build procedure may take 30-45
      minutes.  Installation, however, is a relatively short process
      (~5 minutes).  A common strategy for OFED installation on large
      homogeneous clusters is to extract the tarball on a network
      file system (such as NFS), build OFED RPMs on NFS, and then run the
      installer on each node with the RPMs that were previously built.

==============================================================================
7. IP-over-IB (IPoIB) Configuration
==============================================================================

Configuring IPoIB is an optional step during the installation.  During
an interactive installation, the user may choose to insert the ifcfg-ib<n>
files.  If this option is chosen, the ifcfg-ib<n> files will be
installed under:

- RedHat: /etc/sysconfig/network-scripts/
- SuSE:   /etc/sysconfig/network/

Setting IPoIB Configuration:
----------------------------
There is no default configuration for IPoIB interfaces.

One should manually specify the full IP configuration during the
interactive installation: IP address, network address, netmask, and
broadcast address, or use the ofed_net.conf file.

For bonding setting please see "ipoib_release_notes.txt"

For unattended installations, a configuration file can be provided
with this information.  The configuration file must specify the
following information:
- Fixed values for each IPoIB interface
- Base IPoIB configuration on Ethernet configuration (may be useful for
  cluster configuration)

Here are some examples of ofed_net.conf:

# Static settings; all values provided by this file
IPADDR_ib0=172.16.0.4
NETMASK_ib0=255.255.0.0
NETWORK_ib0=172.16.0.0
BROADCAST_ib0=172.16.255.255
ONBOOT_ib0=1

# Based on eth0; each '*' will be replaced by the script with corresponding
# octet from eth0.
LAN_INTERFACE_ib0=eth0
IPADDR_ib0=172.16.'*'.'*'
NETMASK_ib0=255.255.0.0
NETWORK_ib0=172.16.0.0
BROADCAST_ib0=172.16.255.255
ONBOOT_ib0=1

# Based on the first eth<n> interface that is found (for n=0,1,...);
# each '*' will be replaced by the script with corresponding octet from eth<n>.
LAN_INTERFACE_ib0=
IPADDR_ib0=172.16.'*'.'*'
NETMASK_ib0=255.255.0.0
NETWORK_ib0=172.16.0.0
BROADCAST_ib0=172.16.255.255
ONBOOT_ib0=1


==============================================================================
8. Using SDP
==============================================================================

Overview:
---------

Sockets Direct Protocol (SDP) is an InfiniBand byte-stream transport protocol
that provides TCP stream semantics. Capable of utilizing InfiniBand's advanced
protocol offload capabilities, SDP can provide lower latency, higher
bandwidth, and lower CPU utilization than IPoIB running some sockets-based
applications.

SDP can be used by applications and improve their performance transparently
(that is, without any recompilation). Since SDP has the same socket semantics
as TCP, an existing application is able to run using SDP; the difference is
that the application's TCP socket gets replaced with an SDP socket.

It is also possible to configure the driver to automatically translate TCP to
SDP based on the source IP, the destination, or the application name (See
below).

The SDP protocol is composed of a kernel module that implements the SDP as a
new address-family/protocol-family, and a library that is used for replacing
the TCP address family with SDP according to a policy.

libsdp.so Library:
------------------

libsdp.so is a dynamically linked library, which is used for transparent
integration of applications with SDP. The library is preloaded, and therefore
takes precedence over glibc for certain socket calls. Thus, it can
transparently replace the TCP socket family with SDP socket calls.

The library also implements a user-level socket switch. Using a configuration
file, the system administrator can set up the policy that selects the type of
socket to be used. libsdp.so also has the option to allow server sockets to
listen on both SDP and TCP interfaces. The various configurations with SDP/TCP
sockets are explained inside the /etc/libsdp.conf file.

Configuring SDP:
----------------

To load SDP upon boot, edit the file  /etc/infiniband/openib.conf and set
"SDP_LOAD=yes".

Note: For the changes to take effect, run: /etc/init.d/openibd restart

SDP shares the same IP addresses and interface names as IPoIB. See IPoIB
Configuration (chapter 7)

How to Know SDP Is Working:
---------------------------

Since SDP is a transparent TCP replacement, it can sometimes be difficult to
know that it is working correctly.
To figure out whether traffic is passing through SDP or TCP, check
/proc/net/sdpstats and monitor which counters are running.

sdpnetstat:
-----------

The sdpnetstat program can be used to verify both that SDP is loaded and is
being used:

host1$ sdpnetstat -S

This command shows all active SDP sockets using the same format as the
traditional netstat program.  Without the '-S' option, it shows all the
information that netstat does plus SDP data.

Assuming that the SDP kernel module is loaded and is being used, then the
output of the command will show something like the following:

host1$ sdpnetstat -S

Proto Recv-Q Send-Q Local Address           Foreign Address
sdp        0      0 193.168.10.144:34216    193.168.10.125:12865
sdp        0 884720 193.168.10.144:42724    193.168.10.:filenet-rmi

The example output above shows  two active SDP sockets and contains details
about the connections.  If the SDP kernel module is not loaded, or it is
loaded but is not being used, then the output of the command will be something
like the following:

host1$ sdpnetstat -S

Proto Recv-Q Send-Q Local Address           Foreign Address
netstat: no support for `AF INET (tcp)' on this system.

To verify whether the module is loaded or not, you can use the lsmod command

Monitoring and Troubleshooting Tools:
-------------------------------------

SDP has debug support for both the user space libsdp.so library and the ib_sdp
kernel module.
Both can be useful to understand why a TCP socket was not redirected over SDP
and to help find problems in the SDP implementation.

User-space SDP debug is controlled by options in the libsdp.conf file. You can also have a local
version and point to it explicitly using the following command:

host1$ export LIBSDP_CONFIG_FILE=<path>/libsdp.conf

To obtain extensive debug information, you can modify libsdp.conf to have the
log directive produce maximum debug output (provide the min-level flag with
the value 1). More details in the default libsdp.conf installed by OFED.
A non-root user can configure libsdp.so to record function calls and return values in the file
/tmp/libsdp.log.<pid>

Kernel Space SDP Debug - The SDP kernel module can log detailed trace
information if you enable it using the 'debug_level' variable in the sysfs
filesystem. The following command performs this:

host1$ echo 1 > /sys/module/ib_sdp/debug_level

Note: Depending on the operating system distribution on your machine, you may need
an extra level, 'parameters', in the directory structure, so you may need to direct
the echo command to /sys/module/ib_sdp/parameters/debug_level.

Turning off kernel debug is done by setting the sysfs variable to zero using
the following command:

host1$ echo 0 > /sys/module/ib_sdp/debug_level

To display debug information, use the dmesg command:

host1$ dmesg

Environment Variables:
----------------------

For the transparent integration with SDP, the following two environment
variables are required:
1. LD_PRELOAD - this environment variable is used to preload libsdp.so and it
   should point to the libsdp.so library. The variable should be set by the
   system administrator to libsdp.so.
2. LIBSDP_CONFIG_FILE - this environment variable is used to configure the
   policy for replacing TCP sockets with SDP sockets. By default it points to:
   /etc/libsdp.conf

Using RDMA:
-----------

For smaller buffers, the overhead of preparing a user buffer to be RDMA'ed is
too big; therefore, it is more efficient to use BCopy. (Large buffers can also
be sent using RDMA, but they lower CPU utilization.) This mode is called
"ZCopy combined mode". The sendmsg syscall is blocked until the buffer is
transfered to the socket's peer, and the data is copied directly from the user
buffer at the source side to the user buffer at the sink side.

To set the threshold, use the module parameter sdp_zcopy_thresh. This parameter
can be accessed through sysfs (/sys/module/ib_sdp/parameters/sdp_zcopy_thresh).
Setting it to 0, disables ZCopy.


==============================================================================
9. Uninstalling OFED
==============================================================================

There are two ways to uninstall OFED:
1) Via the installation menu.
2) Using the script ofed_uninstall.sh. The script is part of ofed-scripts
   package.
3) ofed_uninstall.sh script supports an option to executes 'openibd stop'
   before removing the RPMs using the flag: --unload-modules

==============================================================================
10. Upgrading OFED
==============================================================================

If an old OFED version is installed, it may be upgraded by installing a
new OFED version as described in section 5. Note that if the old OFED
version was loaded before upgrading, you need to restart OFED or reboot
your machine in order to start the new OFED stack.

==============================================================================
11. Configuration
==============================================================================

Most of the OFED components can be configured or reconfigured after
the installation by modifying the relevant configuration files.  The
list of the modules that will be loaded automatically upon boot can be
found in the /etc/infiniband/openib.conf file.  Other configuration
files include:
- SDP configuration file:    /etc/libsdp.conf
- OpenSM configuration file: /etc/ofa/opensm.conf (for RedHat)
                             /etc/sysconfig/opensm (for SuSE) - should be
                             created manually if required.
- DAPL configuration file:   /etc/dat.conf

See packages Release Notes for more details.

Note: After the installer completes, information about the OFED
      installation such as the prefix, kernel version, and
      installation parameters can be found by running
      /etc/infiniband/info.


==============================================================================
12. Starting and Verifying the IB Fabric
==============================================================================
1)  If you rebooted your machine after the installation process completed,
    IB interfaces should be up. If you did not reboot your machine, please
    enter the following command: /etc/init.d/openibd restart

2)  Check that the IB driver is running on all nodes: ibv_devinfo should print
    "hca_id: <linux device name>" on the first line.

3)  Make sure that a Subnet Manager is running by invoking the sminfo utility.
    If an SM is not running, sminfo prints:
    sminfo: iberror: query failed
    If an SM is running, sminfo prints the LID and other SM node information.
    Example:
    sminfo: sm lid 0x1 sm guid 0x2c9010b7c2ae1, activity count 20 priority 1

    To check if OpenSM is running on the management node, enter: /etc/init.d/opensmd status
    To start OpenSM, enter: /etc/init.d/opensmd start

    Note: OpenSM parameters can be set via the file /etc/opensm/opensm.conf

4)  Verify the status of ports by using ibv_devinfo: all connected ports should
    report a "PORT_ACTIVE" state.

5)  Check the network connectivity status: run ibchecknet to see if the subnet
    is "clean" and ready for ULP/application use. The following tools display
    more information in addition to IB info: ibnetdiscover, ibhosts, and
    ibswitches.

6)  Alternatively, instead of running steps 3 to 5 you can use the ibdiagnet
    utility to perform a set of tests on your network. Upon finding an error,
    ibdiagnet will print a message starting with a "-E-". For a more complete
    report of the network features you should run ibdiagnet -r. If you have a
    topology file describing your network you can feed this file to ibdiagnet
    (using the option: -t <file>) and all reports will use the names they
    appear in the file (instead of LIDs, GUIDs and directed routes).

7)  To run an application over SDP set the following variables:
    env LD_PRELOAD='stack_prefix'/lib/libsdp.so
    LIBSDP_CONFIG_FILE=/etc/libsdp.conf <application name>
    (or LD_PRELOAD='stack_prefix'/lib64/libsdp.so on 64 bit machines)
    The default 'stack_prefix' is /usr

==============================================================================
13. MPI (Message Passing Interface)
==============================================================================
In Step 2 of the main menu of install.pl, options 2, 3 and 4 can
install one or more MPI stacks.  Multiple MPI stacks can be installed
simultaneously -- they will not conflict with each other.

Three MPI stacks are included in this release of OFED:
- MVAPICH
- Open MPI
- MVAPICH2

OFED also includes 4 basic tests that can be run against each MPI
stack: bandwidth (bw), latency (lt), Intel MPI Benchmark and Presta. The tests
are located under: <prefix>/mpi/<compiler>/<mpi stack>/tests/.

Please see MPI_README.txt for more details on each MPI package and how to run
the tests.

==============================================================================
14. Related Documentation
==============================================================================

OFED documentation is located in the ofed-docs RPM.  After
installation the documents are located under the directory:
/usr/share/doc/ofed-docs-x.x.x for RedHat
/usr/share/doc/packages/ofed-docs-x.x.x for SuSE

Documents list:

   o README.txt
   o OFED_Installation_Guide.txt
   o MPI_README.txt
   o Examples of configuration files
   o OFED_tips.txt
   o HOWTO.build_ofed
   o All release notes and README files

For more information, please visit the OpenFabrics web site:
   http://www.openfabrics.org

open-iscsi documentation is located at:
- RedHat: /usr/share/doc/iscsi-initiator-utils-<version number>
- SuSE: /usr/share/doc/packages/open-iscsi

For more information, please visit the open-iscsi web site:
   http://www.open-iscsi.org

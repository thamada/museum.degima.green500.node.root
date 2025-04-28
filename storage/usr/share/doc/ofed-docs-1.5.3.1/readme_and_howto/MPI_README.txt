
			   MPI in OFED 1.5.2 README

				September 2010

===============================================================================
Table of Contents
===============================================================================
1. Overview
2. MVAPICH
3. Open MPI
4. MVAPICH2


===============================================================================
1. Overview
===============================================================================
Open Fabrics Enterprise Distribution (OFED)Three MPI stacks are included in
this release of OFED:
- MVAPICH 1.2.0
- Open MPI 1.4.2
- MVAPICH2 1.5.1

Setup, compilation and run information of MVAPICH, Open MPI and MVAPICH2 is
provided below in sections 2, 3 and 4 respectively.

1.1 Installation Note
---------------------
In Step 2 of the main menu of install.pl, options 2, 3 and 4 can install
one or more MPI stacks. Please refer to docs/OFED_Installation_Guide.txt
to learn about the different options.

The installation script allows each MPI to be compiled using one or
more compilers. Users need to set, per MPI stack installed, the PATH
and/or LD_LIBRARY_PATH so as to install the desired compiled MPI stacks.

1.2 MPI Tests
-------------
OFED includes four basic tests that can be run against each MPI stack:
bandwidth (bw), latency (lt), Intel MPI Benchmark, and Presta. The tests
are located under: <prefix>/mpi/<compiler>/<mpi stack>/tests/, 
where <prefix> is /usr by default.

1.4 Selecting Which MPI to Use: mpi-selector
--------------------------------------------
Depending on how the OFED installer was run, multiple different MPI
implementations may be installed on your system.  The OFED installer
will run an MPI selector tool during the installation process,
presenting a menu-based interface to select which MPI implementation
is set as the default for all users.  This MPI selector tool can be
re-run at any time by the administrator after the OFED installer
completes to modify the site-wide default MPI implementation selection
by invoking the "mpi-selector-menu" command (root access is typically
required to change the site-wide default).

The mpi-selector-menu command can also be used by non-administrative
users to override the site-wide default MPI implementation selection
by setting a per-user default.  Specifically: unless a user runs the
MPI selector tool to set a per-user default, their environment will be
setup for the site-wide default MPI implementation.

Note that the default MPI selection does *not* affect the shell from
which the command was invoked (or any other shells that were already
running when the MPI selector tool was invoked).  The default
selection is only changed for *new* shells started after the selector
tool was invoked.  It is recommended that once the default MPI
implementation is changed via the selector tool, users should logout
and login again to ensure that they have a consistent view of the
default MPI implementation.  Other tools can be used to change the MPI
environment in the current shell, such as the environment modules
software package (which is not included in the OFED software package;
see http://modules.sourceforge.net/ for details).

Note that the site-wide default is set in a file that is typically not
on a networked file system, and is therefore specific to the host on
which it was run.  As such, it is recommended to run the
mpi-selector-menu command on all hosts in a cluster, picking the same
default MPI implementation on each.  It may be more convenient,
however, to use the mpi-selector command in script-based scenarios
(such as running on every host in a cluster); mpi-selector effects all
the same functionality as mpi-selector-menu, but is intended for
automated environments.  See the mpi-selector(1) manual page for more
details.

Additionally, per-user defaults are set in a file in the user's $HOME
directory.  If this directory is not on a network-shared file system
between all hosts that will be used for MPI applications, then it also
needs to be propagated to all relevant hosts.

Note: The MPI selector tool typically sets the PATH and/or
LD_LIBRARY_PATH for a given MPI implementation.  This step can, of
course, also be performed manually by a user or on a site-wide basis.
The MPI selector tool simply bundles up this functionality in a
convenient set of command line tools and menus.

1.4 Updating MPI Installations
------------------------------
Note that all of the MPI implementations included in the OFED software
package are the versions that were available when OFED v1.5 was
released.  They have been QA tested with this version of OFED and are
fully supported.

However, note that administrators can go to the web sites of each MPI
implementation and download / install newer versions after OFED has
been successfully installed.  There is nothing specific about the
OFED-included MPI software packages that prohibit installing
newer/other MPI implementations.

It should be also noted that versions of MPI released after OFED v1.5
are not supported by OFED.  But since each MPI has its own release
schedule and QA process (each of which involves testing with the OFED
stack), it may sometimes be desirable -- or even advisable, depending
on how old the MPI implementations are that are included in OFED -- to
download install a newer version of MPI.

The web sites of each MPI implementation are listed below:

- Open MPI: http://www.open-mpi.org/
- MVAPICH:  http://mvapich.cse.ohio-state.edu/
- MVAPICH2: http://mvapich.cse.ohio-state.edu/overview/mvapich2/

===============================================================================
2. MVAPICH MPI
===============================================================================

This package is a 1.2.0 version of the MVAPICH software package,
and is the officially supported MPI stack for this release of OFED. 
See http://mvapich.cse.ohio-state.edu for more details.
 

2.1 Setting up for MVAPICH
--------------------------
To launch MPI jobs, its installation directory needs to be included
in PATH and LD_LIBRARY_PATH. To set them, execute one of the following
commands:
  source <prefix>/mpi/<compiler>/<mpi stack>/bin/mpivars.sh
	-- when using sh for launching MPI jobs
 or
  source <prefix>/mpi/<compiler>/<mpi stack>/bin/mpivars.csh
	-- when using csh for launching MPI jobs


2.2 Compiling MVAPICH Applications:
-----------------------------------
***Important note***: 
A valid Fortran compiler must be present in order to build the MVAPICH MPI
stack and tests.

The default gcc-g77 Fortran compiler is provided with all RedHat Linux
releases. SuSE distributions earlier than SuSE Linux 9.0 do not provide
this compiler as part of the default installation.

The following compilers are supported by OFED's MVAPICH package: Gcc,
Intel, Pathscale and PGI.  The install script prompts the user to choose
the compiler with which to build the MVAPICH RPM. Note that more
than one compiler can be selected simultaneously, if desired.

For details see:
  http://mvapich.cse.ohio-state.edu/support

To review the default configuration of the installation, check the default
configuration file: <prefix>/mpi/<compiler>/<mpi stack>/etc/mvapich.conf

2.3 Running MVAPICH Applications:
---------------------------------
Requirements:
o At least two nodes. Example: mtlm01, mtlm02
o Machine file: Includes the list of machines. Example: /root/cluster
o Bidirectional rsh or ssh without a password
 
Note: ssh will be used unless -rsh is specified. In order to use
rsh, add to the mpirun_rsh command the parameter: -rsh

*** Running OSU tests ***

/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/osu_benchmarks-3.1.1/osu_bw
/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/osu_benchmarks-3.1.1/osu_latency
/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/osu_benchmarks-3.1.1/osu_bibw
/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/osu_benchmarks-3.1.1/osu_bcast

*** Running Intel MPI Benchmark test (Full test) ***

/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/IMB-3.2/IMB-MPI1
 
*** Running Presta test ***

/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/presta-1.4.0/com -o 100
/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/presta-1.4.0/glob -o 100
/usr/mpi/gcc/mvapich-1.2.0/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich-1.2.0/tests/presta-1.4.0/globalop


===============================================================================
3. Open MPI
===============================================================================

Open MPI is a next-generation MPI implementation from the Open MPI
Project (http://www.open-mpi.org/).  Version 1.4 of Open MPI is
included in this release, which is also available directly from the
main Open MPI web site.

A working Fortran compiler is not required to build Open MPI, but some
of the included MPI tests are written in Fortran.  These tests will
not compile/run if Open MPI is built without Fortran support.

The following compilers are supported by OFED's Open MPI package: GNU,
Pathscale, Intel, or Portland.  The install script prompts the user
for the compiler with which to build the Open MPI RPM.  Note that more
than one compiler can be selected simultaneously, if desired.

Users should check the main Open MPI web site for additional
documentation and support. (Note: The FAQ file considers OpenFabrics
tuning among other issues.)

3.1 Setting up for Open MPI
---------------------------
Selecting to use Open MPI via the mpi-selector-mpi and mpi-selector
tools will perform all the necessary setup for users to build and run
Open MPI applications.  If you use the MPI selector tools, you can
skip the rest of this section.

If you do not wish to use the MPI selector tools, the Open MPI team
strongly advises users to put the Open MPI installation directory in
their PATH and LD_LIBRARY_PATH. This can be done at the system level
if all users are going to use Open MPI.  Specifically:

- add <prefix>/bin to PATH
- add <prefix>/lib to LD_LIBRARY_PATH

<prefix> is the directory where the desired Open MPI instance was
installed ("instance" refers to the compiler used for Open MPI
compilation at install time.).

If you are using a job scheduler to launch MPI jobs (e.g., SLURM,
Torque), setting the PATH and LD_LIBRARY_PATH is still required, but
it does not need to be set in your shell startup files.  Procedures
describing how to add these values to PATH and LD_LIBRARY_PATH are
described in detail at:

    http://www.open-mpi.org/faq/?category=running

3.2 Open MPI Installation Support / Updates
-------------------------------------------
The OFED package will install Open MPI with support for TCP, shared
memory, and the OpenFabrics network stacks.  No other networks are
supported by the OFED Open MPI installation.

Open MPI supports a wide variety of run-time environments.  The OFED
installer will not include support for all of them, however (e.g.,
Torque and PBS-based environments are not supported by the
OFED-installed Open MPI).

The ompi_info command can be used to see what support was installed;
look for plugins for your specific environment / network / etc.  If
you do not see them, the OFED installer did not include support for
them.

As described above, administrators or users can go to the Open MPI web
site and download / install either a newer version of Open MPI (if
available), or the same version with different configuration options
(e.g., support for Torque / PBS-based environments).

3.3 Compiling Open MPI Applications
-----------------------------------
(copied from http://www.open-mpi.org/faq/?category=mpi-apps -- see 
this web page for more details)

The Open MPI team strongly recommends that you simply use Open MPI's
"wrapper" compilers to compile your MPI applications. That is, instead
of using (for example) gcc to compile your program, use mpicc. Open
MPI provides a wrapper compiler for four languages:

          Language       Wrapper compiler name 
          -------------  --------------------------------
          C              mpicc
          C++            mpiCC, mpicxx, or mpic++
                         (note that mpiCC will not exist
                          on case-insensitive file-systems)
          Fortran 77     mpif77
          Fortran 90     mpif90
          -------------  --------------------------------

Note that if no Fortran 77 or Fortran 90 compilers were found when
Open MPI was built, Fortran 77 and 90 support will automatically be
disabled (respectively).

If you expect to compile your program as: 

    > gcc my_mpi_application.c -lmpi -o my_mpi_application
 
Simply use the following instead: 

    > mpicc my_mpi_application.c -o my_mpi_application

Specifically: simply adding "-lmpi" to your normal compile/link
command line *will not work*.  See
http://www.open-mpi.org/faq/?category=mpi-apps if you cannot use the
Open MPI wrapper compilers.
 
Note that Open MPI's wrapper compilers do not do any actual compiling
or linking; all they do is manipulate the command line and add in all
the relevant compiler / linker flags and then invoke the underlying
compiler / linker (hence, the name "wrapper" compiler). More
specifically, if you run into a compiler or linker error, check your
source code and/or back-end compiler -- it is usually not the fault of
the Open MPI wrapper compiler.

3.4 Running Open MPI Applications:
----------------------------------
Open MPI uses either the "mpirun" or "mpiexec" commands to launch
applications.  If your cluster uses a resource manager (such as
SLURM), providing a hostfile is not necessary:

    > mpirun -np 4 my_mpi_application

If you use rsh/ssh to launch applications, they must be set up to NOT
prompt for a password (see http://www.open-mpi.org/faq/?category=rsh
for more details on this topic).  Moreover, you need to provide a
hostfile containing a list of hosts to run on.

Example:

    > cat hostfile
    host1.example.com
    host2.example.com
    host3.example.com
    host4.example.com

    > mpirun -np 4 -hostfile hostfile my_mpi_application
      (application runs on all 4 hosts)

In the following examples, replace <N> with the number of hosts to run on,
and <HOSTFILE> with the filename of a valid hostfile listing the hosts
to run on (unless you are running under a supported resource manager,
in which case a hostfile is unnecessary).

Also note that Open MPI is highly run-time tunable.  There are many
options that can be tuned to obtain optimal performance of your MPI
applications (see the Open MPI web site / FAQ for more information:
http://www.open-mpi.org/faq/).

 - <N> is an integer indicating how many MPI processes to run (e.g., 2)
 - <HOSTFILE> is the filename of a hostfile, as described above

Example 1: Running the OSU bandwidth:

    > cd /usr/mpi/gcc/openmpi-1.4.1/tests/osu_benchmarks-3.1.1
    > mpirun -np <N> -hostfile <HOSTFILE> osu_bw

Example 2: Running the Intel MPI Benchmark benchmarks:

    > cd /usr/mpi/gcc/openmpi-1.4.1/tests/IMB-3.2
    > mpirun -np <N> -hostfile <HOSTFILE> IMB-MPI1

    --> Note that the version of IMB-EXT that ships in this version of
        OFED contains a bug that will cause it to immediately error
        out when run with Open MPI.

Example 3: Running the Presta benchmarks:

    > cd /usr/mpi/gcc/openmpi-1.4.1/tests/presta-1.4.0
    > mpirun -np <N> -hostfile <HOSTFILE> com -o 100

NOTE: In order to run Open MPI over RoCCE (RDMAoE) network, follow MCA parameter
      is required:
        --mca btl_openib_cpc_include rdmacm


3.5 More Open MPI Information
-----------------------------
Much, much more information is available about using and tuning Open
MPI (to include OpenFabrics-specific tunable parameters) on the Open
MPI web site FAQ:

    http://www.open-mpi.org/faq/

Users who cannot find the answers that they are looking for, or are
experiencing specific problems should consult the "how to get help" web
page for more information:

    http://www.open-mpi.org/community/help/


===============================================================================
4. MVAPICH2 MPI
===============================================================================

MVAPICH2 is an MPI-2 implementation which includes all MPI-1 features.
It is based on MPICH2 and MVICH.  MVAPICH2 provides many features including
fault-tolerance with checkpoint-restart, RDMA_CM support, iWARP support,
optimized collectives, on-demand connection management, multi-core optimized
and scalable shared memory support, and memory hook with ptmalloc2 library
support. The ADI-3-level design of MVAPICH2 supports many features including:
MPI-2 functionalities (one-sided, collectives and data-type), multi-threading
and all MPI-1 functionalities.  It also supports a wide range of platforms
(architecture, OS, compilers, InfiniBand adapters and iWARP adapters).  More
information can be found on the MVAPICH2 project site:

http://mvapich.cse.ohio-state.edu/overview/mvapich2/

A valid Fortran compiler must be present in order to build the MVAPICH2
MPI stack and tests.  The following compilers are supported by OFED's
MVAPICH2 MPI package: gcc, intel, pgi, and pathscale.  The install script
prompts the user to choose the compiler with which to build the MVAPICH2
MPI RPM.  Note that more than one compiler can be selected simultaneously,
if desired.

The install script prompts for various MVAPICH2 build options as detailed
below:


- Implementation (OFA or uDAPL)            [default "OFA"]
     - OFA (IB and iWARP) Options:
          - ROMIO Support                  [default Y]
          - Shared Library Support         [default Y]
          - Checkpoint-Restart Support     [default N]
               * requires an installation of BLCR and prompts for the
                 BLCR installation directory location
     - uDAPL Options:
          - ROMIO Support                  [default Y]
          - Shared Library Support         [default Y]
          - Cluster Size                   [default "Small"]
          - I/O Bus                        [default "PCI-Express"]
          - Link Speed                     [default "SDR"]
          - Default DAPL Provider          [default ""]
              * the default provider is determined based on detected OS

For non-interactive builds where no MVAPICH2 build options are stored in
the OFED configuration file, the default settings are:

Implementation:             OFA
ROMIO Support:              Y
Shared Library Support:     Y
Checkpoint-Restart Support: N


4.1 Setting up for MVAPICH2
---------------------------
Selecting to use MVAPICH2 via the MPI selector tools will perform
most of the setup necessary to build and run MPI applications with
MVAPICH2.  If one does not wish to use the MPI Selector tools, using
the following settings should be enough:

 - add <prefix>/bin to PATH

The <prefix> above is the directory where the desired MVAPICH2
instance was installed ("instance" refers to the path based on
the RPM package name, including the compiler chosen during the
install).  It is also possible to source the following files
in order to setup the proper environment:

source <prefix>/bin/mpivars.sh  [for Bourne based shells]
source <prefix>/bin/mpivars.csh [for C based shells]

In addition to the user environment settings handled by the MPI selector
tools, some other system settings might need to be modified.  MVAPICH2
requires the memlock resource limit to be modified from the default
in /etc/security/limits.conf:

*               soft    memlock         unlimited

MVAPICH2 requires bidirectional rsh or ssh without a password to work.
The default is ssh, and in this case it will be required to add the
following line to the /etc/init.d/sshd script before sshd is started:

ulimit -l unlimited

It is also possible to specify a specific size in kilobytes instead
of unlimited if desired.

The MVAPICH2 OFA build requires an /etc/mv2.conf file specifying the
IP address of an Infiniband HCA (IPoIB) for RDMA-CM functionality
or the IP address of an iWARP adapter for iWARP functionality if
either of those are desired.  This is not required by default, unless
either of the following runtime environment variables are set when
using the OFA MVAPICH2 build:

RDMA-CM
-------
MV2_USE_RDMA_CM=1

iWARP
-----
MV2_USE_IWARP_MODE=1

Otherwise, the OFA build will work without an /etc/mv2.conf file using
only the Infiniband HCA directly.

The MVAPICH2 uDAPL build requires an /etc/dat.conf file specifying the
DAPL provider information.  The default DAPL provider is chosen at
build time, with a default value of "ib0", however it can also be
specified at runtime by setting the following environment variable:

MV2_DEFAULT_DAPL_PROVIDER=<interface>

More information about MVAPICH2 can be found in the MVAPICH2 User Guide:

http://mvapich.cse.ohio-state.edu/support/


4.2 Compiling MVAPICH2 Applications
-----------------------------------
The MVAPICH2 compiler command for each language are:

Language          Compiler Command
--------          ----------------
C                 mpicc
C++               mpicxx
Fortran 77        mpif77
Fortran 90        mpif90

The system compiler commands should not be used directly.  The Fortran 90
compiler command only exists if a Fortran 90 compiler was used during the
build process.


4.3 Running MVAPICH2 Applications
---------------------------------
4.3.1 Running MVAPICH2 Applications with mpirun_rsh
---------------------------------------------------
>From release 1.2, MVAPICH2 comes with a faster and more scalable startup based 
on mpirun_rsh. To launch a MPI job with mpirun_rsh, password-less ssh needs to
be enabled across all nodes. 

Note: ssh will be used by default. In order to use rsh, use the -rsh option on 
the mpirun_rsh command line. For more options, see mpirun_rsh -help or the 
MVAPICH2 user guide.

*** Running 4 processes on 4 nodes ***

$ cat > hostfile
node1
node2
node3
node4
$ mpirun_rsh -np 4 -hostfile hostfile /path/to/my_mpi_app

*** Running OSU tests ***

/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/osu_benchmarks-3.1.1/osu_bw
/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/osu_benchmarks-3.1.1/osu_latency
/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/osu_benchmarks-3.1.1/osu_bibw
/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/osu_benchmarks-3.1.1/osu_bcast

*** Running Intel MPI Benchmark test (Full test) ***

/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/IMB-3.2/IMB-MPI1
 
*** Running Presta test ***

/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/presta-1.4.0/com -o 100
/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/presta-1.4.0/glob -o 100
/usr/mpi/gcc/mvapich2-1.2p1/bin/mpirun_rsh -np 2 -hostfile /root/cluster /usr/mpi/gcc/mvapich2-1.2p1/tests/presta-1.4.0/globalop

4.3.2 Running MVAPICH2 Applications with mpd and mpiexec
--------------------------------------------------------
Launching processes in MVAPICH2 is a two step process.  First, mpdboot must
be used to launch MPD daemons on the desired hosts.  Second, the mpiexec
command is used to launch the processes.  MVAPICH2 requires bidirectional
ssh or rsh without a password.  This is specified when the MPD daemons are
launched with the mpdboot command through the --rsh command line option.
The default is ssh.  Once the processes are finished, stopping the MPD
daemons with the mpdallexit command should be done.  The following example
shows the basic procedure:

4 Processes on 4 Hosts Example:

$ cat >hostsfile
node1.example.com
node2.example.com
node3.example.com
node4.example.com

$ mpdboot -n 4 -f ./hostsfile

$ mpiexec -n 4 ./my_mpi_application

$ mpdallexit

It is also possible to use the mpirun command in place of mpiexec.  They are
actually the same command in MVAPICH2, however using mpiexec is preferred.

It is possible to run more processes than hosts.  In this case, multiple
processes will run on some or all of the hosts used.  The following examples
demonstrate how to run the MPI tests.  The default installation prefix and
gcc version of MVAPICH2 are shown.  In each case, it is assumed that a hosts
file has been created in the specific directory with two hosts.

OSU Tests Example:

$ cd /usr/mpi/gcc/mvapich2-1.2p1/tests/osu_benchmarks-3.1.1
$ mpdboot -n 2 -f ./hosts
$ mpiexec -n 2 ./osu_bcast
$ mpiexec -n 2 ./osu_bibw
$ mpiexec -n 2 ./osu_bw
$ mpiexec -n 2 ./osu_latency
$ mpdallexit

Intel MPI Benchmark Example:

$ cd /usr/mpi/gcc/mvapich2-1.2p1/tests/IMB-3.2
$ mpdboot -n 2 -f ./hosts
$ mpiexec -n 2 ./IMB-MPI1
$ mpdallexit

Presta Benchmarks Example:

$ cd /usr/mpi/gcc/mvapich2-1.2p1/tests/presta-1.4.0
$ mpdboot -n 2 -f ./hosts
$ mpiexec -n 2 ./com -o 100
$ mpiexec -n 2 ./glob -o 100
$ mpiexec -n 2 ./globalop
$ mpdallexit

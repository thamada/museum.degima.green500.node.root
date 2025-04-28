	     Open Fabrics Enterprise Distribution (OFED)
                Performance Tests README for OFED 1.5
		  
			  December 2010



===============================================================================
Table of Contents
===============================================================================
1. Overview
2. Notes on Testing Methodology
3. Test Descriptions
4. Running Tests

===============================================================================
1. Overview
===============================================================================
This is a collection of tests written over uverbs intended for use as a
performance micro-benchmark. As an example, the tests can be used for
HW or SW tuning and/or functional testing.

The collection conatains a set of BW and latency benchmark such as :

	* Read  - ib_read_bw and ib_read_lat.
	* Write - ib_write_bw, ib_write_bw_postlist and ib_write_lat.
	* Send  - ib_send_bw and ib_send_lat.
	* RDMA  - rdma_bw and rdma_lat.
	* Additional benchmark:   ib_clock_test.

Please post results/observations/bugs/remarks to the mailing list specified below:
	* Maintainer - idos@dev.mellanox.co.il
	* OFED mailing list - ewg@lists.openfabrics.org 
	  or linux-rdma@vger.kernel.org 
	* http://openib.org/mailman/listinfo/openib-general

===============================================================================
2. Notes on Testing Methodology
===============================================================================
The bencmarks specified below are tested of the following architectures:	
- i686 
- x86_64
- ia64

- The benchmark uses the CPU cycle counter to get time stamps without context
  switch. Some CPU architectures (e.g., Intel's 80486 or older PPC) do NOT
  have such capability.

- The benchmark measures round-trip time but reports half of that as one-way
  latency. Thus, it may not be sufficiently accurate for asymmetrical
  configurations.

- On BW benchmarks , the BW is calculated on the send side only, as it calculates
  the BW after collecting completion from the receive side.
  If using the bidirectional flag , BW is calculated on both sides 

- Min/Median/Max result is reported.
  The median (vs average) is less sensitive to extreme scores.
  Typically, the "Max" value is the first value measured.

- Larger samples help marginally only. The default (1000) is sufficient.
  Note that an array of cycles_t (typically unsigned long) is allocated
  once to collect samples and again to store the difference between them.
  Large sample sizes (e.g., 1 million) might expose other problems
  with the program.

- The "-H" option will dump the histogram for additional statistical analysis.
  See xgraph, ygraph, r-base (http://www.r-project.org/), pspp, or other 
  statistical math programs.

===============================================================================
4. Test Descriptions
===============================================================================

rdma_lat.c 	latency test with RDMA write transactions
rdma_bw.c 	streaming BW test with RDMA write transactions


The following tests are mainly useful for HW/SW benchmarking.
They are not intended as actual usage examples.

send_lat.c 	latency test with send transactions
send_bw.c 	BW test with send transactions
write_lat.c latency test with RDMA write transactions
write_bw.c 	BW test with RDMA write transactions
read_lat.c 	latency test with RDMA read transactions
read_bw.c 	BW test with RDMA read transactions

The executable name of each test starts with the general prefix "ib_",
e.g., ib_write_lat, except for those of RDMA tests, 
their excutable have the same name except of the .c.

Running Tests
-------------

Prerequisites: 
	kernel 2.6
	ib_uverbs (kernel module) matches libibverbs
		("match" means binary compatible, but ideally of the same SVN rev)

Server:		./<test name> <options>
Client:		./<test name> <options> <server IP address>

		o  <server address> is IPv4 or IPv6 address. You can use the IPoIB
                   address if IPoIB is configured.
		o  --help lists the available <options>

  *** IMPORTANT NOTE: The SAME OPTIONS must be passed to both server and client.


Common Options to all tests:
  -p, --port=<port>            Listen on/connect to port <port> (default: 18515).
  -m, --mtu=<mtu>              Mtu size (default: 1024).
  -d, --ib-dev=<dev>           Use IB device <dev> (default: first device found).
  -i, --ib-port=<port>         Use port <port> of IB device (default: 1).
  -o, --out=<num_of_out>       Number of outstanding reads. only in READ.
  -q, --qp=<num_of_qps>        Number of Qps to perform. only in write_bw.
  -c, --connection=<c>         Connection type : RC,UC,UD according to spec.
  -g, --mcg=<num_of_qps>       Number of Qps in MultiCast group. in SEND only
  -M, --MGID=<addr>	       <addr> as the group MGID in format '255:1:X:X:X:X:X:X:X:X:X:X:X:X:X:X'.
  -s, --size=<size>            Size of message to exchange (default: 1).
  -a, --all                    Run sizes from 2 till 2^23.
  -t, --tx-depth=<dep>         Size of tx queue (default: 50).
  -r, --rx-depth=<dep>         Make rx queue bigger than tx (default 600).
  -n, --iters=<iters>          Number of exchanges (at least 100, default: 1000).
  -I, --inline_size=<size>     Max size of message to be sent in inline mode.
			       On Bw tests default is  1,latency tests is 400.
  -C, --report-cycles          Report times in cpu cycle units.
  -u, --qp-timeout=<timeout>   QP timeout, timeout value is 4 usec*2 ^(timeout).
			       Default is 14.
  -S, --sl=<sl>                SL (default 0).
  -H, --report-histogram       Print out all results (Default: summary only).
			       Only on Latnecy tests.
  -x, --gid-index=<index>      Test uses GID with GID index taken from command
			       Line (for RDMAoE index should be 0). 
  -b, --bidirectional          Measure bidirectional bandwidth (default uni).
  			       On BW tests only (Implicit on latency tests).	
  -V, --version                Display version number.
  -e, --events                 Sleep on CQ events (default poll).
  -N, --no peak-bw             Cancel peak-bw calculation (default with peak-bw)
  -F, --CPU-freq               Do not fail even if cpufreq_ondemand module.

  *** IMPORTANT NOTE: You need to be running a Subnet Manager on the switch or
		      on one of the nodes in your fabric.



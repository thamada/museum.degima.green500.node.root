# museum.degima.green500.node.root
Historical data for DEGIMA GREEN500(Jun/Nov 2011): the storage data for linpack nodes on DEGIMA.

## ChangeLog

2011-10-24  root  <root@g248>

	* Backup: img.007

	* Modify: /etc/sysconfig/network-scripts/ifcfg-eth0
	  - NM_CONTROLLED: yes -> no
	  - NETMASK: 255.255.255.0 -> 255.0.0.0
	  - #PREFIX: 24 -> comment out

	* Modify: /etc/rc5.d/
	  - chkconfig NetworkManager off
	  - chkconfig network on

2011-10-22  root  <root@g248>

	* Modify: /root/.ssh/known_hosts

	* Modify: Network
	  192.168.1.0/24 -> 10.0.0.0/8
	  - /etc/sysconfig/network
	  - /etc/sysconfig/network-scripts/ifcfg-eth0
	  - /etc/hosts

2011-10-21  root  <root@localhost.localdomain>

	* Backup: img.006

	* useradd bude07

2011-05-24  root  <root@g01>

	* Modify: /etc/security/limits.conf
	    *		soft	nproc	40000
	    *		hard	nproc	80000
	    *		soft	nofile	40000
	    *		hard	nofile	80000

2011-05-19  root  <root@localhost.localdomain>

	* Backup: img.005

	* Modify: /etc/fstab

	#nfs:/export/home/green/home	  /home	 	nfs	auto,hard,intr    1 1
	#nfs:/export/home/green/export	  /export	nfs	auto,hard,intr    1 1

	nfs2:/export/home/green/home	  /home	 	nfs	auto,hard,intr    1 1
	nfs2:/export/home/green/export	  /export	nfs	auto,hard,intr    1 1


2011-05-11  root  <root@copy01>

	* Backup: img.004

2011-05-09  root  <root@g01>
	* Modify: /etc/security/limits.conf
	  *     soft    stack   131072
	  *     hard    stack   131072

2011-05-02  root  <root@g01>

	* Modify: /etc/gdm/Init/Default
	   xhost +
	   chmod uog+rw /dev/ati/card*

2011-04-30  root  <root@g222>

	* Backup: img.003

	* Modify: /root/.ssh

	* Install: AMD driver 11.3 (downgrade)

2011-04-29  root  <root@g222>

	* Backup: img.002

	* Add: users
	  - /root/sync/Makefile

	* Add: ssh-keygen -t rsa on root

	* Modify: /etc/hosts

	* Modify: /etc/hosts

	* Modify: /etc/fstab (auto !! not noauto !!)
	  192.168.1.4:/home/green/home	 /home	 nfs	auto,hard,intr    1 1
	  192.168.1.4:/home/green/export /export nfs	auto,hard,intr    1 1

	* Backup: img.001

	* Install: for OFED requirement
	  - yum install tcl-devel tk-devel tcsh glibc-static.x86_64

	* Add: /opt/green
	  - mkdir /opt/green
	  - chown -R hamada.vip /opt/green

	* Install: memtest86+
	  - yum install memtest86+.x86_64

	* Add: /etc/ld.so.conf.d/hamada.conf
	  - ldconf
	  - ldconf -p |grep mpi

	* modify:modify: /etc/security/limits.conf
          - *    soft    memlock         unlimited
	  - *    hard    memlock         unlimited

	* modify: network config

	* modify: /etc/fstab

	* Install: AMD GPU driver
	  - ati-driver-installer-11-4-x86.x86_64.run

	* Backup: img.000


visudo 
cd /etc/
exit
ls
ll
ls -la
df -h /
uname -a
gcc --version
ls
ll
cd /etc/
emacs -nw passwd
er
cd /home/
ls
ll
chown -R hamada.600 hamada
ls -la
cd hamada/
ls -la .gvfs 
ls -la 
cd
groupadd -g 600 vip
ls
ls -la
cd /home/
ls -la
cat /etc/group
cd /etc/rc5.d/
ls
ll
ll |grep S
mv S02lvm2-monitor  K02lvm2-monitor 
mv S08ip6tables K08ip6tables 
mv S08iptables K08iptables 
mv S11auditd K11auditd 
mv S15mdmonitor  K15mdmonitor 
mv S24avahi-daemon  K24avahi-daemon 
mv S25cups  K25cups 
mv S26pcscd  K26pcscd 
mv S50bluetooth  K50bluetooth 
mv S80sendmail  K80sendmail 
mv S85gpm  K85gpm 
mv S95atd  K95atd 
mv S90crond  K90crond 
ls |grep  S
mv S12rsyslog  K12rsyslog 
ll
ls
shutdown -r now
halt
reboot
ls
cd /etc/
l 
ls
cd 
ls
mkdir /export
cd /
ls
mount -t nfs 192.168.1.4:/home/green/export export
ifconfig 
ping 192.168.1.4
ping 192.168.1.1
ping 192.168.1.4
cd
system-config-network
cd
df
mount -t nfs 192.168.1.4:/home/greep/export  /export/
ssh 192.168.1.4
ping 192.168.1.4
cd /etc/
l fstab 
emacs -nw fstab 
mount /export
df
cd /export/
ls
cd tmp/
ls
cd /etc/
l fstab
emacs -nw fstab
er
mount /home/
ls
er
ls
df
su - hamada
ls
cd /
ls
ntpdate ntp.nict.jp
hwclock --systohc
ls
cd etc
ls
cd init.d/
ls
cp ntpd hamada
ll
ll hamada 
l hamada 
emacs -nw hamada 
ls /tmp/
rm -r /tmp/*
rm -fr /tmp/*
ls /tmp/
la /tmp/
ls -a /tmp/
ls
mount /export
cd /export/
ls
cd /etc/rc5.d/
ls
ll
ln -s ../init.d/hamada ./S99hamada
ls
ll
./S99hamada 
l /etc/init.d/ha
l /etc/init.d/hamada
emacs -nw /etc/init.d/hamada
./S99hamada 
df
er
ls
system-config-network
runlevel 
cd /etc/rc5.d/
ls
ls |grep S
./S99hamada 
df
su - hamada
cd /export/opt/
ls
cd src/
ls
cd amdstream-v2.3/
ls
./ati-driver-installer-11-4-x86.x86_64.run 
ls
halt
mount /export
ls
cd /export/opt/src/
ls
cd amdstream-v2.3/
ls
./ati-driver-installer-11-4-x86.x86_64.run 
cat /etc/X11/xorg.conf
cd /etc/X11/
cp xorg.conf xorg.conf.0
aticonfig --initial
diff xorg.conf xorg.conf.0 
ll
rm xorg.conf.0 
emacs -nw xorg.conf
cp xorg.conf xorg.conf.0
fg
er
df
passwd 
exit
which ether-wake 
ls
l ChangeLog
emacs -nw ChangeLog
fg
er
ls
yum search kernel
cat /boot/grub/menu.lst 
yum search memtest
yum install memtest86+.x86_64
cat /boot/grub/menu.lst 
man memtest-setup 
memtest-setup  --help
cat /boot/grub/menu.lst 
ls
yum search ofed
yum search InfiniBand
ll
er
ls
ll
cd
ls
cp .bash_profile .bash_profile.0
cp .bashrc .bashrc.0
df
mount /export/
cp /export/tmp/ubuntu.etc/bashrc.root ./.bashrc
source .bashrc
err
ls
cat .bashrc
mkdir /opt/green
chown -R hamada.vip /opt/green
ls
er
rm .bash_profile
ln -s .bashrc .bash_profile
ls -la
source .bashrc
ll
l ChangeLog 
er
ls
er
ls
halt
cd /etc/
cd security/
ls
emacs -nw limits.conf 
er
pwd
cd ..
cd ld.so.conf.d/
ls
cat >hamada.conf
ll
cat qt-x86_64.conf 
cat xulrunner-64.conf 
cat ../ld.so.conf
ll
emacs -nw hamada.conf 
er
cd ..
cd sysconfig/
ls
cat network
cd network-scripts/
ls
l ifcfg-eth0 
emacs -nw ifcfg-eth0 
er
ls
/etc/init.d/network restart
df -h .
er
ls
ifconfig 
ping www.google.com
er
ls
yum check-update
yum -h
yum check
uname 
uname  -a
cd 
ls
l ChangeLog
emacs -nw ChangeLog
ll
cd /
ls
df
cd /etc/
ls
cd init.d/
ls
er
ls
./hamada 
cd ..
cat rc.local 
ls /var/lock/subsys/local 
ls -la /var/lock/subsys/local 
date
last -20
ls
cd udev/rules.d/
ls
l 70-persistent-net.rules 
er
ls
shutdown -h now
mount /home
mount /export
exit
ls
rsync -av /export/opt/src/OFED-1.5.3.1.tgz .
ls
tar xzvf OFED-1.5.3.1.tgz 
cd OFED-1.5.3.1
ls
./install.pl 
yum search rpm
ls
rm ofed.conf 
ll /tmp/
./install.pl 
ls
time ./install.pl 
cd /etc/rc5.d/
ls
ls |grep opensm
exit
yum install tcl-devel
yum install  tk-devel
yum install  tcsh
yum search glibc-static
yum install  glibc-static.x86_64
ls
ll
ls
ll
cd /etc/
l rc.local 
er
ls
cd rc5.d/
ls
rm S99hamada 
cat S99local 
ll
l S99local 
er
ls
l S99local 
which mount
fg
er
ls
shutdown -r now
ls
l ChangeLog 
ls
er
ls
cd /etc/udev/rules.d/
ls
cat 70-persistent-net.rules 
l 70-persistent-net.rules 
df
mount -a
df
cd /etc/
l fstab 
mount -a
df
mount -a
fg
mount -a
df
mout 
mount /home/
ifconfig 
/etc/init.d/network restart
ifconfig 
mount -a
df
cat fstab
ping 192.168.1.4
mount -a
df
mount /export
df
mount -a
df
umount /export
l fstab
mount -a
df
fg
df
mount -a
df
fg
er
ls
ifconfig 
shutdown -r now
cd /etc/sysconfig/
ls
cd network-scripts/
ls
mv ifcfg-ib0 /root/
/etc/init.d/network stop
ifconfig 
shutdown -r now
cd /etc/sysconfig/
ls
cd network
cat network
cd network-scripts/
ls
cat ifcfg-eth0
cat ifcfg-ib0 
l ifcfg-eth0
fg
cd /etc/
cd rc5.d/
ls
ll |grep rpcbind
ll |grep nfslock
ll |grep netfs
cd /etc/
l fstab 
chkconfig nfslock on
chkconfig rpcbind on
chkconfig netfs on
ls
df - h
df -h
ls
cd rc5.d/
ls
l S99local 
er
mount -a
df
umount /export/
mount -a
df
reboot
/etc/init.d/network restart
ifconfig 
mount -a
df
ls
cd OFED-1.5.3.1
ls
mpirun -n 2 /usr/mpi/gcc/openmpi-1.4.3/tests/osu_benchmarks-3.1.1/osu_bibw 
ls
ll
er
ls
cd ..
ls
mount /home/
ls
mount /export
su - hamada
ls
ifconfig 
cat /etc/resolv.conf 
netstat -rn
cd /etc/
l rc.local 
reboot
runlevel 
cd /etc/rc5.d/
ll
cat S99local 
l S99local 
er
ls /tmp/
./S99local 
cat /tmp/xxx 
l S99local 
./S99local 
df
fg
./S99local 
fg
er
ls
df
./S99local 
pint ntp.nict.jp
ping ntp.nict.jp
df
ll
df
l S99local 
er
ls
/etc/rc.local 
reboot
mount -a
df
ll
cd /etc/rc5.d/
ls
ll
df
ll
df
ls
ll
er
ls
ll
cat S99local 
./S99local 
chkconfig --list local 
chkconfig --list ssh
chkconfig --list
chkconfig --list|grep local
chkconfig --list|grep ssh
chkconfig --list|grep sendmail
chkconfig sendmail off
chkconfig --list|grep opensm
chkconfig --list|grep openib
ls
ll
cd /etc/
cat rc.local 
ll /var/lock/subsys/
ll /var/lock/subsys/ll
cd /etc/ls
ll
ls
ll
ls
ll
ls
mount /home
df
exit
shutdown -h now
cd /etc/
l fstab
er
ls
l rc.local 
er
ls
cd init.d/
ls
l hamada 
er
ls
ifconfig 
ls
er
ls
cd ..
ls
cd rc5.d/
ls
ln -s ../init.d/S99hamada
cat S99
cat S99hamada 
mv S99hamada S98hamada
ls
rm S98hamada 
ln -s ../init.d/hamada S98hamada
cat S98hamada 
ls
reboot
cd 
ls
l ChangeLog 
er
ls
er
ls
cd /etc/udev/rules.d/
ls
l 70-persistent-net.rules
er
ls
cd /etc/
ls
l fstab 
er
ls
cat hosts
l hosts
er
cd 
l ChangeLog 
er
ls
cd /etc/sysconfig/
ls
cd network-scripts/
ls
cat ifcfg-eth0
er
l ifcfg-eth0 
er
ls
halt
cd
l ChangeLog 
er
ls
cd sync/
ls
ll
m.do uptime ./hosts 
ll
er
ls
cd
ls
cd .ssh/
ls
mv /export/opt/genhost.pl .
l genhost.pl 
./genhost.pl 
fg
er
./genhost.pl 
./genhost.pl  >authorized_keys2 
ssh g222
ls
ls /export/opt/src/
rm -r OFED-1.5.3.1
rm -r OFED-1.5.3.1.tgz 
ls
ll
cd sync/
ls
cat Makefile 
mkae user
l hosts 
make user
ls /home/
su - egami
ls
ll
er
ls
/etc/init.d/opensmd status
/etc/init.d/opensmd start
/etc/init.d/opensmd stop
/etc/init.d/opensmd status
ls
cd ..
ls
ll
l ChangeLog 
er
ls
halt
ls
df
mv /export/opt/src/sync .
cd sync/
ls
cat hosts 
ghost 222 222 4 >hosts 
m.do uptime ./hosts 
ssh g222
cd
ssh-keygen -t rsa
cd .ssh/
ls
cat id_rsa.pub >authorized_keys2
ssh g222
ls
ll
df -h .
ls
df
ls
ll
cd sync/
ls
cd ..
ls
halt
cd img.002.20110429/
ls
ls -la
du -sh .
ls -la
ls -lah
ifconfig 
ls -lah
ls -la
watch ls -la
ls
ll
history 
ifconfig 
rsync -av hamada@192.168.1.4:img.002* .
ifconfig 
rsync -av hamada@192.168.1.4:img.002* .
ls
cd img.002.20110429/
ls
ls -1 HDD-* >tmp.sh
l tmp.sh 
er
ls
chmod 755 tmp.sh 
time ./tmp.sh 
halt
exit
cd /etc/
cd
ls
rsync -av hamada@gpu.progrape.jp:/home/green/export/opt/xxx.tar .
ll
tar xvf xxx.tar 
rm xxx.tar 
ls
cd .ssh/
ls
cat authorized_keys2 
cat id_rsa.pub 
fg
l authorized_keys2 
ssh g222
ls
ll
er
cat known_hosts 
ls
cd
ls
l ChangeLog 
df
ls
ll
er
ls
ll
cd /tmp/
ls
ls -la
rm -r virtual-hamada.*
ls
du -sh .
rm -rf OFED.*
ls
rm -r *
la
ll
rm -r .esd-500 .ICE-unix .X0-lock .X11-unix
ls
la
cd /opt/
ls
cd green/
ls
cd ..
df -h .
cd
ls
cd /var/tmp/
du -sh .
ls
cd 
cd /
du -sh *
cd usr/
ls
cd 
ls
cd /etc/
cd udev/rules.d/
ls
l 70-persistent-net.rules 
er
ls
halt
ifconfig 
ls
cd img.002.20110429/
ls
ls /dev/sd*
ll /dev/sd*
cat tmp.sh 
df
time ./tmp.sh 
ls
cd ..
ls
rm -r img.002.20110429
df -h .
ls
cd /etc/sysconfig/
cat network
visudo 
ls
cd network-scripts/
l ifcfg-eth0 
er
ls
er
ls
cat /root/ifcfg-ib0 
df
mount -a
ifconfig 
l ifcfg-eth0 
er
ls
ifconfig 
mount /export/
fg
l ifcfg-eth0 
er
ls
mount 192.168.1.4:/home/green/export /export
cd /export/opt/
ls
cd src/amdstream-v2.3/
ls
chmod 644 ati-driver-installer-11-4-x86.x86_64.run 
chmod 755 ati-driver-installer-11-3-x86.x86_64.run 
./ati-driver-installer-11-3-x86.x86_64.run 
rsync -av  ati-driver-installer-11-3-x86.x86_64.run /root/
cd /root/
sl
./ati-driver-installer-11-3-x86.x86_64.run 
cd /etc/sysconfig/network-scripts/
l ifcfg-eth0 
ls
cd change.host
ls
ll
cd sync/
ll
cat Makefile 
diff ../ifcfg-eth0 .
cat ifcfg-eth0 
cat ../ifcfg-eth0 
exit
cd 
ls
cat ChangeLog 
exit
reboot
su - fcruz
exit
time mkswap /SWAP 
time md5sum --check /home/hamada/md5.txt 
free
free -m
swapon /SWAP 
free -m
swapoff /SWAP 
free -m
exit
ssh g01
exit
cat /proc/cpuinfo 
cat /proc/cpuinfo  |grep MHz
ochiro 
cpuspeed_max
grep MHz /proc/cpuinfo 
ghost 2 144 >/tmp/xxx
m.do '/export/opt/bin/cpuspeed_max' /tmp/xxx 
m.do 'cat /proc/cpuinfo |grep MHz|tail -1' /tmp/xxx 
exit
shutdown -r now
ping 192.168.1.249
cat /etc/hosts
cd .ssh/
ls
cat known_hosts 
ls
exit
cd /etc/
l osts
l hosts
er
less host
less hosts
ping g02
er
ls
reboot
cd /
ls
rsync -av g01:/swapfile.1 /
ll
la
md5sum swapfile.1 
exit
ls
ll
cp /home/hamada/hosts .
l hosts 
er
ls
bcast.pl 'rsync -av g02:/swapfile.1 /' ./hosts 
ghost 218 223 >hosts 
time m.do 'rsync -av g02:/swapfile.1 /' ./hosts 
cp /home/hamada/hosts .
l hosts 
ls
bcast.pl 'ls -l /swapfile.1 ' /home/hamada/hosts
m.uptime ./hosts 
ping g228
ping g233
bcast.pl 'ls -l /.swap ' /home/hamada/hosts
bcast.pl 'ls -l /swapfile.1 ' /home/hamada/hosts
ls
wc -l hosts 
m.do 'md5sum /swapfile.1 ' ./hosts |sort
cat >md5sum.txt
grep 5ccdb023866 md5sum.txt 
grep -v 5ccdb023866 md5sum.txt  
m.do 'md5sum /swapfile.1 ' ./hosts |sort >md5sum.txt2
l md5sum.txt
grep -v 5ccdb023866 md5sum.txt
grep -v 5ccdb023866 md5sum.txt2 
l md5sum.txt2 
ls
m.do 'md5sum /swapfile.1 ' ./hosts |sort |tee md5sum.txt2
grep -v 5ccdb md5sum.txt2 
rm hosts 
exit
cd /etc/
ls
cd security/
ls
l limits.conf
er
reboot
ls
exit
hdparm -t /dev/sda
md5sum /swapfile.1 
ls -la
ls -lah /
exit
ssh g119
ssh g118
ssh g03
exit
yum search bash4
yum provides bash4
yum provides *bin/bash4
yum search bash4
yum search bash3
yum search bash5
cd /var/log/
last -20
ll
cat /etc/logrotate.conf 
cd /etc/
ll
ls
cat logrotate.d/
ls
cd logrotate.d/
ls
ll
cat syslog 
cd ..
ls
cat logrotate.conf 
ll /var/log/
/usr/sbin/logrotate -f /etc/logrotate.conf
ll /var/log/
last -20
cd
ls /var/log/*-20110530
ls -la /var/log/*-20110530
rm  /var/log/*-20110530
cp /home/hamada/hosts .
l hosts 
m.uptime hosts
er
sleeping ./hosts 
l hosts 
bcast.pl '/usr/sbin/logrotate -f /etc/logrotate.conf' ./hosts 
bcast.pl 'rm  /var/log/*-20110530' ./hosts 
jobs
reboot
su - purple
exit
shutdown -r now
killall xhpl
top
exit
reboot
su - aniki
ls
cd sync/
ls
cd ..
ls
ping g01
exit
which ruby
exit
ls
grep g01 WOL/Makefile
sudo ether-wake f4:6d:04:08:40:14 ; sleep2
sudo ether-wake f4:6d:04:08:40:14 ; sleep2 ${WAIT}; # g01 -
cd WOL/Makefile
cd WOL/
ls
l Makefile
sudo ether-wake f4:6d:04:08:40:14 ; sleep2
ssh g113
cd /tmp/
ls
ls -la
ghost 1 144 >xxx
m.uptime ./xxx 
l xxx
m.do 'rm /tmp/aho ' ./xxx
df
cat /etc/fstab 
ls /
ls -la /
m.do 'rm /tmp/aho ' ./xxx
ls -la
m.do 'sync' ./xxx
ls -la
m.do 'rm /tmp/file*' ./xxx
df -h .
ll
m.do 'rm /tmp/file*' ./xxx
ls -la
m.do 'ls -la /tmp/|grep ega' ./xxx 
l xxx 
er
ls
l xxx 
er
ls
ll
m.reboot ./xxx 
ls
w
last -20 -a
reboot
cd /tmp/
ls
cat xxx 
m.uptime ./xxx 
ping g138
rade.check 
rade.safe 
rade.check 
bcast.pl rade.safe ./xxx 
which rade.sa
which rade.safe
bcast.pl /export/opt/bin/rade.safe  ./xxx 
su - hamada
chown hamada.100 xxx
exit
/etc/init.d/opensmd status
/etc/init.d/opensmd start
uptime 
exit
rm -r openmpi-sessions-*
bcast.pl 'rm -r /tmp/openmpi-sessions-*' ./xxx 
bcast.pl 'rm -r /tmp/virtual*' ./xxx 
bcast.pl 'rm -r /tmp/file*' ./xxx 
ls
ll
l xxx 
ghost 33 144 >yyy
m.uptime ./yyy 
ping g49
ghost 3 144 > yyy
ping g49
ghost 3 144 >yyy
bcast.pl uptime ./yyy 
ghost 3 144 >yyy
l yyy 
less yyy 
less xxx 
less yyy 
m.halt ./xxx 
ls
er
ls
suu -
rade.check 
ll
ls
cat /proc/cpuinfo 
exit
ls
cd /tmp/
m.uptime ./xxx
ping g10
m.uptime ./xxx >/dev/null 
m.uptime ./xxx >/dev/null  |sort
ping g104
ping g140
ping g104
m.uptime ./xxx >/dev/null  |sort
ssh g101
ls
m.uptime ./xxx >/dev/null  |sort
ping g96
m.uptime ./xxx >/dev/null  |sort
ping g138
su - hamada
l xxx 
er
ls
ping g138
ssh g138
l xxx 
er
su - hamada
exit
cd /tmp/
la
exit
cd /tmp/
ls
ll
ls
ll
ls
ll
rm xxx yyy 
ls
ll
ls
df -h .
du -sh .
ll
cd ..
ls
ls -la 
cat /etc/fstab 
du -sh .
df -h .
ls
ls -la
ll
ls -lah
ll
ls -alh .
df -h .
w
shutdown -h now
exit
ls
cd /etc/sysconfig/network-scripts/
l ifcfg-eth0 
netstat -rn
ls
l ifcfg-eth0 
er
ls
cd /etc/
cat fstab 
ping nfs2
mount /home/
mount /export
exit
/etc/init.d/network restart
ifconfig 
cd /etc/
ls
cd udev/
ls
cd rules.d/
ls
cat 70-persistent-net.rules 
l 70-persistent-net.rules 
er
ls
ll
cd /etc/sysconfig/network-scripts/
l ifcfg-eth0 
er
ls
reboot
ls
l ChangeLog 
er
ls
ll
er
ls
cd /etc/udev/rules.d/
ls
l 70-persistent-net.rules 
er
ls
ll
ping www.asahi.com
host www.asahi.com
host cv1.progrape.jp
ls
ll
cd
ls
shutdown -h now
cd /etc/udev/rules.d/
ls
l 70-persistent-
l 70-persistent-net.rules 
er
ls
cd /r
cd
ls
cd .ssh/
l known_hosts 
er
cd /etc/
er
cd
ssh nfs
er
ssh nfs2
cd .ssh/
l known_hosts 
er
ssh g02
er
cd
cd /etc/
er
ls
cd /etc/sysconfig/network-scripts/
er
cd ..
er
cd ..
ls
cat udev/rules.d/70-persistent-net.rules 
cd 
l ChangeLog 
er
ls
halt
er
ls
ls /etc/rc5.d/|grep Network
chkconfig /NetworkManager off
chkconfig NetworkManager off
ls /etc/rc5.d/|grep Network
echo 'chkconfig NetworkManager off' >xxx
chkconfig network on >>xxx 
l xxx 
echo 'chkconfig network on' >>xxx 
ls /etc/rc5.d/|grep network
l xxx 
er
ls
rm xxx 
ls
cd /home/hamada/
ls
cd change.host
ls
cd sync
ls
cat Makefile 
cp ifcfg-eth0 /tmp/
/etc/init.d/NetworkManager stop
/etc/init.d/network restart
ifconfig 
cd /tmp/
l ifcfg-eth0 
ifconfig 
fg
er
ls
cd /etc/sysconfig/network-scripts/
ls
er
ls
cat ifcfg-
cat ifcfg-eth0 
mv /tmp/ifcfg-eth0 .
cat ifcfg-eth0 
halt
cd /etc/udev/rules.d/
ls
l 70-persistent-
l 70-persistent-net.rules 
er
ls
cd /root/
ls
l ChangeLog 
er
ls
cat /etc/udev/rules.d/70-persistent-net.rules 
ping nfs2
halt
cp /media/26A1-5921/e1000e-1.11.3-1.x86_64.rpm .
umount /media/26A1-5921/
ls
rpm -ihv ./e1000e-1.11.3-1.x86_64.rpm 
cat /proc/cpuinfo |grep name
free -m
reboot
ochiro 

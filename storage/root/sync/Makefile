HOST_START = 1
HOST_END   = 156

mkhosts:
	ghost 1 $(HOST_END) >hosts


sync.ssh:
	bcast.pl 'rsync -av g01:/root/.ssh /root/' ./hosts

#	bcast.pl 'rsync -av g01:/usr/local/bin /usr/local/' ./hosts


#------------------------------------------------------------------------------------
#	ghost 16 17 >hosts
#	ghost 1 $(HOST_END) >hosts

user:
	@echo '----------------------------------------------------------------------'
	echo 'lkrzvoiMflaQj8slja0JJ' >  /home/hamada/tmp~
	echo 'lkrzvoiMflaQj8slja0JJ' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 600 -u 532 -d /home/fcruz -s /bin/bash -M fcruz' ./hosts
	bcast.pl 'passwd fcruz < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'lkrzvoeMflVQj8slja2KJ' >  /home/hamada/tmp~
	echo 'lkrzvoeMflVQj8slja2KJ' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 600 -u 512 -d /home/egami -s /bin/bash -M egami' ./hosts
	bcast.pl 'passwd egami < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'lkrzvoeMflaQj8slja2KJ' >  /home/hamada/tmp~
	echo 'lkrzvoeMflaQj8slja2KJ' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 600 -u 506 -d /home/nitadori -s /bin/bash -M nitadori' ./hosts
	bcast.pl 'passwd nitadori < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'xyxnklwe8923d89xhdzaf' >  /home/hamada/tmp~
	echo 'xyxnklwe8923d89xhdzaf' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 600 -u 523 -d /home/purple -s /bin/bash -M purple' ./hosts
	bcast.pl 'passwd purple < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'lkrzvdePflVQj8slja73J' >  /home/hamada/tmp~
	echo 'lkrzvdePflVQj8slja73J' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 100 -u 516 -d /home/egaburov -s /bin/bash -M egaburov' ./hosts
	bcast.pl 'passwd egaburov < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'lkrzvoeMflaQj8slja0KJ' >  /home/hamada/tmp~
	echo 'lkrzvoeMflaQj8slja0KJ' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 100 -u 519 -d /home/syoyo -s /bin/bash -M syoyo' ./hosts
	bcast.pl 'passwd syoyo < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'ykrzv2eMflVtj8slja2KJ' >  /home/hamada/tmp~
	echo 'ykrzv2eMflVtj8slja2KJ' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 600 -u 541 -d /home/shun -s /bin/bash -M shun' ./hosts
	bcast.pl 'passwd shun < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'Akrzv2pMflVsj5slMa2KJ' >  /home/hamada/tmp~
	echo 'Akrzv2pMflVsj5slMa2KJ' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 100 -u 510 -d /home/nushio -s /bin/bash -M nushio' ./hosts
	bcast.pl 'passwd nushio < /home/hamada/tmp~ ' ./hosts
	@echo '----------------------------------------------------------------------'
	echo 'rzvp2ptflpVjs5slaM2JK' >  /home/hamada/tmp~
	echo 'rzvp2ptflpVjs5slaM2JK' >> /home/hamada/tmp~
	bcast.pl 'useradd -g 100 -u 540 -d /home/okuyama -s /bin/bash -M okuyama' ./hosts
	bcast.pl 'passwd okuyama < /home/hamada/tmp~ ' ./hosts


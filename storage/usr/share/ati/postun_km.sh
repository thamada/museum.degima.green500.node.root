#!/bin/sh
DRV_RELEASE="8.831.2"

##############################################################
# COMMON HEADER: Initialize variables and declare subroutines

BackupInstPath()
{
    if [ ! -d /etc/ati ]
    then
        # /etc/ati is not a directory or doesn't exist so no backup is required
        return 0
    fi

    if [ -n "$1" ]
    then
        FILE_PREFIX=$1
    else
        # client did not pass in FILE_PREFIX parameter and /etc/ati exists
        return 64
    fi

    if [ ! -f /etc/ati/$FILE_PREFIX ]
    then
        return 0
    fi

    COUNTER=0

    ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
    RETURN_CODE=$?
    while [ 0 -eq $RETURN_CODE ]
    do
        COUNTER=$((${COUNTER}+1))
        ls /etc/ati/$FILE_PREFIX.backup-${COUNTER} > /dev/null 2>&1
        RETURN_CODE=$?
    done

    cp -p /etc/ati/$FILE_PREFIX /etc/ati/$FILE_PREFIX.backup-${COUNTER}

    RETURN_CODE=$?

    if [ 0 -ne $RETURN_CODE ]
    then
        # copy failed
        return 65
    fi

    return 0
}



UpdateInitramfs()
{
    UPDATE_INITRAMFS=`which update-initramfs 2> /dev/null`
    DRACUT=`which dracut 2> /dev/null`
    MKINITRD=`which mkinitrd 2> /dev/null`

    kernel_release=`uname -r`
    kernel_version=`echo $kernel_release | cut -d"." -f 1`
    kernel_major_rev=`echo $kernel_release | cut -d"." -f 2`
    kernel_minor_rev=`echo $kernel_release | cut -d"." -f 3 | cut -d"-" -f 1`

    if [ $kernel_version -ge 2 -a $kernel_major_rev -ge 6 -a $kernel_minor_rev -ge 32 ]; then

        if [ -n "${UPDATE_INITRAMFS}" -a -x "${UPDATE_INITRAMFS}" ]; then
            #update initramfs for current kernel by specifying kernel version
            ${UPDATE_INITRAMFS} -u -k `uname -r` > /dev/null 

            #update initramfs for latest kernel (default)
            ${UPDATE_INITRAMFS} -u > /dev/null
            
            echo "[Reboot] Kernel Module : update-initramfs" >> ${LOG_FILE} 
        elif [ -n "${DRACUT}" -a -x "${DRACUT}" ]; then
            #RedHat/Fedora
            ${DRACUT} -f > /dev/null            
            echo "[Reboot] Kernel Module : dracut" >> ${LOG_FILE}
             

        elif [ -n "${MKINITRD}" -a -x "${MKINITRD}" ]; then
            #Novell
            ${MKINITRD} > /dev/null
            
            echo "[Reboot] Kernel Module : mkinitrd" >> ${LOG_FILE}
            
        fi
    else
        echo "[Message] Kernel Module : update initramfs not required" >> ${LOG_FILE}
    fi

}



# i.e., lib for 32-bit and lib64 for 64-bit.
if [ `uname -m` = "x86_64" ];
then
  LIB=lib64
else
  LIB=lib
fi

# LIB32 always points to the 32-bit libraries (native in 32-bit,
# 32-on-64 in 64-bit) regardless of the system native bitwidth.
# Use lib32 and lib64; if lib32 doesn't exist assume lib is for lib32
if [ -d "/usr/lib32" ]; then
  LIB32=lib32
else
  LIB32=lib
fi

#process INSTALLPATH, if it's "/" then need to purge it
#SETUP_INSTALLPATH is a Loki Setup environment variable
INSTALLPATH=${SETUP_INSTALLPATH}
if [ "${INSTALLPATH}" = "/" ]
then
    INSTALLPATH=""
fi

# project name and derived defines
MODULE=fglrx
IP_LIB_PREFIX=lib${MODULE}_ip

# general purpose paths
XF_BIN=${INSTALLPATH}${ATI_X_BIN}
XF_LIB=${INSTALLPATH}${ATI_XLIB}
OS_MOD=${INSTALLPATH}`dirname ${ATI_KERN_MOD}`
USR_LIB=${INSTALLPATH}/usr/${LIB}
MODULE=`basename ${ATI_KERN_MOD}`

#FGLRX install log
LOG_PATH=${INSTALLPATH}${ATI_LOG}
LOG_FILE=${LOG_PATH}/fglrx-install.log
if [ ! -e ${LOG_PATH} ]
then
  mkdir -p ${LOG_PATH} 2>/dev/null 
fi
if [ ! -e ${LOG_FILE} ]
then
  touch ${LOG_FILE}
fi

#DKMS version
DKMS_VER=`dkms -V 2> /dev/null | cut -d " " -f2`

#DKMS expects kernel module sources to be placed under this directory
DKMS_KM_SOURCE=/usr/src/${MODULE}-${DRV_RELEASE}

# END OF COMMON HEADER
#######################

###Begin: postun_km ###
if [ -z ${DKMS_VER} ]; then
  # === kernel module ===
  # remove kernel module directory
  if [ -d ${OS_MOD}/${MODULE} ]; then

		# make sure we're not doing "rm -rf /"; that would be bad
		if [ -z "${OS_MOD}" -a -z "${MODULE}" ]
		then
			echo "Error: OS_MOD and MODULE are both empty in post_un.sh;" 1>&2
			echo "aborting rm operation to prevent unwanted data loss" 1>&2

			exit 1
		fi

    rm -R -f ${OS_MOD}/${MODULE}
  fi
  
  # remove kernel module from all existing kernel configurations
  KernelListFile=/usr/share/ati/KernelVersionList.txt             #File where kernel versions are saved
  if [ -f ${KernelListFile} ]
  then
       for multiKern in `cat ${KernelListFile}`
       do
           rm -f ${multiKern}/${MODULE}*.*o
       done
       rm -f ${KernelListFile}
  fi

  #refresh modules.dep to remove fglrx*.ko link from modules.dep
  /sbin/depmod
else
    dkms remove -m ${MODULE} -v ${DRV_RELEASE} --all --rpm_safe_upgrade > /dev/null
		
    if [ $? -gt 0 ]; then
        echo "Errors during DKMS module removal"
    fi

	# We shouldn't delete module sources from the source tree, because they may be
	# refered by DKMS for other kernels
	##!! However!  We can check status of the module, and if there are no refs, we can delete the source!
    # make sure we're not doing "rm -rf /"; that would be bad
    if [ "/" = "${DKMS_KM_SOURCE}" ]
    then
        echo "Error: DKMS_KM_SOURCE is / in post.sh; aborting rm operation" 1>&2
        echo "to prevent unwanted data loss" 1>&2
        exit 1
    fi

    dkms status -m ${MODULE} | grep -i "${MODULE}"
    if [ $? -ne 0 ];
    then
        rm -R -f ${DKMS_KM_SOURCE} 2> /dev/null        # Clean up contents
    fi

fi

#update the initramfs if applicable
UpdateInitramfs

# Remove fglrxbuild startup script in case it was never run or failed
FGLRXKO_SCRIPT_NAME="fglrxkobuild"
FGLRXKO_BUILD_SCRIPT="/etc/init.d/${FGLRXKO_SCRIPT_NAME}"

if [ -e /etc/insserv.conf ]; then
    #on SUSE based system, use insserv to create script startup links
    insserv -rf ${FGLRXKO_BUILD_SCRIPT} 2> /dev/null
fi

#must delete script after running insserv and must delete script before running update-rc
rm -f ${FGLRXKO_BUILD_SCRIPT} 2> /dev/null

UPDATE_RC_BIN=`which update-rc.d 2> /dev/null`
if [ $? -eq 0 ] && [ -x "${UPDATE_RC_BIN}" ]; then
    #on debian based system, use update-rc.d was used to create links
    update-rc.d -f ${FGLRXKO_SCRIPT_NAME} remove > /dev/null
fi

# for any links manually created, delete 
rm -f ${FGLRXKO_BUILD_SCRIPT} 2> /dev/null
rm -f /etc/rc[0-5].d/S[0-9][0-9]${FGLRXKO_SCRIPT_NAME} 2> /dev/null


###End: postun_km ###

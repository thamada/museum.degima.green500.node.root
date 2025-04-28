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

###Begin: postun_cp ###

  # remove links, icon, and localization files
  rm -f ${INSTALLPATH}${ATI_CP_LNK}/amdcccle.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_LNK}/amdccclesu.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_ICON}/ccc_large.xpm > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_I18N}/*.qm > /dev/null
  rmdir --ignore-fail-on-non-empty ${INSTALLPATH}${ATI_CP_I18N} 2>/dev/null
  rmdir --ignore-fail-on-non-empty ${INSTALLPATH}${ATI_LIB} 2>/dev/null

  # remove legacy links and icon for cccle, we should clean up any
  # old references if they are found.
  rm -f ${INSTALLPATH}${ATI_CP_KDE_LNK}/amdcccle.kdelnk > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_GNOME_LNK}/amdcccle.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_ICON}/ccc_small.xpm > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_KDE3_LNK}/amdcccle_kde3.desktop > /dev/null

  # remove legacy links and icon
  # Prior to 8.35 the control panel was called fireglcontrol*.  This app
  # is now obsolete and will no longer be built, but we should clean up any
  # old references if they are found.
  rm -f ${INSTALLPATH}${ATI_CP_KDE_LNK}/fireglcontrol.kdelnk > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_GNOME_LNK}/fireglcontrol.desktop > /dev/null
  rm -f ${INSTALLPATH}${ATI_ICON}/ati.xpm > /dev/null
  rm -f ${INSTALLPATH}${ATI_CP_KDE3_LNK}/fireglcontrol_kde3.desktop > /dev/null
  # remove legacy sources
  # Prior to 8.35 the control panel source code had to be included as it
  # used the open version of Qt.  amdcccle doesn't have this requirement so
  # source files are no longer shipped, but we should clean up any old
  # references if they are found.
  rm -f ${INSTALLPATH}${ATI_SRC}/fglrx_panel_sources.tgz > /dev/null

  #remove link created for PAM secured system
  rm -f /etc/pam.d/amdcccle-su > /dev/null

###End: postun_cp ###

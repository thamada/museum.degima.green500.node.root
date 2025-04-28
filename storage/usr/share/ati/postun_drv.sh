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

###Begin: postun_drv ###

  # determine which lib dirs are of relevance in current system
  /sbin/ldconfig -v -N -X 2>/dev/null | sed -e 's/ (.*)$//g' | sed -n -e '/^\/.*:$/s/:$//p' >libdirs.txt

  # remove all invalid paths to simplify the following code  
  # have a look for the XF86 lib dir at the same time
  found_xf86_libdir=0;
  echo -n >libdirs2.txt
  for libdir in `cat libdirs.txt`;
  do
    if [ -d $libdir ]
    then
      echo $libdir >>libdirs2.txt
    fi
  done

  # browse all dirs and cleanup existing libGL.so* symlinks
  for libdir in `cat libdirs2.txt`;
  do 
    for libfile in `ls -1 $libdir/libGL.so* 2>/dev/null`;
    do
      libname=`find $libfile -printf %f`
      # act on file, depending on its type
      if [ -h $libdir/$libname ]
      then
        # delete symlinks
        rm -f $libdir/$libname
      else
        if [ -f $libdir/$libname ]
        then
          # remove regular files
          rm -f $libdir/$libname
        else
          echo "WARNING: lib file $libdir/$libname"
          echo "is of unknown type and therefore not handled."
        fi
      fi
    done
  done

  # Step 2: restore any "libGL.so*" from XFree86
  # - zero sized files will finally get deleted
  for libdir in `cat libdirs2.txt`;
  do
    for libfile in `ls -1 $libdir/FGL.renamed.libGL.so* 2>/dev/null`;
    do
      libname=`find $libfile -printf %f`
      origlibfile=`echo $libdir/$libname | sed -n -e 's/FGL\.renamed\.//p'`
      origlibname=`echo $libname | sed -n -e 's/FGL\.renamed\.//p'`
      mv $libdir/$libname $libdir/$origlibname
      if [ ! -s $libdir/$origlibname ]
      then
        rm -f $libdir/$origlibname
      fi
    done
  done

  # Step 3: rebuild any library symlinks
  /sbin/ldconfig

  # Ensures correct install of libGL.so symlink
  libdir=`cat /usr/share/ati/libGLdir.txt`
  ln -s $libdir/libGL.so.1 $libdir/libGL.so
  rm /usr/share/ati/libGLdir.txt

  # cleanup helper files
  rm -f libdirs.txt libdirs2.txt

  # Step X: backup current xconf & restore last .original backup
  OLD_DIR=`pwd`
  cd ${INSTALLPATH}/etc/X11/
  xconf_list="XF86Config
XF86Config-4
xorg.conf"

  for xconf in ${xconf_list}; do
  if [ -f ${xconf} ]; then
    count=0
    #backup last xconf
    #assume the current xconf has fglrx, backup to <xconf>.fglrx-<#>
    while [ -f "${xconf}.fglrx-${count}" ]; do
        count=$(( ${count} + 1 ))
    done
    cp "${xconf}" "${xconf}.fglrx-${count}"

    #now restore the last saved non-fglrx
    count=0
    while [ -f "${xconf}.original-${count}" ]; do
       count=$(( ${count} + 1 ))
    done
    if [ ${count} -ne 0 ]; then
      #check if xorg.conf was created by aticonfig because no xorg.conf existed
      #do not restore the xorg.conf file it the file begins with # NOXORGCONFEXISTED
      xorg_chk=`head -n 1 < "${xconf}.original-$(( ${count} - 1 ))" | grep '^# NOXORGCONFEXISTED'`
      if [ -n "${xorg_chk}" ]; then
         #delete the xorg.conf file
         rm -f "${xconf}"
      else
         #restore the xorg.conf file
         cp -f "${xconf}.original-$(( ${count} - 1 ))" "${xconf}"
      fi

    fi
  fi
  done

  cd ${OLD_DIR}

  # Remove ATI_PROFILE script (from post.sh)
  ATI_PROFILE_FNAME="ati-fglrx"
  PROFILE_COMMENT=" # Do not modify - set by ATI FGLRX"
  PROFILE_LINE="\. /etc/ati/${ATI_PROFILE_FNAME}\.sh ${PROFILE_COMMENT}"
  ATI_PROFILE_FILE1="/etc/profile.d/${ATI_PROFILE_FNAME}.sh"
  ATI_PROFILE_FILE2="/etc/ati/${ATI_PROFILE_FNAME}.sh"

  if [ -w "${ATI_PROFILE_FILE1}" ]; then
    rm -f "${ATI_PROFILE_FILE1}"

  elif [ -w "${ATI_PROFILE_FILE2}" ]; then
    rm -f "${ATI_PROFILE_FILE2}"

    PROFILE_TEMP=`mktemp -t profile_temp.XXXXXX`
    if [ $? -eq 0 ]; then
      # Match tempfile permissions with current profile
      chmod --reference=/etc/profile ${PROFILE_TEMP} 2>/dev/null
      grep -ve "${PROFILE_LINE}" /etc/profile 2>/dev/null > ${PROFILE_TEMP}
      if [ $? -eq 0 ]; then
        mv -f ${PROFILE_TEMP} /etc/profile 2>/dev/null
      fi
    fi

  fi

  #restore original libglx.so
  LIBGLX="libglx.so"

  if [ -f $ATI_XLIB_EXT_32/FGL.renamed.$LIBGLX ]; then
    rm $ATI_XLIB_EXT_32/$LIBGLX 2>/dev/null
    rm $ATI_XLIB_EXT_32/`echo $LIBGLX | sed -e s/libglx/libglx.fgl/g` 2>/dev/null
    mv $ATI_XLIB_EXT_32/FGL.renamed.$LIBGLX $ATI_XLIB_EXT_32/$LIBGLX 2>/dev/null
  fi

  if [ -f $ATI_XLIB_EXT_64/FGL.renamed.$LIBGLX ]; then
    rm $ATI_XLIB_EXT_64/$LIBGLX 2>/dev/null
    rm $ATI_XLIB_EXT_64/`echo $LIBGLX | sed -e s/libglx/libglx.fgl/g` 2>/dev/null
    mv $ATI_XLIB_EXT_64/FGL.renamed.$LIBGLX $ATI_XLIB_EXT_64/$LIBGLX 2>/dev/null
  fi

  # remove docs
  # make sure we're not doing "rm -rf /"; that would be bad
  if [ "${ATI_DOC}" = "/" ]
  then
    echo "Error: ATI_DOC is / in post_un.sh;" 1>&2
    echo "aborting rm operation to prevent unwanted data loss" 1>&2

    exit 1
  fi
  rm -rf ${ATI_DOC} 2>/dev/null

  echo "restore of system environment completed"

###End: postun_drv ###

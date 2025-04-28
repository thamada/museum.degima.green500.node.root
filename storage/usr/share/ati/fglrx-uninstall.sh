#!/bin/sh
# Copyright (c) 2011 Advanced Micro Devices, Inc.
#
#ATI fglrx driver uninstaller script
#Purpose : Uninstall previously installed ATI Linux Driver
#	  
#Location: It should reside under ${ATI_UNINST}
#Usage: 
#     - must be root to execute this script
#     - .list files must be present under the same directory
#     - preun/postun related scripts must be present under the same directory
#     - sh fglrx-uninstall.sh [Enter] 
#Warning: do not move this script and relevant files to other location

#check if root
if [ "`whoami`" != "root" ]; then
    echo "[Warning] ATI Catalyst(TM) Proprietary Driver Uninstall : must be run as root to execute this script"
    exit 1
fi

#create an uninstall log file
UNINSTALL_LOG=/etc/ati/fglrx-uninstall.log
if [ -f $UNINSTALL_LOG ]; then
   count=0
   #backup last log
   while [ -f "$UNINSTALL_LOG-${count}" ]; do
        count=$(( ${count} + 1 ))
    done
   mv "$UNINSTALL_LOG" "$UNINSTALL_LOG-${count}"
   
fi
echo "*** ATI Catalyst(TM) Proprietary Driver Uninstall Log `date +'%F %H:%M:%S'` ***" > ${UNINSTALL_LOG}

#move to where the script resides to find all the files to remove
cd `dirname $0`


#get parameters
useForce="N"
doDryRun="N"
uninstallResult=0
while [ "$*" != "" ]
do
  #Requested action
	action=$1

	case "${action}" in
	-h | --help)
		printHelp
		exit 0
		;;
	--dryrun)
      doDryRun=Y   	   
    	;;
	--force)
      useForce=Y
    	;;
	*|--*)
   	echo "${action}: unsupported option passed to ATI Catalyst(TM) Proprietary Driver Uninstall"
    	exit 1
    	;;
	esac
	shift
done


if [ "$doDryRun" = "Y" -a "$useForce" = "Y" ]; then
   echo "ATI Catalyst(TM) Proprietary Driver does not support"
   echo "--dryrun and --force commands together."
   echo "Please use --dryrun only for uninstall details."
   exit 1
elif [ "$doDryRun" = "Y" ]; then
   echo "Simulating uninstall of ATI Catalyst(TM) Proprietary Driver."
   echo "Dryrun only, uninstall is not done."
   echo "Dryrun only, uninstall is not done." >> ${UNINSTALL_LOG}
   
elif [ "$useForce" = "Y" ]; then
   echo "Forcing uninstall of ATI Catalyst(TM) Proprietary Driver."
   echo "No integrity verification is done." 
   echo "Forcing uninstall." >> ${UNINSTALL_LOG}
   
fi

#try to get the stored variable paths from the previous installation
if [ -f /etc/ati/inst_path_default -a -f /etc/ati/inst_path_override ]; then
   . /etc/ati/inst_path_default
   . /etc/ati/inst_path_override

else
   #support ${FORCE_ATI_UNINSTALL} for backwards compatiblity
   #but only advertise to use --force
   
    if [ -n "${FORCE_ATI_UNINSTALL}" -o $useForce = "Y" ]
    then
        if [ -d /usr/share/ati ]
        then
            SUFFIX=ati
        else
            SUFFIX=fglrx
        fi

        ATI_LOG=/usr/share/${SUFFIX}
        ATI_UNINST=/usr/share/${SUFFIX}
        ATI_DOC=/usr/share/doc/${SUFFIX}
        ATI_KERN_MOD=/lib/modules/fglrx
    else
        echo
        echo "[Warning] Uninstall : inst_path_default or inst_path_override"
        echo " does not exist in /etc/ati.  This suggests that the ATI driver"
        echo " is not installed, the ATI driver is only partially installed,"
        echo " or the current ATI driver installed is an older version than the"
        echo " one this script was designed for.  Both files listed above are"
        echo " required for determining where installed files are located."
        echo " To force uninstallation of the driver by guessing where the"
        echo " uninstallation files are located, set the force option"
        echo " re-run $0 (this is not recommended)."
        echo
        exit 1
    fi
fi

#check for the location where this script resides, in turn determine the INSTALLPATH
#(the root install dir where the driver components were installed)
CURRENT_DIR=`pwd`
#since we now are in the script directory, SCRIPT_SUBDIR is not really needed
SCRIPT_SUBDIR="."

PREUN_PATTERN="preun_*.sh"
POSTUN_PATTERN="postun_*.sh"
PREUN_SCRIPTLIST=`ls ${CURRENT_DIR}/${SCRIPT_SUBDIR}/${PREUN_PATTERN} 2>/dev/null`
POSTUN_SCRIPTLIST=`ls ${CURRENT_DIR}/${SCRIPT_SUBDIR}/${POSTUN_PATTERN} 2>/dev/null`
UNINSTALL_FILE_PATTERN="*.list"
UNINSTALL_FILELIST=`ls ${CURRENT_DIR}/${SCRIPT_SUBDIR}/${UNINSTALL_FILE_PATTERN} 2>/dev/null`


#verification step to make sure uninstall can be done successfully
MD5SUM_BIN=`which md5sum 2> /dev/null`
if [ $? -ne 0 ]; then
 echo "md5sum not on system" >> ${UNINSTALL_LOG}
fi

if [ "$useForce" = "N" ]; then

   #loop through .list files to verify the installed file's md5sum

   for uninstall_file in ${UNINSTALL_FILELIST}
	do
      	
      while read libfile 
      do 
                
         #split the md5sum and the file path      
         MD5SUM_RESULT=`echo ${libfile} | cut -d' ' -f1`
                
         if [ -n "${MD5SUM_RESULT}" -a "${MD5SUM_RESULT}" != "${libfile}" ]; then
            LIBFILE_PATH=`echo ${libfile} | sed -e 's/^'"${MD5SUM_RESULT}"\ '//'`
         else
            #there is no md5sum check for this file
            MD5SUM_RESULT=""
            LIBFILE_PATH=${libfile}
         fi        		

         if [  -e "${LIBFILE_PATH}" -o -L "${LIBFILE_PATH}" ]; then
            #verify the line begins with a md5sum and md5sum is on the system
            if [ -n "`echo $libfile | grep '^/'`" -o -z "$MD5SUM_BIN" ]; then

               #no install md5sum check value for file or system does not have md5sum
               #does not cause uninstall to fail verification
               echo "No md5sum install value for $libfile." >> ${UNINSTALL_LOG}
                
            else 
               result=`${MD5SUM_BIN} "${LIBFILE_PATH}" 2>> ${UNINSTALL_LOG}`
               new_MD5SUM_RESULT=`echo ${result} | cut -d' ' -f1`

               if [ "$new_MD5SUM_RESULT" != "${MD5SUM_RESULT}" ]; then
                  #md5sum check failed
                  echo "md5sum integrity check failed for ${LIBFILE_PATH}." >> ${UNINSTALL_LOG}
                  uninstallResult=1
               fi
            fi
        
         else
            #file does not exist
            if [ -n "${LIBFILE_PATH}" ]; then
               echo "File is missing from system ${LIBFILE_PATH}." >> ${UNINSTALL_LOG}
               uninstallResult=1
            fi
         fi
      done < ${uninstall_file}			
					
		
	done

   #special libGL check to verify if user has changed libGL since install
   libGL_file="${SETUP_INSTALLPATH}${ATI_XLIB}/libGL.so.1.2"

   #only do this check if the user has installed our driver
   #user may have done custom install without selecting driver
   if [ -f "${CURRENT_DIR}/${SCRIPT_SUBDIR}/drv.list" ]; then

      if [ -L "$libGL_file" -a -e "$libGL_file" ]; then
	   
         #file is a valid symlink, check that it points to either FGL.renamed* 
         #or a file in /fglrx/ folder
         link_result=`readlink -f $libGL_file`

         filename_check=`basename $link_result | grep '^FGL.renamed.libGL.so'`
      
         if [ -z "$filename_check" ]; then
            #symlink does not point to FGL.renamed
            #check if it is pointing to the installed libGL.so
            dirname_check=`echo $link_result | grep '/fglrx/libGL.so'`
      
            if [ -z "$dirname_check" ]; then
               #symlink does not point to a directory that we installed to
               #and does not point to the backed up file, FGL_Renamed
               #suspect libGL has been changed.
               echo "Symbolic link has been modified, $libGL_file, since last install." >> ${UNINSTALL_LOG}
               uninstallResult=1
            fi
            
         fi
      elif [ -e "$libGL_file"  ]; then
         echo "File has been modified, $libGL_file, since last install." >> ${UNINSTALL_LOG}
         uninstallResult=1     
      else
         #file is missing
         echo "File has been removed, $libGL_file, since last install." >> ${UNINSTALL_LOG}
         uninstallResult=1
      fi
   fi
fi



#Exit here if failed either md5sum check or libGL validation check
if [ $uninstallResult -eq 1 -a "$useForce" = "N" ]; then

      echo "One or more files have been altered since installation."
      echo "Uninstall will not be completed. See ${UNINSTALL_LOG} for details."

cat - >> ${UNINSTALL_LOG} << UNINSTALL_ERR_END
One or more files have been altered since installation.
Uninstall will not be completed.

To force uninstall, removing all installed files without verification,
run /usr/share/ati/amd-uninstall.sh --force.

Forcing uninstall is not recommended and may cause system corruption.

UNINSTALL_ERR_END

   if [ "$doDryRun" = "Y" ]; then
   
      echo "Dryrun completed with errors" >> ${UNINSTALL_LOG}
      echo "Dryrun uninstall of fglrx driver complete."
   
   fi
			
   exit 1 
fi

#assumption - verification passed and can uninstall successfully

if [ "$doDryRun" = "Y" ]; then
	
	#dry run only, do not execute preun scripts
	for preun_script in ${PREUN_SCRIPTLIST}
	do
   	 echo "Would have executed ${preun_script} here..."  >> ${UNINSTALL_LOG}
	done

else

    #execute preun scripts
	for preun_script in ${PREUN_SCRIPTLIST}
	do
   	 . ${preun_script}   	    
	done

fi



for uninstall_file in ${UNINSTALL_FILELIST}
do
	

    while read libfile 
    do 
        # Note 1: in the .list file each file is prefixed with its md5sum at install time
        # if md5sum is available on system

        # Note 2: in the .list file the file begins with "/"
        # therefore no / is needed in front of libfile 

        # Note 3: we added the -L check because some symlinks are created in
        # ati-installer.sh; -e returns true on a symlink only if that symlink
        # points to a file that exists, while -L always returns true on a
			# symlink

        #split the md5sum and the file path      
        MD5SUM_RESULT=`echo ${libfile} | cut -d' ' -f1`
        
        if [ -n "$MD5SUM_RESULT" -a "$MD5SUM_RESULT" != "${libfile}" ]; then
           LIBFILE_PATH=`echo ${libfile} | sed -e 's/^'"${MD5SUM_RESULT}"\ '//'`
        else
           MD5SUM_RESULT=""
           LIBFILE_PATH=${libfile}
        fi        		

        if [  -e "${LIBFILE_PATH}" -o -L "${LIBFILE_PATH}" ]; then
            
            #do the md5sum check again here to generate detailed information for dryrun
            
            #verify the line begins with a md5sum 
            if [ -n "`echo $libfile | grep '^/'`" -o -z "$MD5SUM_BIN" ]; then
                
                #no install md5sum check value for file or system does not have md5sum
                               
                if [ "$doDryRun" = "Y" ]; then
                  echo "Would have removed ${LIBFILE_PATH}" >> ${UNINSTALL_LOG}
                else
                  #remove the file
                  rm -f ${LIBFILE_PATH}
                  echo "Removed ${LIBFILE_PATH}" >> ${UNINSTALL_LOG}
				   fi
                     
            else
               result=`${MD5SUM_BIN} "${LIBFILE_PATH}" 2>> ${UNINSTALL_LOG}`
               new_MD5SUM_RESULT=`echo ${result} | cut -d' ' -f1`
                       
               if [ "$new_MD5SUM_RESULT" = "${MD5SUM_RESULT}" ]; then
                  #md5sum check passed
	   			   if [ "$doDryRun" = "Y" ]; then
	   			      echo "Would have removed ${LIBFILE_PATH}" >> ${UNINSTALL_LOG}
                  else
                     #real uninstall, remove the file
                     rm -f ${LIBFILE_PATH}
                  	echo "Removed ${LIBFILE_PATH}" >> ${UNINSTALL_LOG}
	   			   fi

               else
                  #md5sum check failed
                  #should not get here unless executing force because initial verification would have caught failure
                  #dryrun option is not supported here because dryrun and force cannot be used together
                  #and dryrun would have exited when doing initial verification that would have failed
                  if [ -L "${LIBFILE_PATH}" ]; then
	                  #file is a symlink and passed initial md5sum check so symlink integrity is valid
	                  #file that symlink points to may have already been removed causing md5sum check to fail at this point
                     rm -f ${LIBFILE_PATH}
                  elif [ "$useForce" = "Y" ]; then 
                     echo "md5sum integrity check failed.  Force option removes ${LIBFILE_PATH}" >> ${UNINSTALL_LOG}
                     rm -f ${LIBFILE_PATH}
                  else
                     #unsupported state: should have exited script in first md5sum check
                     echo "Unknown state. ${LIBFILE_PATH} failed md5sum check but executing without force. File not removed" >> ${UNINSTALL_LOG}
                     uninstallResult=1
                  fi
				    
               fi
               
           fi
         else
            if [ -n "${LIBFILE_PATH}" ]; then
               echo "Installed file is missing from system ${LIBFILE_PATH}." >> ${UNINSTALL_LOG}
            fi

         fi
    done < ${uninstall_file}
done

if [ "$doDryRun" = "Y" ]; then

	#dry run only, do not execute preun scripts
	for postun_script in ${POSTUN_SCRIPTLIST}
	do
   	 echo "Would have executed ${postun_script} here..."  >> ${UNINSTALL_LOG}
	done
	
else

    #execute postun scripts
	for postun_script in ${POSTUN_SCRIPTLIST}
	do
	    . ${postun_script}
	    if [ $? -ne 0 ]; then
	        echo "Error returned from executing ${postun_script}" 
	    fi
	done
fi


#remove fglrx related files and directory
if [ "$doDryRun" = "Y" ]; then
   echo "Would remove the following at this time"  >> ${UNINSTALL_LOG}
   echo "${PREUN_SCRIPTLIST}"  >> ${UNINSTALL_LOG}
   echo "${POSTUN_SCRIPTLIST}"  >> ${UNINSTALL_LOG}
   echo "${UNINSTALL_FILELIST}"  >> ${UNINSTALL_LOG}
   echo "${SETUP_INSTALLPATH}${ATI_LOG}/ATI_LICENSE.TXT"  >> ${UNINSTALL_LOG}
   echo "${SETUP_INSTALLPATH}${ATI_LOG}/fglrx-install.log"  >> ${UNINSTALL_LOG}
   echo "/etc/ati/inst_path_default" >> ${UNINSTALL_LOG}
   echo "/etc/ati/inst_path_override" >> ${UNINSTALL_LOG}
   echo "/usr/share/ati/amd-uninstall.sh"  >> ${UNINSTALL_LOG}
   echo "/usr/share/ati/`basename $0`"  >> ${UNINSTALL_LOG}

   echo "Dryrun uninstall of fglrx driver complete."
   echo "See $UNINSTALL_LOG for detailed dryrun log."  

else
    #preun
    for preun_script in ${PREUN_SCRIPTLIST}
    do
	rm -f ${preun_script} 2>/dev/null
    done
    #postun
    for postun_script in ${POSTUN_SCRIPTLIST}
    do
	rm -f ${postun_script} 2>/dev/null
    done
    #.list files
    for uninstall_file in ${UNINSTALL_FILELIST}
    do
	rm -f ${uninstall_file} 2>/dev/null
    done
    #ATI_LICENSE.TXT
    rm -f ${SETUP_INSTALLPATH}${ATI_LOG}/ATI_LICENSE.TXT 2>/dev/null
    
    #fglrx-install.log
    rm -f ${SETUP_INSTALLPATH}${ATI_LOG}/fglrx-install.log 2>/dev/null

    #policy layers
    rm -f /etc/ati/inst_path_default 2>/dev/null
    rm -f /etc/ati/inst_path_override 2>/dev/null

    #amd-uninstall
    rm -f /usr/share/ati/amd-uninstall.sh 2>/dev/null

    #fglrx-uninstall.sh(self)
    rm -f `basename $0` 2>/dev/null

    # remove directories as defined by the policy layer 
    # use rmdir because we still want to preserve the directory if the user
    # put in any file that is not ATI driver related
    rmdir --ignore-fail-on-non-empty ${SETUP_INSTALLPATH}${ATI_SRC} 2>/dev/null
    rmdir --ignore-fail-on-non-empty ${SETUP_INSTALLPATH}${ATI_LOG} 2>/dev/null
    rmdir --ignore-fail-on-non-empty ${ATI_UNINST} 2>/dev/null

    if [ $uninstallResult -eq 0 ]; then
      echo "Uninstall fglrx driver complete."
      echo "For detailed log of uninstall, please see $UNINSTALL_LOG"
      echo "System must be rebooted to avoid system instability and potential data loss." 
    else
      echo "Error uninstalling the driver..."
      echo "For detailed log of uninstall, please see $UNINSTALL_LOG"		
    fi
fi




exit $uninstallResult

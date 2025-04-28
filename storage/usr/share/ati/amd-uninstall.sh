#!/bin/sh
#
# Copyright (c) 2011 Advanced Micro Devices, Inc.
#
# Purpose
#    AMD uninstall script for fglrx install
#
# Usage
#    

printHelp()
{
    echo "ATI Catalyst(TM) Proprietary Driver Uninstall script supports the following arguments:"
    echo "--help                           : print help messages"
    echo "--force                          : uninstall without checking for discrepencies"
    echo "--dryrun                         : tests uninstall but does not uninstall"
}


#Function: getUninstallVersion()
#Purpose: return the the current version of this uninstall script
getUninstallVersion()
{
    return 1
}


doUninstall()
{

	#move to where the script resides to find all the files to remove
	cd `dirname $0`
	
	if [ -f fglrx-uninstall.sh ]; then
		eval sh fglrx-uninstall.sh $1 $2
		return $?
	else
		echo "ATI Catalyst(TM) Proprietary Driver Uninstall is corrupt.  Uninstall script 'fglrx-uninstall.sh' is missing."
		return 1
	fi


}


#Starting point of this script, process the {action} argument
useForce=""
doDryRun=""

#get parameters
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
		doDryRun="--dryrun"
	   ;;
	--force)
		useForce="--force"
    	;;
	--getUninstallVersion)
    	getUninstallVersion
    	exit $?
    	;;
	*|--*)
    	echo "${action}: unsupported option passed to ATI Catalyst(TM) Proprietary Driver Uninstall"
    	exit 1
    	;;
	esac
	shift
done

doUninstall $useForce $doDryRun


#!/bin/bash
#
# Copyright (c) 2009 Mellanox Technologies. All rights reserved.
#
# This Software is licensed under one of the following licenses:
#
# 1) under the terms of the "Common Public License 1.0" a copy of which is
#    available from the Open Source Initiative, see
#    http://www.opensource.org/licenses/cpl.php.
#
# 2) under the terms of the "The BSD License" a copy of which is
#    available from the Open Source Initiative, see
#    http://www.opensource.org/licenses/bsd-license.php.
#
# 3) under the terms of the "GNU General Public License (GPL) Version 2" a
#    copy of which is available from the Open Source Initiative, see
#    http://www.opensource.org/licenses/gpl-license.php.
#
# Licensee has the right to choose one of the above licenses.
#
# Redistributions of source code must retain the above copyright
# notice and one of the license notices.
#
# Redistributions in binary form must reproduce both the above copyright
# notice, one of the license notices in the documentation
# and/or other materials provided with the distribution.
#
#
# Add/Remove a patch to/from OFED's ofa_kernel package


usage()
{
cat << EOF
        
        Usage: 
            Add patch to OFED:
                `basename $0`   --add
                                --ofed|-o <path_to_ofed> 
                                --patch|-p <path_to_patch>
                                --type|-t <kernel|backport <kernel tag>|addons <kernel tag>>

            Remove patch from OFED:
                `basename $0`   --remove
                                --ofed|-o <path_to_ofed> 
                                --patch|-p <patch name>
                                --type|-t <kernel|backport <kernel tag>|addons <kernel tag>>

        Example:
                `basename $0` --add --ofed /tmp/OFED-1.X/ --patch /tmp/cma_establish.patch --type kernel

                `basename $0` --remove --ofed /tmp/OFED-1.X/ --patch cma_establish.patch --type kernel

EOF
}

action=""

# Execute command w/ echo and exit if it fail
ex()
{
        echo "$@"
        if ! "$@"; then
                printf "\nFailed executing $@\n\n"
                exit 1
        fi
}

add_patch()
{
        if [ -f $2/${1##*/} ]; then
                echo Replacing $2/${1##*/}
                ex /bin/rm -f $2/${1##*/}
        fi
        ex cp $1 $2
}

remove_patch()
{
        if [ -f $2/${1##*/} ]; then
                echo Removing $2/${1##*/}
                ex /bin/rm -f $2/${1##*/}
        else
                echo Patch $2/${1##*/} was not found
                exit 1
        fi
}

set_rpm_info()
{
        package_SRC_RPM=$(/bin/ls -1 ${ofed}/SRPMS/${1}*src.rpm 2> /dev/null)
        if [[ -n "${package_SRC_RPM}" && -s ${package_SRC_RPM} ]]; then
                package_name=$(rpm --queryformat "[%{NAME}]" -qp ${package_SRC_RPM})
                package_ver=$(rpm --queryformat "[%{VERSION}]" -qp ${package_SRC_RPM})
                package_rel=$(rpm --queryformat "[%{RELEASE}]" -qp ${package_SRC_RPM})
        else
                echo $1 src.rpm not found under ${ofed}/SRPMS
                exit 1
        fi
}

main()
{
        while [ ! -z "$1" ]
        do
                case $1 in
                        --add)
                                action="add"
                                shift
                        ;;
                        --remove)
                                action="remove"
                                shift
                        ;;
                        --ofed|-o)
                                ofed=$2
                                shift 2
                        ;;
                        --patch|-p)
                                patch=$2
                                shift 2
                        ;;
                        --type|-t)
                                type=$2
                                shift 2
                                case ${type} in
                                        backport|addons)
                                                tag=$1
                                                shift
                                        ;;
                                esac
                        ;;
                        --help|-h)
                                usage
                                exit 0
                        ;;
                        *)
                                usage
                                exit 1
                        ;;
                esac
        done

        if [ -z "$action" ]; then
                usage
                exit 1
        fi

        if [ -z "$ofed" ] || [ ! -d "$ofed" ]; then
                echo Set the path to the OFED directory. Use \'--ofed\' parameter
                exit 1
        else
                ofed=$(readlink -f $ofed)
        fi

        if [ "$action" == "add" ]; then
                if [ -z "$patch" ] || [ ! -r "$patch" ]; then
                        echo Set the path to the patch file. Use \'--patch\' parameter
                        exit 1
                else
                        patch=$(readlink -f $patch)
                fi
        else
                if [ -z "$patch" ]; then
                        echo Set the name of the patch to be removed. Use \'--patch\' parameter
                        exit 1
                fi
        fi

        if [ -z "$type" ]; then
                echo Set the type of the patch. Use \'--type\' parameter
                exit 1
        fi

        if [ "$type" == "backport" ] || [ "$type" == "addons" ]; then
                if [ -z "$tag" ]; then
                        echo Set tag for backport patch.
                        exit 1
                fi
        fi

        # Get ofa RPM version
        case $type in
                kernel|backport|addons)
                set_rpm_info ofa_kernel
                ;;
                *)
                echo "Unknown type $type"
                exit 1
                ;;
        esac

        package=${package_name}-${package_ver}
        cd ${ofed}
        if [ ! -e SRPMS/${package}-${package_rel}.src.rpm ]; then
                echo File ${ofed}/SRPMS/${package}-${package_rel}.src.rpm not found
                exit 1
        fi

        if ! ( set -x && rpm -i --define "_topdir $(pwd)" SRPMS/${package}-${package_rel}.src.rpm && set +x ); then
                echo "Failed to install ${package}-${package_rel}.src.rpm"
                exit 1
        fi

        cd -

        cd ${ofed}/SOURCES
        ex tar xzf ${package}.tgz

        case $type in
                kernel)
                if [ "$action" == "add" ]; then
                        add_patch $patch ${package}/kernel_patches/fixes
                else
                        remove_patch $patch ${package}/kernel_patches/fixes
                fi
                ;;
                backport)
                if [ "$action" == "add" ]; then
                        if [ ! -d ${package}/kernel_patches/backport/$tag ]; then
                                echo Creating ${package}/kernel_patches/backport/$tag directory
                                ex mkdir -p ${package}/kernel_patches/backport/$tag
                                echo WARNING: Check that ${package} configure supports backport/$tag 
                        fi
                        add_patch $patch ${package}/kernel_patches/backport/$tag
                else
                        remove_patch $patch ${package}/kernel_patches/backport/$tag
                fi
                ;;
                addons)
                if [ "$action" == "add" ]; then
                        if [ ! -d ${package}/kernel_addons/backport/$tag ]; then
                                echo Creating ${package}/kernel_addons/backport/$tag directory
                                ex mkdir -p ${package}/kernel_addons/backport/$tag
                                echo WARNING: Check that ${package} configure supports backport/$tag 
                        fi
                        add_patch $patch ${package}/kernel_addons/backport/$tag
                else
                        remove_patch $patch ${package}/kernel_addons/backport/$tag
                fi
                ;;
                *)
                echo Unknown patch type: $type
                exit 1
                ;;
        esac

        ex tar czf ${package}.tgz ${package}
        cd -

        cd ${ofed}
        echo Rebuilding ${package_name} source rpm:
        if ! ( set -x && rpmbuild -bs --define "_topdir $(pwd)" SPECS/${package_name}.spec && set +x ); then 
                echo Failed to create ${package}-${package_rel}.src.rpm
                exit 1
        fi
        ex rm -rf SOURCES/${package}*
        if [ "$action" == "add" ]; then
                echo Patch added successfully.
        else
                echo Patch removed successfully.
        fi
        echo
        echo Remove existing RPM packages from ${ofed}/RPMS direcory in order
        echo to rebuild RPMs
}

main $@

#!/usr/bin/python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# (c) 2007 Red Hat. Written by skvidal@fedoraproject.org
# preupgrade-cli

import sys
import os
import os.path
import locale
import gettext

# Needed for i18n support
APP = 'preupgrade'
DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

sys.path.insert(0,'/usr/share/yum-cli/')
from cli import *
from utils import YumUtilBase
from yum import Errors
from preupgrade.misc import hrsize
from preupgrade.dev import bootpath_to_anacondapath
from preupgrade import PreUpgrade, PUError
from preupgrade import __version__ as preupgrade_version
from urlgrabber.grabber import URLGrabError
from output import YumTextMeter
from yum.misc import setup_locale
from optparse import OptionValueError
setup_locale(override_codecs=False)

class PreUpgradeCli(PreUpgrade, YumUtilBase):
    NAME = 'PreUpgrade'
    USAGE = _('usage: preupgrade [options] release')

    def __init__(self):
        PreUpgrade.__init__(self)
        YumUtilBase.__init__(self,
                             PreUpgradeCli.NAME,
                             preupgrade_version,
                             PreUpgradeCli.USAGE)
        self.kernel_args = ""
        self.kickstart_cmds = ""

    def _valid_entries(self):
        cur_ver = float(self.conf.yumvar['releasever'])
        print _("valid entries include:")
        for rel in self.return_available_versions(cur_ver, beta_ok=True):
            print '   "%s"' % rel

    def add_preupgrade_options(self):
        '''Add the preupgrade-specific commandline options:
        --vnc, --dhcp, --ip, --netmask, --gateway, --dns.'''
        # First add the --vnc flag
        def vnc_password_callback(option, opt, value, parser):
            if len(value) < 6:
                raise OptionValueError, _("VNC password must be at least 6 characters")
            setattr(parser.values, option.dest, value)

        self.optparser.add_option("--vnc", metavar=_("[password]"), default="",
          action="callback", callback=vnc_password_callback, type="string",
          help=_("run a VNC server during install, requiring the given password"))
        # A couple of helper functions to validate network options
        def valid_ip(ipstr):
            ip = [0, 0, 0, 0] # 4 placeholder values
            try:
                (ip[0], ip[1], ip[2], ip[3]) = ipstr.split('.')
                for t in ip:
                    b = int(t)
                    if (b < 0) or (b > 255):
                        return False
            except ValueError:
                return False
            return True
        def ip_option_callback(option, opt, value, parser):
            if (opt == '--ip' and parser.values.dhcp) or \
               (opt == '--dhcp' and parser.values.ip):
                raise OptionValueError, _("Can't combine --dhcp and --ip")
            if opt == '--ip' and value == 'dhcp':
                raise OptionValueError, _("--ip=dhcp deprecated. Use --dhcp.")
            if opt in ('--ip', '--netmask', '--gateway', '--dns'):
                if not valid_ip(value):
                    raise OptionValueError, _("%s: '%s' is not a valid ip") % (opt, value)
            elif opt == '--dhcp':
                value = True
            else:
                raise OptionValueError, _("don't know how to handle %s") % opt
            setattr(parser.values, option.dest, value)
        # --clean flag
        self.optparser.add_option("--clean", action="store_true", default=False,
          help=_("Clean up a partially-completed preupgrade run"))
        # Network config options
        self.optparser.add_option("--dhcp", default=False,
          action="callback", callback=ip_option_callback,
          help=_("use DHCP to autoconfigure network during upgrade"), dest='dhcp')
        self.optparser.add_option("--ip", metavar="[IPADDR]", default="",
          type="string", action="callback", callback=ip_option_callback,
          help=_("use this IP address during upgrade"), dest='ip')
        self.optparser.add_option("--netmask", metavar="[NETMASK]", default="",
          type="string", action="callback", callback=ip_option_callback,
          help=_("use this netmask during upgrade"), dest='netmask')
        self.optparser.add_option("--gateway", metavar="[IPADDR]", default="",
          type="string", action="callback", callback=ip_option_callback,
          help=_("use this gateway address during upgrade"), dest='gateway')
        self.optparser.add_option("--dns", metavar="[DNSSERVER]", default="",
          type="string", action="callback", callback=ip_option_callback,
          help=_("use this DNS server during upgrade"), dest='dns')

    def check_network_options(self, opts):
        '''Check for missing network options, according to these rules:
        --vnc requires --dhcp or --ip.
        --ip requires --netmask, --gateway, and --dns.
        --dhcp or --ip are not useful without --vnc.'''
        have_net = (opts.ip != "") or opts.dhcp
        if opts.vnc and not have_net:
            print _("VNC requires a network connection (--ip or --dhcp)")
            return False
        if opts.ip and not (opts.netmask and opts.gateway and opts.dns):
            print _("Static networking requires --ip, --netmask, --gateway, and --dns")
            return False
        if have_net and not opts.vnc:
            print _("Networking is only needed with VNC (--vnc)")
            return False
        return True

    def getconfig(self):
        # Add util commandline options to the yum-cli ones
        self.optparser = self.getOptionParser()
        self.add_preupgrade_options()
        # Parse the commandline option and setup the basics.
        opts = self.doUtilConfigSetup()
        self.opts = opts
        if self.opts.clean:
            return
        try:
            self.retrieve_release_info()
        except IOError:
            print _("Failed to fetch release info."+"\n"+\
      "This could be caused by a missing network connection or a bad mirror.")
            return
        if len(self.cmds) < 1:
            print _("please give a release to try to pre-upgrade to")
            self._valid_entries()
            sys.exit(1)
        myrelease = self.cmds[0]
        if not self.release_map.has_key(myrelease):
            self.errorprint(_("no release named %s available") % myrelease)
            self._valid_entries()
            sys.exit(1)
        if not self.check_network_options(opts):
            sys.exit(1)
        if opts.vnc:
            print _("Enabling VNC mode for the upgrade.")
            self.kickstart_cmds += "vnc --password=%s\n" % opts.vnc
        if opts.dhcp:
            self.kernel_args += " ksdevice=link"
            self.kickstart_cmds += "network --bootproto=dhcp\n"
        elif opts.ip:
            self.kernel_args += " ksdevice=link"
            self.kickstart_cmds += "network --bootproto=static --ip=%s " \
                    "--netmask=%s --gateway=%s --nameserver=%s\n" %      \
                    (opts.ip, opts.netmask, opts.gateway, opts.dns)
        return myrelease

    def errorprint(self, msg):
        print >> sys.stderr, _('Error: %s') % msg

    def main(self, myrelease):
        # Step 1: set up yum repos
        try:
            self.setup(myrelease)
        except Errors.YumBaseError, e:
            self.errorprint(str(e) + "\n\n" + \
                _("This could be caused by a missing network connection or a bad mirror."))
            sys.exit(1)

        # setup progress callbacks on the enabled repos
        if sys.stdout.isatty():
            self.setupProgressCallbacks()

        # Step 2: Get installer images
        self.retrieve_treeinfo()

        # let the user ctrl-C :)
        self.instrepo.setInterruptCallback(self.interrupt_callback)
        # setup progress callback for kernel/stage2 "Repo"
        if sys.stdout.isatty():
            self.instrepo.setCallback(YumTextMeter(fo=sys.stdout))

        try:
            self.retrieve_critical_boot_files()
        except URLGrabError, e:
            # FIXME: allow retry, give details (e.g. not enough space)
            # buttons: "Quit" "Try again" "Different Mirror" etc.
            self.errorprint(str(e))
            sys.exit(1)

        # Try to fetch stage2 and write kickstart to /boot
        extra_args = ""
        try:

            # TODO: make generate_kickstart cram the kickstart into initrd, so
            # /boot-less upgrades can still be automated
            # generate a kickstart file to automate the installation
            extra_args += " ks=%s" % self.generate_kickstart(extra_cmds=self.kickstart_cmds)

            # download stage2.img
            stage2file = self.retrieve_non_critical_files()
            stage2_abs = self.bootpath+"/"+stage2file
            bootdevpath = bootpath_to_anacondapath(stage2_abs, UUID=True)
            extra_args += " stage2=%s" % bootdevpath
        except PUError, e:
            # TODO: offer to create CD/copy stage2 to USB. bluh.
            message = str(e) + "\n\n"
            message += _("The main installer image could not be saved to your hard drive. The installer can download this file once it starts, but this requires a wired network connection during installation.\n\nIf you do not have a wired network connection available, you should quit now.")
            # FIXME: sleep here?
            self.errorprint(message)
            # We fall back to getting stage2 from instrepo
            stage2url = os.path.join(self.instrepo.urls[0], self.mainimage)
            extra_args += " stage2=" + stage2url


        # Step 3: Find out what packages we need to download
        try:
            self.figure_out_what_we_need()
        except Errors.YumBaseError, e:
            self.errorprint(str(e))
            sys.exit(1)

        downloadpkgs = self.get_download_pkgs()

        self.listPkgs(downloadpkgs, _('Packages we need to download'), 'list')
        # print out the size to download, and check available disk space
        cachedir = self.instrepo.cachedir
        downloadsize = self.get_download_size(downloadpkgs)
        print _("Total download size: %s") % hrsize(downloadsize)
        dirstat = os.statvfs(cachedir)
        cachefree = dirstat.f_bsize * dirstat.f_bavail
        if downloadsize > cachefree:
            print _("You don't have enough free disk space in %s to download"\
                  "the packages needed to upgrade.\n\n"\
                  "You must free up at least %s before you can continue.") % \
                  (cachedir,hrsize(downloadsize-cachefree))
            sys.exit(1)

        # Step 4: download the rpms we need
        # confirm with user
        print _('Download packages? ')
        if self._promptWanted():
            if not self.userconfirm():
                print _('Exiting on user command')
                sys.exit(1)
        problems = self.downloadPkgs(downloadpkgs)
        del(self.tsInfo)

        # Check for free space needed to complete upgrade
        def sizecheck(dir, upgradesize):
            s = os.statvfs(dir)
            freespace = s.f_bsize * s.f_bavail
            if upgradesize > freespace:
                print _("Low disk space detected in %s\n\n"\
                      "We recommend that you free up %s before rebooting, "\
                      "or the upgrade may not run.\n\n"\
                      "Note: If the upgrade fails due to low diskspace, "\
                      "your system will not be damaged.") % \
                      (dir,hrsize(upgradesize-freespace))
                return False
            return True
        sizecheck('/usr', self.get_upgrade_size())
        sizecheck('/boot', self.get_kernel_size())

        # FIXME: Step 5 - generate metadata and test transaction
        # Step 5a: make a proper yum repo from downloaded files
        print _("Generating metadata for preupgrade repo")
        comps = self.instrepo.retrieveMD("group")
        # XXX FIXME: get comps data from other repos?
        self.generate_repo(cachedir, comps) # TODO: callback?
        # Add repo=PATH to boot commandline
        repopath = "hd::%s" % cachedir
        extra_args = "repo=%s %s" % (repopath, extra_args)
        # Add kernel_args
        extra_args += self.kernel_args

        print _("Preparing system to boot into installer")
        self.add_boot_target(extra_args)
        self.change_boot_target()

        print _('All finished. The upgrade will begin when you reboot.')
        if 'vnc' in self.kickstart_cmds:
            print
            print _("Once the upgrade starts, a VNC server will open on port 5901.")
            print _("Use it to monitor progress or fix problems that may arise.")
        # FIXME: Ask and reboot for them?


if __name__ == '__main__':
    if os.getuid() != 0:
        print >> sys.stderr, _("You need to be root to run this.")
        sys.exit(1)
    try:
        pu = PreUpgradeCli()
        release = pu.getconfig() # sets pu.opts
        if pu.opts.clean:
            r = pu.resuming_run()
            if r:
                print _("Cleaning previous upgrade to %s") % r
                pu.clear_incomplete_run()
            else:
                print _("No previous run to clean up")
            sys.exit(0)
        elif release:
            pu.main(release)
    except KeyboardInterrupt:
        print _("Exiting.")
        sys.exit(1)

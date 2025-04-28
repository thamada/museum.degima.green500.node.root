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

import sys
import os
import time
import fnmatch
import locale
import gettext
from preupgrade.misc import hrsize
from preupgrade.dev import bootpath_to_anacondapath
from preupgrade import PreUpgrade, PUError
from yum.Errors import YumBaseError
from urlgrabber.grabber import URLGrabError
from yum.misc import setup_locale
setup_locale(override_codecs=False)

# Needed for i18n support
APP = 'preupgrade'
DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

if os.getuid() == 0:
    if '--clean' in sys.argv:
        pu = PreUpgrade()
        resuming_clean = pu.resuming_run()
        if resuming_clean:
            print _("Cleaning previous upgrade to %s") % resuming_clean
            pu.clear_incomplete_run()
        else:
            print _("No previous run to clean up")
        sys.exit(0)
else:
    print _("You need to be root to run this.")
    sys.exit(1)

import gtk
import gtk.glade
import gobject
from preupgrade.guihelpers import UI, Controller
from preupgrade.guihelpers.dialogs import *

gtk.glade.bindtextdomain(APP, DIR)
gtk.glade.textdomain(APP)

if os.path.exists("preupgrade.glade"):
    gladefn = "preupgrade.glade"
else:
    gladefn = "/usr/share/preupgrade/preupgrade.glade"

#FIXME: sure would be nice if the downloadcallback knew about RPM sizes
#TODO: Add to ETA to file download progress?
#TODO: maybe add a skip mirror button?

def update_interface():
    while gtk.events_pending():
        gtk.main_iteration()

# This is used when we retry network connections. If the user brings up the
# network after a failed connection attempt, we need to reset the resolver to
# make gethostbyname() work right.
# Since preupgrade-cli doesn't do retries, it's not needed there.
def reset_resolver():
    '''Attempt to reset the system hostname resolver.
    Returns 0 on success, or -1 if an error occurs.'''
    import ctypes
    reset = -1
    try:
        resolv = ctypes.CDLL("libresolv.so.2")
        reset = resolv.__res_init()
    except (OSError, AttributeError):
        print _("WARNING: could not find __res_init in libresolv.so.2")
    return reset

def exit_instance(exitcode=0):
    try:
        gtk.main_quit()
    except:
        pass
    sys.exit(exitcode)

no_release_available_text = _('No releases available for upgrade')

# (see http://www.pygtk.org/docs/pygtk/class-gtkstatusicon.html)
class StatusIcon:
    '''Convenience class for handling a status icon'''
    def __init__(self, ui):
        self.ui = ui
        self.icon = gtk.StatusIcon()
        self.icon.set_from_stock(gtk.STOCK_REFRESH)
        self.icon.connect('activate', self.on_status_icon_activate)
        self.icon.connect('popup-menu', self.on_popup_menu)
        self.text = ''
        self.frac = 0.0
        self.menu = gtk.Menu()
        self.menuitem_hide = gtk.MenuItem(_("_Hide/Show window"))
        self.menuitem_hide.connect('activate', self.on_menuitem_hide_activate)
        self.menuitem_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuitem_quit.connect('activate', self.on_menuitem_quit_activate)
        self.menu.append(self.menuitem_hide)
        self.menu.append(self.menuitem_quit)
        self.details(_('Fedora Upgrade Assistant is running'))
    def hide(self):
        self.icon.set_visible(False)
    def show(self):
        self.icon.set_visible(True)
    def set_frac(self, frac):
        self.frac = frac
        self.details(self.text)
    def details(self, text):
        self.text = text
        if self.frac:
            text = "(%2.1f%%) %s" % (100*self.frac, text)
        self.icon.set_tooltip(text)
    def hide_ui(self):
        (self.ui.saved_x, self.ui.saved_y) = self.ui.assistant.get_position()
        self.ui.assistant.hide()
        self.ui.visible = False
        # XXX assistant.get_current_page() keeps returning -1. WTF?
        self.ui.saved_page_num = self.ui.page_num
    def show_ui(self):
        self.ui.assistant.move(self.ui.saved_x, self.ui.saved_y)
        self.ui.assistant.show()
        self.ui.visible = True
        self.ui.assistant.set_current_page(self.ui.saved_page_num)
    def toggle_ui(self):
        if self.ui.visible:
            self.hide_ui()
        else:
            self.show_ui()
    def on_menuitem_hide_activate(self, widget, data=None):
        self.toggle_ui()
    def on_menuitem_quit_activate(self, widget, data=None):
        exit_instance()
    def on_status_icon_activate(self, widget):
        '''Called when the systray icon is clicked'''
        self.toggle_ui()
    def on_popup_menu(self, widget, button, timestamp):
        '''Called when systray icon is rightclicked'''
        # TODO: change label to "S_how"/"_Hide" depending on self.ui.visible
        self.menu.show_all()
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, timestamp, self.icon)

class Progress:
    '''An object that provides convenient access to the progress screen'''
    def __init__(self, ui):
        self.ui = ui
        # FIXME: this makes the status bar flicker.
        # Should probably create this in the 'prepare' signal..
        self.icon = StatusIcon(ui)
        self.icon.hide()
        self.step_images = (self.ui.image_step1, self.ui.image_step2,
                            self.ui.image_step3, self.ui.image_step4,
                            self.ui.image_step5)
        self.step = -1
        # These are the target progressbar positions for each step
        # 1) repodata, 2) boot images, 3) depsolving,
        # 4) download packages, 5) generate metadata + transaction test
        self.step_frac = (0.10, 0.20, 0.30, 0.90, 1.00)
        self.frac = 0.0

    def clear(self):
        # Empty out the icons on the progress page
        for i in self.step_images:
            i.clear()
        self.step = -1
        self.set(0.0)
        self.details('')

    def next_step(self):
        if self.step >= 0:
            # we've completed a step - mark it, dude
            self.step_images[self.step].set_from_stock(gtk.STOCK_YES, 1)
            # move the progress bar
            self.set(self.step_frac[self.step])
        self.step += 1
        # Mark the current step (if applicable)
        if self.step < len(self.step_images):
            self.step_images[self.step].set_from_stock(gtk.STOCK_GO_FORWARD, 1)

    def details(self, text, seticon=True):
        self.ui.progressbar.set_text(text)
        if seticon:
            self.icon.details(text)

    def set(self, frac=None):
        if frac:
            self.frac = frac
        self.ui.progressbar.set_fraction(self.frac)
        self.icon.set_frac(frac)

    def pulse(self):
        self.ui.progressbar.pulse()

    def next_target(self):
        return self.step_frac[self.step+1]

    def cur_target(self):
        return self.step_frac[self.step]

class PreUpgradeController(Controller):
    """
    This class incapsulate the glade file.
    all widgets are available under

    self.ui.widget_name

    methods are bound to signals definded in the glade file
    """
    def __init__(self):
        ui = UI(gladefn, "assistant")
        # init the Controller Class to connect signals.
        Controller.__init__(self, ui)
        # Somewhere to save the original text of the first page
        self.finish_text = ''
        self.ui.visible = True
        self.ui.page_num = -1
        self.running = False
        self.release_selection = None
        self.pu = None

        # Find or create a cancel button
        self.ui.assistant.forall(self._find_cancel)
        if not hasattr(self.ui, 'cancel_button'):
            # Add a button to cancel operation
            self.ui.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        if self.ui.cancel_button:
            self.ui.cancel_button.connect('clicked', self.exit_instance)

    # needs to be superclassed
    def main_preupgrade(self):
        pass

    ###################### Callback Handlers #######################
    def on_assistant_apply(self, widget):
        '''
        Called when the apply button is pressed in the
        Assistant.
        Do the real action.
        '''
        self.ui.page_num = 2 # progress page
        self.ui.assistant.set_current_page(self.ui.page_num)
        self._do_main()

    def _find_cancel(self, widget):
        '''
        Find the gtk.Assistant action area cancel button.
        '''
        if isinstance(widget, gtk.Container):
            for child in widget:
                if isinstance(child, gtk.Button):
                    if child.get_label() == 'gtk-cancel':
                        self.ui.cancel_button = child
                        break

    def _do_main(self):
        self.release_name = self.release_selection.get_active_text()
        if self.release_name is None:
            return
        if not self.running:
            self.running = True
            self.main_preupgrade()

    def exit_instance(self, widget=None, event=None, exitcode=0):
        '''quit handler'''
        quit(exitcode)

    def on_reboot_button_clicked(self, widget):
        '''Handler for the reboot button'''
        try:
            self.pu.change_boot_target()
        except AttributeError:

            pass
        os.system("/sbin/reboot")
        self.exit_instance(0)

    def on_assistant_close(self, widget):
        '''assistant close button handler'''
        self.exit_instance(0)

    def on_assistant_prepare(self, widget, page):
        '''
        Assistant prepare handler
        called when a switching to a new page, using the
        forward/backward button
        Dont do anything yet.
        '''
        if page == self.ui.introPage:
            self.ui.page_num = 0
        elif page == self.ui.selectPage:
            self.ui.page_num = 1
        elif page == self.ui.progressPage:
            # Enable the cancel button before the page is completed
            self.ui.cancel_button.set_sensitive(True)
            self.ui.page_num = 2
        elif page == self.ui.endPage:
            self.ui.page_num = 3

    def on_release_combo_changed(self, widget):
        ''' release combo changed handler '''
        # Make the next button active on the select page
        # when a release is selected.
        t = self.release_selection.get_active_text()
        if t and t != no_release_available_text:
            # Make the last page say the right release name
            if not self.finish_text:
                self.finish_text = self.ui.finished_label.get_label()
            label_text = self.finish_text.replace('%RELEASE%', t)
            self.ui.finished_label.set_label(label_text)
            self.ui.assistant.set_page_complete(self.ui.selectPage, True)
        else:
            self.ui.assistant.set_page_complete(self.ui.selectPage, False)


class PreUpgradeGtk(PreUpgradeController):
    def __init__(self):
        PreUpgradeController.__init__(self)
        self.release_selection = self.ui.release_combo
        self.pu = PreUpgrade()
        # Here we hit the network for the first time. If something goes wrong,
        # let the user retry until it works or they give up.
        while not self.pu.release_map:
            try:
                self.pu.retrieve_release_info()
            except IOError, e:
                message = _("Failed to fetch release info."+"\n\n"+\
                            "This could be caused by a missing network connection or a bad mirror.")
                response = continueQuitDialog(self.ui.assistant, message, "Retry")
                if response == gtk.RESPONSE_NO:
                    self.exit_instance(exitcode=1)
                else:
                    reset_resolver()

        # setup the task based progress on the progress page
        self.progress = Progress(self.ui)
        # Empty out the icons on the progress page
        self.progress.clear()
        # This keeps us from running main_preupgrade multiple times
        self.running = False

        # Populate the release_selection combobox
        self.populate_release_selection()
        # and connect the handler for the beta checkbutton
        self.ui.beta_checkbutton.connect('toggled', self.populate_release_selection)
        # make the next button active on the introPage
        self.ui.assistant.set_page_complete(self.ui.introPage, True)
        # Connect the window close event to the quit handler
        self.ui.assistant.connect('delete_event', self.exit_instance)
        # get a pixbuf based on a stock icon
        pix = self.ui.assistant.render_icon(gtk.STOCK_REFRESH, gtk.ICON_SIZE_LARGE_TOOLBAR)
        # Set Assistant header icon
        for page in (self.ui.introPage, self.ui.selectPage, self.ui.progressPage):
            self.ui.assistant.set_page_header_image(page, pix)
        # Check to see if we're resuming an interrupted run
        resuming = self.pu.resuming_run()
        if resuming:
            print _("Detected in-progress upgrade to %s") % resuming
        rel = self.pu.release_map.get(resuming)
        if rel:
            cur_ver = float(self.pu.conf.yumvar['releasever'])
            releases = self.pu.return_available_versions(cur_ver, False)
            beta_releases = self.pu.return_available_versions(cur_ver, True)
            if resuming in beta_releases:
                response = questionDialog(self.ui.assistant,
                    _("Would you like to resume your upgrade to %s?") % resuming)
                if not response:
                    # clear out old caches / boot files / etc
                    print _("Clearing data from upgrade to %s") % resuming
                    self.pu.clear_incomplete_run()
                else:
                    # Act like we just hit the 'Apply' button
                    if resuming not in releases:
                        self.ui.beta_checkbutton.set_active(True)
                        releases = beta_releases
                    index = releases.index(resuming)
                    self.release_selection.set_active(index)
                    self.ui.page_num = 2 # skip the first two pages
                    self.ui.assistant.set_current_page(self.ui.page_num)
                    self._do_main()

    def populate_release_selection(self, widget=None):
        '''Method for populating the dropbox with the list of releases.
        Can be used as a callback (e.g. for beta_checkbutton)'''
        beta_ok = self.ui.beta_checkbutton.get_active()
        store = gtk.ListStore(gobject.TYPE_STRING)
        cur_ver = float(self.pu.conf.yumvar['releasever'])
        for name in self.pu.return_available_versions(cur_ver, beta_ok):
            store.append([name])
        if len(store) == 0:
            # Nothing available! Disable the box.
            store.append([no_release_available_text])
            self.release_selection.set_sensitive(False)
        else:
            # We're OK - enable the box
            self.release_selection.set_sensitive(True)
        self.release_selection.set_model(store)
        self.release_selection.set_active(0)

    def sizecheck(self, needsize, targetpath, errormsg, retry=True):
        '''Keep checking the target path for the required free space (in bytes).
        If there's not enough room, show errormsg, and offer 'Check again' and
        'Quit' options.'''
        if retry:
            button = _("Check again")
        else:
            button = _("Continue")
        freespace = 0
        while needsize > freespace:
            dirstat = os.statvfs(targetpath)
            freespace = dirstat.f_bsize * dirstat.f_bavail
            print _("Available disk space for %s: %s") % \
                    (targetpath, hrsize(freespace))
            if needsize > freespace:
                response = continueQuitDialog(self.ui.assistant,
                        errormsg % (targetpath, hrsize(needsize-freespace)),
                        button)
                if response == gtk.RESPONSE_NO:
                    self.exit_instance(exitcode=1)
                if not retry:
                    break

    def main_preupgrade(self):
        # show the statusbar icon
        self.progress.icon.show()
        # Step 1: set up yum
        self.progress.next_step()
        self.progress.details(_("Setting up..."))
        update_interface()
        # set up a download progress callback
        self.dnlProgress = MultiDownloadProgress(self.progress, 3, throttle= 0.1)
        # XXX: we assume 3 metadata files max, but how can we know for sure?
        # (failure condition: oh well, the bar doesn't move right. no biggie)
        update_interface()
        done = False
        # Setup Repositories
        while not done:
            try:
                self.pu.setup(self.release_name,
                              download_progressbar= self.dnlProgress)
                installed_pkgcount = len(self.pu.doPackageLists().installed)
                done = True
            except YumBaseError, e:
                print str(e)
                response = continueQuitDialog(self.ui.assistant, str(e)+"\n\n"+\
       _("This could be caused by a missing network connection or a bad mirror."), _("Retry"))
                if response == gtk.RESPONSE_NO:
                    self.exit_instance(exitcode=1)
                else:
                    # reset for the retry
                    self.pu.clear_all_repos()
                    reset_resolver()

        # Step 2: Get installer images
        self.progress.next_step()
        self.dnlProgress.reset(4) # treeinfo, kernel, initrd, stage2
        done = False
        while not done:
            try:
                self.progress.details(_("Getting installer metadata..."))
                update_interface()
                self.pu.retrieve_treeinfo()
                self.progress.details(_("Getting installer images..."))
                self.pu.retrieve_critical_boot_files()
                done = True
            except (URLGrabError, PUError), e:
                print str(e)
                response = continueQuitDialog(self.ui.assistant, _("Failed to download installer data.")+"\n\n"+\
        _("This could be caused by a missing network connection or a bad mirror."), _("Retry"))
                if response == gtk.RESPONSE_NO:
                    self.exit_instance(exitcode=1)
                else:
                    reset_resolver()

        # Try to download stage2.img and write kickstart to /boot
        extra_args = ""
        try:
            # TODO: make generate_kickstart cram the kickstart into initrd, so
            # /boot-less upgrades can still be automated
            # generate a kickstart file to automate the installation
            extra_args += " ks=%s" % self.pu.generate_kickstart()

            # download stage2.img
            stage2file = self.pu.retrieve_non_critical_files()
            stage2_abs = self.pu.bootpath+"/"+stage2file
            bootdevpath = bootpath_to_anacondapath(stage2_abs, UUID=True)
            extra_args += " stage2=%s" % bootdevpath
        except PUError, e:
            # TODO: offer to create CD/copy stage2 to USB. bluh.
            message = str(e) + "\n\n"
            print message
            message += _("The main installer image could not be saved to your hard drive. The installer can download this file once it starts, but this requires a wired network connection during installation.\n\nIf you do not have a wired network connection available, you should quit now.")
            response = continueQuitDialog(self.ui.assistant, message)
            if response == gtk.RESPONSE_NO:
                self.exit_instance(exitcode=1)
            # Fallback: let anaconda stage1 download stage2 from instrepo
            stage2url = os.path.join(self.pu.instrepo.urls[0], self.pu.mainimage)
            extra_args += " stage2=" + stage2url

        # Step 3: Find out what packages we need to download
        self.progress.next_step()
        self.dnlProgress.movebar = False # let depsolvecallback handle things
        self.progress.details(_("Checking %i package dependencies (this takes a while)...") % installed_pkgcount)
        update_interface()
        # Set up depsolvecallback
        self.pu.dsCallback = DepSolveCallBack(self.progress, installed_pkgcount, throttle=0.1)
        try:
            self.pu.figure_out_what_we_need()
        except YumBaseError, e:
            print str(e)
            errorDialog(self.ui.assistant, str(e))
            self.exit_instance(exitcode=1)
        self.dnlProgress.movebar = True # back to downloading files!

        # Step 4a: figure out which rpms we need
        self.progress.next_step()
        self.progress.details(_("Checking cached packages..."))
        update_interface()
        downloadpkgs = self.pu.get_download_pkgs()
        # Step 4b: check available disk space
        cachedir = self.pu.instrepo.cachedir
        downloadsize = self.pu.get_download_size(downloadpkgs)
        print _("Downloading %s") % hrsize(downloadsize)
        self.sizecheck(downloadsize, cachedir,
                    _("You don't have enough free disk space in %s to download"\
                    "the packages needed to upgrade.\n\n"\
                    "You must free up at least %s before you can continue."))

        # Step 4c: download needed RPMs
        self.dnlProgress.reset(len(downloadpkgs), downloadsize)
        self.dnlProgress.datamode = True
        problems = self.pu.downloadPkgs(downloadpkgs)
        del self.pu.tsInfo

        # Step 4d: check upgrade sizes now that we've downloaded RPMs
        upgradesize = self.pu.get_upgrade_size()
        print _("Upgrade requires %s") % hrsize(upgradesize)
        self.sizecheck(upgradesize, '/usr',
                    _("Low disk space detected in %s\n\n"\
                    "We recommend that you free up %s before rebooting, "\
                    "or the upgrade may not run.\n\n"\
                    "Note: If the upgrade fails due to low diskspace, "\
                    "your system will not be damaged."))
        # TODO: offer to remove old kernels, tune2fs -r 0, etc..
        kernelsize = self.pu.get_kernel_size()
        print _("Kernel requires %s") % hrsize(kernelsize)
        self.sizecheck(kernelsize, '/boot',
                    _("Low disk space detected in %s\n\n"\
                    "We recommend that you free up %s by deleting old kernels "\
                    "or the upgrade may not run.\n\n"\
                    "Note: If the upgrade fails due to low diskspace, "\
                    "your system will not be damaged."))

        # Step 5a: make a proper yum repo from downloaded pacakages
        self.progress.next_step()
        # Callback will take care of actually updating the pbar details
        comps = self.pu.instrepo.retrieveMD("group")
        # XXX FIXME: get comps data from other repos?
        self.progress.details(_("Generating metadata for upgrade..."))
        print _("Generating metadata for preupgrade repo")
        update_interface()
        self.pu.generate_repo(cachedir, comps,
                              callback=MDGenCallback(pbar=self.progress))
        # Add repo= PATH to boot commandline
        repopath = "hd::%s" % cachedir
        extra_args = "repo=%s %s" % (repopath, extra_args)


        # Final step! Prepare system!
        self.progress.details(_("Preparing system to boot into installer"))
        self.pu.add_boot_target(extra_args)
        # We're done!
        self.progress.next_step()
        self.progress.details(_('Finished!'))
        self.ui.assistant.set_page_complete(self.ui.progressPage, True)

class ProgressbarCallback(object):
    '''Base class for callback classes that talk to the Progress class.
    Provides a simple _update_pbar method and update throttling.'''
    def __init__(self, pbar, throttle=0.0):
        self.pbar = pbar
        self.throttle = throttle # If > 0, throttle updates to this interval
        self.updateTime = 0.0    # time of next update (used when throttling)
    def _update_pbar(self, txt=None):
        if txt:
            self.pbar.details(txt, seticon=False)
        else:
            self.pbar.pulse()

        if self.throttle > 0.0:
            now = time.time()
            if now <= self.updateTime:
                return
            else:
                self.updateTime = now + self.throttle
        update_interface()

class DepSolveCallBack(ProgressbarCallback):
    def __init__(self, progress, installed_pkgcount=None, throttle=0.0):
        ProgressbarCallback.__init__(self, progress, throttle)
        self.installed_pkgcount = installed_pkgcount
        if installed_pkgcount:
            self.base_frac = self.pbar.frac
            self.target_frac = self.pbar.cur_target()
            self.pkg_factor = (self.target_frac-self.base_frac)/self.installed_pkgcount
        self.installcount = 0
        self.erasecount = 0

    def _update_pbar(self, txt=None):
        if self.installed_pkgcount:
            frac = self.base_frac+float(self.installcount)*self.pkg_factor
            self.pbar.set(frac)
        ProgressbarCallback._update_pbar(self, txt)

    # Show info on packages being added to transaction
    def pkgAdded(self, pkgtup, mode):
        (n, a, e, v, r) = pkgtup
        if mode != "e":
            self._update_pbar(_("Found upgrade for %s...") % n)
            self.installcount += 1
    # This takes a few seconds sometimes, and if we don't update the details
    # it looks like certain random packages are hanging the process..
    def procReq(self, name, formatted_req):
        self._update_pbar(_("Checking package dependencies..."))
    # Just wiggle the bar for other depsolving activity
    def start(self):
        self._update_pbar()
    def tscheck(self):
        self._update_pbar()
    def restartLoop(self):
        self._update_pbar()
    def unresolved(self, msg):
        self._update_pbar()
    def procConflict(self, name, confname):
        self._update_pbar()
    def transactionPopulation(self):
        self._update_pbar()
    def downloadHeader(self, name):
        self._update_pbar()
    def end(self):
        self.pbar.set(self.target_frac)
        update_interface()

class MDGenCallback(ProgressbarCallback):
    def __init__(self, pbar, throttle= 0.0):
        ProgressbarCallback.__init__(self, pbar, throttle)
        self.base_frac = self.pbar.frac
        self.target_frac = self.pbar.cur_target()
    def errorlog(self, thing):
        print _("MDGEN ERROR: %s") % thing
    def log(self, thing):
        update_interface()
    def progress(self, item, current, total):
        factor = (self.target_frac-self.base_frac) / total
        self.pbar.set(self.base_frac + (current*factor))
        if current < total:
            self._update_pbar(_("Generating metadata: %d%%") % (current*100/total))
        else:
            self._update_pbar(_("Finishing up..."))

MetaDataMap = {
'repomd.xml'             : _("repository metadata"),
'metalink'               : _("repository metadata"),
'*primary.sqlite.bz2'    : _("package metadata"),
'*primary.xml.gz'        : _("package metadata"),
'*filelists.sqlite.bz2'  : _("filelist metadata"),
'*filelists.xml.gz'      : _("filelist metadata"),
'*other.sqlite.bz2'      : _("changelog metadata"),
'*other.xml.gz'          : _("changelog metadata"),
'*comps*.xml*'           : _("group metadata"),
'updateinfo.xml.gz'      : _("update metadata"),
'vmlinuz'                : _("installer kernel"),
'updates.img'            : _("installer updates"),
'initrd.img'             : _("installer stage 1"),
'ramdisk.image.gz'       : _("installer stage 1"),
'stage2.img'             : _("installer stage 2"),
'install.img'            : _("installer stage 2"),
'minstg2.img'            : _("installer stage 2"),
'.treeinfo'              : _("installer metadata"),
'.discinfo'              : _("installer metadata"),
}

class MultiDownloadProgress(object):
    def __init__(self, progress, numfiles= 0, throttle= 0.0):
        self.progress = progress
        self.reset(numfiles)
        self.throttle = throttle
        self.updateTime = 0.0
        self.datamode = False

    def reset(self, numfiles, totaldata= 0):
        self.cur_file = None
        self.cur_file_size = 0
        self.filecount = 0
        self.datacount = 0
        self.datacomplete = 0
        self.totaldata = totaldata
        self.movebar = True
        self.numfiles = numfiles
        self.base_frac = self.progress.frac
        self.target_frac = self.progress.cur_target()
        self.update_factor = self.target_frac - self.base_frac

    def _getMetadataType(self, name):
        '''
        get metadata type based on the metadata filename
        @param: name: metadata filename
        '''
        typ = 'metadata'
        for pat in MetaDataMap.keys():
            if fnmatch.fnmatch(name, pat):
                typ = MetaDataMap[pat]
                break
        else:
            print _("unknown metadata being downloaded: %s") % name
        return typ

    def updateProgress(self, name, frac, fread, ftime):
        '''This method gets called as a callback from yum's repo stuff.
         Update the progressbar
        @param name: filename
        @param frac: Progress downloading the current file (0 -> 1)
        @param fread: formated string containing BytesRead
        @param ftime : formated string containing remaining or elapsed time
        '''
        if name and name != self.cur_file:
            # Hey look, a new file.
            if self.filecount < self.numfiles:
                self.filecount += 1
            self.cur_file = name
            # Update statusbar info
            if name.endswith('.rpm'):
                self.progress.details(name)
            else:
                self.progress.details(_("Downloading %s...") % self._getMetadataType(name))
            # force an interface update when there's a new file
            self.updateTime = 0.0
        # Move statusbar (unless that's been disabled, like when the depsolver
        # callback is doing its thing)
        if self.movebar:
            if self.numfiles and self.filecount:
                if self.datamode and self.totaldata:
                    f = float(self.datacount)/self.totaldata
                else:
                    # -1+frac gives us fractional movement as we get updates between files
                    f = (self.filecount-1+frac)/self.numfiles
                self.progress.set(self.base_frac + (self.update_factor*f))
                #print "%s: %i/%i (%f)" % (name, self.filecount, self.numfiles, frac)
            else:
                self.progress.pulse()

        if self.throttle > 0.0:
            now = time.time()
            if now <= self.updateTime:
                return
            else:
                self.updateTime = now + self.throttle
        update_interface()

    # Define methods to implement URLGrabber's progressbar protocol
    def start(self, filename=None, url=None, basename=None,
              size=None, now=None, text=None):
        '''This is a callback method used by URLGrabber objects'''
        self.cur_file_size = size
        self.updateProgress(basename, 0.0, '', '')
    def update(self, amount_read):
        '''Another callback from URLGrabber'''
        frac = 0.0
        if self.cur_file_size:
            frac = float(amount_read)/self.cur_file_size
        self.datacount = self.datacomplete + amount_read
        self.updateProgress(self.cur_file, frac, '', '')
    def end(self, amount_read):
        '''Final callback from URLGrabber'''
        self.update(amount_read)
        self.datacomplete += amount_read


if __name__ == "__main__":
    if os.getuid() == 0:
        widgets = PreUpgradeGtk()
        gtk.main()
    else:
        print _("You need to be root to run this.")
        sys.exit(1)

# author: Jonathan Dieter <jdieter@lesbg.com>
#
# heavily modified from yum-deltarpm.py created by
#         Lars Herrmann <herrmann@redhat.com>
# 
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
# Copyright 2005 Duke University
# Copyright 2007 Jonathan Dieter
# Copyright 2007 Red Hat, Inc.  -- Jeremy Katz <katzj@redhat.com>

import os
import subprocess
import gzip
import time
import thread
import threading
import Queue
try:
    from cElementTree import iterparse
except:
    from xml.etree.cElementTree import iterparse

from yum.plugins import TYPE_CORE, PluginYumExit
import yum.Errors
import yum.misc
import yum.logginglevels
from urlgrabber.grabber import URLGrabError
from urlgrabber.progress import format_number
import urlgrabber.progress

complete_download_size = 0
actual_download_size   = 0

process_lock     = None # For progress, updated in thread
processed_t_size = 0    # For progress, updated in thread
processed_f_size = 0    # For progress, updated in thread
processing_fnlst = []   # For progress, updated in thread

requires_api_version = '2.1'
plugin_type = (TYPE_CORE,)

# mapping of repo.id -> PrestoInfo
pinfo = {}

def verifyDelta(sequence, arch):
    """checks that the deltarpm can be applied"""
    if subprocess.call(["/usr/bin/applydeltarpm", "-a", arch,
                        "-C", "-s", sequence], close_fds=True):
        return False
    return True

def applyDelta(deltarpmfile, newrpmfile, arch):
    """applies the deltarpm to create the new rpm"""
    if subprocess.call(["/usr/bin/applydeltarpm", "-a", arch,
                        deltarpmfile, newrpmfile], close_fds=True):
        return False
    return True

def reconstruct(conduit, po, deltalocal, deltasize):
    """logic around applyDelta"""
    retlist = ""
    global actual_download_size
    global processed_t_size
    global processed_f_size

    rpmlocal = po.localpath
    rpmarch  = po.arch
    process_lock.acquire()
    processing_fnlst.append(rpmlocal)
    process_lock.release()
    # applyDelta can think it's succeeded when it hasn't due to signing
    # changes. Also have to be careful about SQL issues, see below.
    if not applyDelta(deltalocal, rpmlocal, rpmarch) or not po.verifyLocalPkg():
        process_lock.acquire()
        processing_fnlst.pop()
        processed_f_size += po.size
        process_lock.release()

        retlist += "Error rebuilding rpm from %s! Will " \
                      "download full package.\n" % os.path.basename(deltalocal)
        try:
            os.unlink(rpmlocal)
        except (OSError, IOError), e:
            pass
    else:
        process_lock.acquire()
        processing_fnlst.pop()
        processed_t_size += po.size
        process_lock.release()

        # Calculate new download size
        actual_download_size -= po.size - deltasize
        
        # Check to see whether or not we should keep the drpms
        delete = not conduit.getConf().keepcache
        if conduit.confBool('main', 'keepdeltas'):
            delete = False
        
        if delete:
            try:
                os.unlink(deltalocal)
            except (OSError, IOError), e:
                pass
    return retlist

class ReconstructionThread(threading.Thread):
    """Threaded process to create rpms from deltarpms"""
    def __init__(self, queue, lock, run_function):
        threading.Thread.__init__(self)
        self.run_function = run_function
        self.queue = queue
        self.lock = lock
        self.can_exit = False
        self.messages = ""
        
    def run(self):
        while True:
            try:
                retval = self.queue.get(not self.can_exit)
            except Queue.Empty:
                # If we're done with our drpms and no more are coming, let's
                # blow this joint
                break
            if retval != None:
                messages = apply(self.run_function, retval)
                if self.can_exit:
                    # If there are not going to be any more new drpms,
                    # send messages directly to conduit
                    conduit = retval[0]
                    if self.messages != "":
                        conduit.info(2, self.messages[:-1])
                        self.messages = ""
                    if messages != "":
                        conduit.info(2, messages[:-1])
                else:
                    # We may be downloading drpms still, so queue messages
                    self.lock.acquire()
                    self.messages += messages
                    self.lock.release()
 

def getDelta(po, presto, conduit, conf_minimum_percentage=100):
    """Does the package have a reasonable delta for us to use?"""
    rpmdb = conduit.getRpmDB()

    # local packages don't make sense to use a delta for...
    if hasattr(po, 'pkgtype') and po.pkgtype == 'local':
        conduit.info(5, "Package %s.%s is local, not using a delta" 
                         % (po.name, po.arch))
        return None
    if po.remote_url.startswith("file:/"):
        # kind of a hack, but file:/ repos are basically local
        conduit.info(5, "Package %s.%s is in a file:// repo, not using a delta"
                         % (po.name, po.arch))
        return None

    # if there's not presto info for the repo, we don't have a delta for
    # the package
    if not presto.has_key(po.repo.id):
        conduit.info(5, "No delta information for repository %s." % po.repo.id)
        return None
    deltainfo = presto[po.repo.id]

    # any deltas for the new package in the repo?
    nevra = "%s-%s:%s-%s.%s" % (po.name, po.epoch, po.version,
                               po.release, po.arch)
    if not deltainfo.has_key(nevra):
        conduit.info(5, "Could not find delta rpm for package %s.%s." 
                         % (po.name, po.arch))
        return None
    deltas = deltainfo[nevra]

    # check to see if we've already got the full package
    local = po.localPkg()
    if os.path.exists(local):
        cursize = os.stat(local)[6]
        totsize = po.size
        if po.verifyLocalPkg(): # we've got it.
            conduit.info(5, "Already have package for %s.%s." 
                             % (po.name, po.arch))
            return None
        if cursize < totsize: # we have part of the file; do a reget
            conduit.info(5, "Already have part of package for %s.%s." 
                             % (po.name, po.arch))
            return None
        os.unlink(local)

    # did we have a previous package of the same arch installed?
    installed = rpmdb.searchNevra(po.name, None, None, None, po.arch)
    if len(installed) == 0:
        conduit.info(5, "Package for %s.%s of the same arch not installed." 
                         % (po.name, po.arch))
        return None
            
    # now, let's see if there's a delta for us...
    bestdelta = None

    for oldpo in installed:
        evr = "%s:%s-%s" % (oldpo.epoch, oldpo.version, oldpo.release)
        if not deltas.has_key(evr):
            continue
        delta = deltas[evr]

        # If the delta isn't small enough, ignore it
        povsize = (po.size * conf_minimum_percentage) / 100
        if povsize < delta['size']:
            continue

        # we just want to use the smallest delta
        if bestdelta and delta['size'] >= bestdelta['size']:
            continue

        # FIXME: This probably takes a while ... need to do something. progress?
        if not verifyDelta(delta['sequence'], po.arch):
            continue

        bestdelta = delta
    if not bestdelta:
        conduit.info(5, "No delta rpm for %s.%s." % (po.name, po.arch))
    return bestdelta

def _processing_data():
    pfnm = None
    process_lock.acquire()
    ptsz = processed_t_size
    pfsz = processed_f_size
    if processing_fnlst:
        pfnm = processing_fnlst[0]
    process_lock.release()
    return ptsz, pfsz, pfnm

def _safe_stat_size(fname):
    if fname is None:
        return 0

    try:
        return os.stat(fname)[6]
    except:
        return 0

def _get_delta_path(cache, po, delta):
    # verify the delta if it already exists
    deltadir = os.path.join(po.repo.cachedir, 'deltas')

    if deltadir not in cache and not os.path.isdir(deltadir):
        try:
            os.mkdir(deltadir)
        except OSError:
            return None

    cache.add(deltadir)
    return os.path.join(deltadir, os.path.basename(delta['filename']))

def downloadPkgs(conduit, presto, download_pkgs=None):
    """download list of package objects handed to you, return errors"""
    global process_lock

    errors = {}
    def adderror(po, msg):
        errors.setdefault(po, []).append(msg)

    rebuild_size = 0 # Size of packages we are going to rebuild.
    cb = None

    conf_mp = conduit.confInt('main', 'minimum_percentage',
                               default=95)
    if conf_mp > 100:
        conf_mp = 100
    if conf_mp < 0:
        conf_mp = 0

    # Set up thread for applying drpms
    queue = Queue.Queue(0)
    process_lock = thread.allocate_lock()
    lock = thread.allocate_lock()
    curthread = ReconstructionThread(queue, lock, reconstruct)
    curthread.start()

    remote_pkgs = []
    remote_size = 0

    must_still_download_pkgs = 0

    if download_pkgs is None:
        download_pkgs = conduit.getDownloadPackages()

    # see which deltas we need to download; if the delta is already
    # downloaded, we can start it reconstructing in the background
    deltapath_cache = set()
    for po in download_pkgs:
        delta = getDelta(po, presto, conduit, conf_mp)
        if delta is None:
            must_still_download_pkgs += po.size
            continue

        deltapath = _get_delta_path(deltapath_cache, po, delta)
        if not deltapath:
            must_still_download_pkgs += po.size
            continue

        if os.path.exists(deltapath):
            try:
                conduit._base.verifyChecksum(deltapath, delta['checksum_type'],
                                             delta['checksum'])
            except URLGrabError, e:
                if po.repo.cache:
                    msg = "Caching enabled and local cache for " \
                               "%sdoesn't match checksum" % deltapath
                    raise yum.Errors.RepoError, msg
                else:
                    cursize = os.stat(deltapath)[6]
                    totsize = delta['size']
                    if cursize >= totsize:
                        os.unlink(deltapath)

                    remote_size += totsize
                    remote_pkgs.append( (po, delta) )
            else:
                # Deltarpm is local and good, put it in the rebuild thread.
                conduit.info(5, "using local copy of deltarpm for %s" % po)
                # HACK: Use the download progress, at least we get something
                cb = po.repo.callback
                po.returnChecksums() # Magic, see below
                queue.put((conduit, po, deltapath, delta['size']))
                rebuild_size += po.size
                continue
        else:
            remote_size += delta['size']
            remote_pkgs.append( (po, delta) )

    #  This is kind of a hack and does nothing in non-Fedora versions,
    # we'll fix it one way or anther soon.
    if (hasattr(urlgrabber.progress, 'text_meter_total_size') and
        len(remote_pkgs) > 1):
        urlgrabber.progress.text_meter_total_size(remote_size)

    if remote_size:
        conduit.info(2, "Download delta size: %s" % format_number(remote_size))

    # now we need to do downloads
    i = 0
    local_size = 0
    for (po, delta) in remote_pkgs:
        i += 1
        # FIXME: verifyChecksum should handle the urlgrabber objects...
        checkfunc = (lambda fo, csumtype, csum:
                     conduit._base.verifyChecksum(fo.filename, csumtype, csum),
                     (delta['checksum_type'],
                      delta['checksum']), {})

        deltadir = os.path.join(po.repo.cachedir, 'deltas')
        deltapath = os.path.join(deltadir,
                                 os.path.basename(delta['filename']))

        # FIXME: this should be moved into _getFile
        dirstat = os.statvfs(deltadir)
        delta_size = delta['size']
        if (dirstat.f_bavail * dirstat.f_bsize) <= (long(po.size) + delta_size):
            adderror(po, 'Insufficient space in download directory %s '
                    'to download' % (deltadir,))
            continue

        if hasattr(urlgrabber.progress, 'text_meter_total_size'):
            urlgrabber.progress.text_meter_total_size(remote_size, local_size)
        try:
            if i == 1 and not local_size and remote_size == delta_size:
                text = os.path.basename(delta['filename'])
            else:
                text = "(%s/%s): %s" % (i, len(remote_pkgs),
                                        os.path.basename(delta['filename']))
            deltafile = po.repo._getFile(url=po.basepath,
                                    relative=delta['filename'],
                                    local=deltapath,
                                    checkfunc=checkfunc,
                                    text=text,
                                    cache=po.repo.cache)
            local_size += delta_size
            if hasattr(urlgrabber.progress, 'text_meter_total_size'):
                urlgrabber.progress.text_meter_total_size(remote_size,
                                                          local_size)
        except yum.Errors.RepoError, e:
            adderror(po, str(e))
        else:
            # HACK: Use the download progress, at least we get something
            cb = po.repo.callback
            #  Magic: What happens here is that the checksum data is loaded
            # from the SQL db in this thread, so that the other thread can call
            # .verifyLocalPkg() without having to hit sqlite.
            po.returnChecksums()
            queue.put((conduit, po, deltafile, delta['size']))
            rebuild_size += po.size

            if errors.has_key(po):
                del errors[po]

        # Check for waiting messages from building thread
        lock.acquire()
        if curthread.messages != "":
            conduit.info(2, curthread.messages[:-1])
            curthread.messages = ""
        lock.release()
        
    if hasattr(urlgrabber.progress, 'text_meter_total_size'):
        urlgrabber.progress.text_meter_total_size(0)
    ptsz, pfsz, pfnm = _processing_data()
    if cb and rebuild_size > (ptsz + pfsz):
        conduit.info(2, "Finishing rebuild of rpms, from deltarpms")
        text = "<delta rebuild>"
        cb.start(text=text, size=rebuild_size)
        sofar_sz = ptsz + pfsz
        cb.update(sofar_sz)
        while sofar_sz < rebuild_size and curthread.isAlive():
            ptsz, pfsz, pfnm = _processing_data()
            sz = ptsz + pfsz + _safe_stat_size(pfnm)
            if sz > sofar_sz:
                cb.update(sz)
                sofar_sz = sz
            time.sleep(0.5)
        ptsz, pfsz, pfnm = _processing_data()
        cb.end(ptsz + pfsz + _safe_stat_size(pfnm))
    
    # Tell build thread that there are no more drpms and wait for it to exit
    curthread.can_exit = True
    queue.put(None)
    curthread.join()
    process_lock = None
    
    if curthread.messages != "":
        conduit.info(2, curthread.messages[:-1])
        curthread.messages = ""
                
    return (errors, must_still_download_pkgs)

class DeltaInfo(object):
    """Base Delta rpm info object"""
    def __init__(self, elem):
        self.epoch = elem.get("oldepoch")
        self.version = elem.get("oldversion")
        self.release = elem.get("oldrelease")
        self.filename = None
        self.sequence = None
        self.size = None
        self.checksum = None
        self.checksum_type = None

        for x in elem.getchildren():
            if x.tag == "checksum":
                self.checksum_type = x.get("type")
            setattr(self, x.tag, x.text)

        # Things expect/assume this, might as well help them:
        self.size = long(self.size)

    def evr(self):
        return "%s:%s-%s" % (self.epoch, self.version, self.release)

    def __str__(self):
        return "filename: %s, sequence: %s, size: %d, checksum (%s) = %s" \
                         % (self.filename, self.sequence, self.size, 
                            self.checksum_type, self.checksum)

    def __getitem__(self, key):
        return getattr(self, key)

class NewPackage(object):
    def __init__(self, elem):
        for prop in ("name", "version", "release", "epoch", "arch"):
            setattr(self, prop, elem.get(prop))

        self.deltas = {}
        for child in elem.getchildren():
            if child.tag != "delta":
                continue
            d = DeltaInfo(child)
            self.deltas[d.evr()] = d

    def nevra(self):
        return "%s-%s:%s-%s.%s" % (self.name, self.epoch, self.version,
                                  self.release, self.arch)

    def __str__(self):
        return "%s <== %s" % (self.nevra(), self.deltas)

    def has_key(self, key):
        return self.deltas.has_key(key)
    def __getitem__(self, key):
        return self.deltas[key]

class PrestoParser(object):
    def __init__(self, filename):
        self.deltainfo = {}
        
        if filename.endswith(".gz"):
            fo = gzip.open(filename)
        else:
            fo = open(filename, 'rt')
        for event, elem in iterparse(fo):
            if elem.tag == "newpackage":
                p = NewPackage(elem)
                self.deltainfo[p.nevra()] = p

    def getDeltas(self):
        return self.deltainfo

# Configuration stuff
def config_hook(conduit):
    # Add --disable-presto option
    parser = conduit.getOptParser()
    if parser:
        parser.add_option('', '--disablepresto', dest='disablepresto',
            action='store_true', default=False,
            help="disable Presto plugin and don't download any deltarpms")

# Set up Presto repositories
#  Don't do this when repos. are setup as that happens a lot, but we only
# care about presto when we are about to download packages. Eventaully if
# we have MD deltas we'll want to trigger then too.
def xpostreposetup_hook(conduit, repos=None):
    opts, commands = conduit.getCmdLine()
    if opts and opts.disablepresto:
        conduit.info(5, '--disablepresto specified - Presto disabled')
        return

    conduit.info(2, 'Setting up and reading Presto delta metadata')
    if repos is None:
        repos = conduit.getRepos().listEnabled()
    for active_repo in repos:
        try:
            deltamd = active_repo.retrieveMD("prestodelta")
        except (yum.Errors.RepoMDError, yum.Errors.RepoError), e:
            try:
                deltamd = active_repo.retrieveMD("deltainfo")
            except (yum.Errors.RepoMDError, yum.Errors.RepoError), e:
                conduit.info(3, "No Presto metadata available for %s" % active_repo)
                continue
        pinfo[active_repo.id] = PrestoParser(deltamd).getDeltas()

def predownload_hook(conduit):
    global complete_download_size
    global actual_download_size

    opts, commands = conduit.getCmdLine()
    if (opts and opts.disablepresto) or len(conduit.getDownloadPackages()) == 0:
        return

    # Get download size, to calculate accurate download savings
    pkglist = conduit.getDownloadPackages()
    repos = set()
    download_pkgs = []
    for po in pkglist:
        local = po.localPkg()
        if os.path.exists(local):
            if conduit._base.verifyPkg(local, po, False):
                continue
        repos.add(po.repo)
        download_pkgs.append(po)
        complete_download_size += po.size
    actual_download_size = complete_download_size

    if not download_pkgs:
        return
    if hasattr(conduit, 'registerPackageName'):
        conduit.registerPackageName("yum-presto")
    xpostreposetup_hook(conduit, repos)
    conduit.info(2, "Processing delta metadata")

    download_pkgs.sort()
    # Download deltarpms
    (problems, more) = downloadPkgs(conduit, pinfo, download_pkgs)

    #  Remove from "our" size, the size which still has to be got via. pkg
    # downloads
    complete_download_size   -= more
    actual_download_size     -= more

    # If 'exitondownloaderror' is on, exit
    if conduit.confBool('main', 'exitondownloaderror') and \
           len(problems.keys()) > 0:
        errstring = 'Error Downloading DeltaRPMs:\n'
        for key in problems.keys():
            errors = yum.misc.unique(problems[key])
            for error in errors:
                errstring += '  %s: %s\n' % (key, error)
        raise PluginYumExit(errstring)

    xpostdownload_hook(conduit)
    if more:
        conduit.info(2, "Package(s) data still to download: %s" %
                     format_number(more))

#  Output stats. about delta downloads ... if we don't have deltas for
# everything (pretty common), we want to output these before we start
# downloading the pkgs themselves. So don't do it postdownload, but after above.
def xpostdownload_hook(conduit):
    global complete_download_size
    global actual_download_size

    opts, commands = conduit.getCmdLine()

    if (opts and opts.disablepresto) or \
       (complete_download_size == actual_download_size):
        return

    drpm_string  = format_number(actual_download_size)
    rpm_string   = format_number(complete_download_size)
        
    saveper = (float(actual_download_size * 100) / complete_download_size)
    saveper = 100 - int(saveper)
    conduit.info(2, "Presto reduced the update size by %i%% (from %s to %s)." % (saveper, rpm_string, drpm_string))

def clean_hook(conduit):
    # Mostly Copy & Paste, from yb._cleanFiles()...
    self = conduit._base # yum :)

    filetype = 'delta-package'
    filelist = []
    removed = 0
    for repo in self.repos.listEnabled():
        path = os.path.join(repo.cachedir, 'deltas')
        if os.path.exists(path) and os.path.isdir(path):
            filelist = yum.misc.getFileList(path, 'drpm', filelist)

    for item in filelist:
        try:
            yum.misc.unlink_f(item)
        except OSError, e:
            self.logger.critical('Cannot remove %s file %s', filetype, item)
            continue
        else:
            self.verbose_logger.log(yum.logginglevels.DEBUG_4,
                '%s file %s removed', filetype, item)
            removed+=1
    self.verbose_logger.info('%d %s files removed, by presto' % (removed, filetype))

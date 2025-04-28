#!/usr/bin/python
import Alchemist
import os
import re
import exceptions
import string

def VersionList(cache_dir,template):
	"""
	Utility function.
	We build a list of the versions available of a given template file in
	a cache directory. the files will resemble /cache_dir/version.template
	"""
        version_list = []
        cache_match = re.compile(r'(\d+)\.cache.' + re.escape(template))
        for file in os.listdir(cache_dir):
                match = cache_match.match(file)
                if match:
                        version_list.append(string.atoi(match.groups(0)[0]))
        version_list.sort()
        return version_list


def getBox(box_cfg):
	"""
	getBox: get a BlackBox from this module
	@box_cfg: a box_cfg conformant AdmList element containing
	the following elements:
	path: type string, the path to the context file (required)
	
	returns: CacheBlackBox object
	"""
	return CacheBlackBox(box_cfg)

class CacheBlackBox(Alchemist.BlackBox):
	"""
	The CacheBlackBox class provides a class to read and write Contexts
	from and to files.
	"""
	def __init__ (self, box_cfg):
		"""
		__init__: Initialize a BlackBox
		@self: the class instance
		@box_cfg: a box_cfg conformant AdmList element containing
		the following elements:
			cache_dir : a string
			template : a string
			mode : an integer
		"""
		self.status = 0
		self.me = self.__class__.__module__
		self._errNo = 0
		self._errStr = None
		self.writable = 1
	
		Alchemist.validateBoxCfg(box_cfg)
	
		try:
			self.cache_dir = box_cfg.getChildByName("cache_dir").getValue()
		except:
			raise ValueError, "CacheBlackBox box_cfg must contain a 'cache_dir' entry"

		try:
			self.template = box_cfg.getChildByName("template").getValue()
		except:
			raise ValueError, "CacheBlackBox box_cfg must contain a 'template' entry"

		try:
			self.mode = box_cfg.getChildByName("mode").getValue()
		except:
			raise ValueError, "CacheBlackBox box_cfg must contain a 'mode' entry"

		try:
			self.depth = box_cfg.getChildByName("depth").getValue()
		except:
			raise ValueError, "CacheBlackBox box_cfg must contain a 'dapth' entry"
			

	def isReadable (self):
		"""
		isReadable: if a read were attempted now, would it succede?
		@self: this BlackBox instance
		"""
		vlist = VersionList(self.cache_dir, self.template)
		if len(vlist) > 0:
			return 1
		return 0

	def readVersion(self, version):
		"""
		readVersion: reads a specific version from the cache directiry, if it exists.
		"""

		try:
			path = self.cache_dir + '/' + repr(version) + '.cache.' + self.template
			return Alchemist.ReadContextFromFile(path)
		except:
			return None


	def read (self):
		"""
		read: read the contents of the CacheBlackBox
		@self: this CacheBlackBox instance

		"""
		vlist = VersionList(self.cache_dir, self.template)
		if len(vlist) == 0:
			return None

		# Read the highest version in the list
		return self.readVersion(vlist[-1])

	def version(self):
		"""
                version: returns the version of this CacheBlackBox's context
                @self: this CacheBlackBox instance

		"""
		vlist = VersionList(self.cache_dir, self.template)
		if len(vlist) != 0:
			return vlist[-1]

		return None

	def write (self, context):
		"""
		write: write the contents of the CacheBlackBox
		@self: this CacheBlackBox instance

		This function is callable multiple times. It writes a
		Context out to the file the CacheBlackBox is initialized with.
		It returns 0 on failure, and a non-zero, positive integer
		on success.
		"""

		serial = context.getIdentityRoot().getSerial()
		path = self.cache_dir + '/' + repr(serial) + '.cache.' + self.template
		try:
			Alchemist.WriteContextToFile(path, context, mode = self.mode)	
	
			# Trash the bottom of the context stack if we've over flowed it.
			vlist = VersionList(self.cache_dir, self.template)
			if len(vlist) > self.depth:
				os.unlink(self.cache_dir + '/' + repr(vlist[0]) + '.' + self.template)

			return 1

		except Exception, e:
			if len(e.args) == 1:
				self._errNo = 1
				self._errStr = e.args[0]
			else:
				self._errStr = e.args[1]
				self._errNo = e.args[0]
			return 0

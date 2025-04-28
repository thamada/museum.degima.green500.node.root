#!/usr/bin/python
import Alchemist
import gzip
import os
import stat
import sys
import time

def ReadContextFromFile(file_path):
	"""
	ReadContextFromFile: read a context from a given file
	@file_path: the path to the file

	This function reads a context from a gzip'ed file
	
	returns: the context from the file
	exceptions: FileIO
	"""
	try:
		xml_string = gzip.open(file_path).read()
	except IOError:
		xml_string = open(file_path).read()
		
	return Alchemist.Context(xml = xml_string)

def WriteContextToFile(file_path, context, mode = 0600, compressed = 9):
	"""
	WriteContextFromFile: write a context to a given file
	@file_path: the path to the file
	@context: the context to write

	This function writes a context to a gzip'ed file
	
	returns: none
	exceptions: FileIO
	"""
	xml_string = context.toXML()

	if os.path.exists(file_path):
		os.unlink(file_path)

	fd = os.open(file_path, os.O_WRONLY | os.O_CREAT| os.O_TRUNC, mode)
	file = os.fdopen(fd, "w")

	if compressed:
		file = gzip.GzipFile(file_path, "w", compresslevel = compressed, fileobj = file)

	file.write(xml_string)
	file.close()

def getBox(box_cfg):
	"""
	getBox: get a BlackBox from this module
	@box_cfg: a box_cfg conformant AdmList element containing
	the following elements:
	path: type string, the path to the context file (required)
	readable: type bool, flag, if the box should be readable (optional)
	writable: type bool, flag, if the box should be writable (optional)
	
	returns: FileBlackBox object
	"""
	return FileBlackBox(box_cfg)

class FileBlackBox(Alchemist.BlackBox):
	"""
	The FileBlackBox class provides a class to read and write Contexts
	from and to files.
	"""
	def __init__ (self, box_cfg):
		"""
		__init__: Initialize a BlackBox
		@self: the class instance
		@box_cfg: a box_cfg conformant AdmList element containing
		the following elements:
		   path: type string, the path to the context file (required)
		   readable: type bool, flag, if the box should
		          be readable (optional)
		   writable: type bool, flag, if the box should
		          be writable (optional)
		   mode: an integer file mode

		This function is the initializer for FileBlackBoxes.
		"""
		self.status = 0
		self.me = self.__class__.__module__
		self._errNo = 0
		self._errStr = None
		self.readable = 1
		self.writable = 1
	
		Alchemist.validateBoxCfg(box_cfg)
	
		try:
			self.path = box_cfg.getChildByName("path").getValue()
		except:
			raise ValueError, "FileBlackBox box_cfgs must contain a 'path' element"

		try:
			self.readable = box_cfg.getChildByName("readable").getValue()
		except:
			pass

		try:
			self.writable = box_cfg.getChildByName("writable").getValue()
		except:
			pass

		try:
			self.mode = box_cfg.getChildByName("mode").getValue()
		except:
			self.mode = 0600
			pass

	def isReadable (self):
		"""
		isReadable: if a read were attempted now, would it succede?
		@self: this BlackBox instance
		"""
		return (self.readable and os.access(self.path, os.R_OK))

	def isWritable (self):
		"""
		isWritable: if a write were attempted now, would it succede?
		@self: this BlackBox instance
		"""
		
		writable = 0
		
		if os.access(self.path, os.W_OK):
			writable = 1
		elif (not os.access(self.path, os.F_OK)) and os.access(os.path.dirname(self.path), os.W_OK):
			writable = 1

		return self.writable and writable

	def read (self):
		"""
		read: read the contents of the FileBlackBox
		@self: this FileBlackBox instance

		This function is callable multiple times, and if it cannot
		succede on a given call, it returns None. It does not
		cache returns information in the normal sense, unless the data
		is not dynamic. And it does not keep a reference to the
		AdmContext it returns.

		It also sets the serial of the returned context to the modify
		time of the file.
		"""
		# am I readable?
		if (not self.isReadable()):
			return None

		version = self.version()
		context = ReadContextFromFile(self.path)
		context.getIdentityRoot().setSerial(version)
		
		return context


	def version(self):
		"""
                version: returns the version of this FileBlackBox's context
                @self: this FileBlackBox instance

		This function returns the modification time (in seconds since the epoch)
		of the file referenced by self.path
		"""

		if os.path.exists(self.path):
			return os.stat(self.path)[8]

		return None

	def write (self, context):
		"""
		write: write the contents of the FileBlackBox
		@self: this FileBlackBox instance

		This function is callable multiple times. It writes a
		Context out to the file the FileBlackBox is initialized with.
		It returns 0 on failure, and a non-zero, positive integer
		on success.
		"""
		# am I writable?
		if (not self.isWritable()):
			return 0

		# write the context out
		try:
			WriteContextToFile(self.path, context, mode = self.mode)
		except Exception, e:
			if len(e.args) == 1:
				self._errNo = 1
				self._errStr = e.args[0]
			else:
				self._errStr = e.args[1]
				self._errNo = e.args[0]
			return 0


###########################################################################
#
# Test
#
###########################################################################
#if __name__ == '__main__':

#   boxpath = '/var/tmp/BootStrap'
    
#    bbc = Alchemist.Context(name = 'FileBlackBox', serial = 1)
#    broot = bbc.getDataRoot()
#    list = broot.addChild(Alchemist.Data.ADM_TYPE_LIST, 'box_cfg')
#    list.addChild(Alchemist.Data.ADM_TYPE_STRING, 'path').setValue(boxpath)
#    list.addChild(Alchemist.Data.ADM_TYPE_STRING, 'box_type').setValue('FileBlackBox')
#    list.addChild(Alchemist.Data.ADM_TYPE_BOOL, 'readable').setValue(true)
#    list.addChild(Alchemist.Data.ADM_TYPE_BOOL, 'writable').setValue(true)

#    bb = FileBlackBox(list)
    
#    if bb.errNo():
#	    print 'Error creating FileBlackBox: ' + bb.strError()
#	    sys.exit(10)
    
#    if bb.isWritable():
#        if bb.write(bbc) != true:
#            if bb.errNo():
#                print 'Error writing to BlackBox: ' + bb.strError()
#            else:
#                print bbc.toXML()
#    else: print 'Error: ' + boxpath + ' is not writable!'

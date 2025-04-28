#! /usr/bin/python

## Alchemist - Python bindings for the Alchemist
## Copyright (C) 2000 Red Hat, Inc.
## Copyright (C) 2000 Tim Waugh <twaugh@redhat.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

use_pyalchemist = True

if use_pyalchemist:
	from PyAlchemist import *
else:
	from _alchemist import *
import exceptions
import imp
import time

if not use_pyalchemist:
	def _mkData (_dat):
		if _dat == None:
			return None
		type = data_getType (_dat)
		if (type == Data.ADM_TYPE_LIST):
			return ListData (_dat)
		if (type == Data.ADM_TYPE_COPY):
			return CopyData (_dat)
		if (type == Data.ADM_TYPE_INT):
			return IntData (_dat)
		if (type == Data.ADM_TYPE_FLOAT):
			return FloatData (_dat)
		if (type == Data.ADM_TYPE_BOOL):
			return BoolData (_dat)
		if (type == Data.ADM_TYPE_STRING):
			return StringData (_dat)
		if (type == Data.ADM_TYPE_BASE64):
			return Base64Data (_dat)
		return None

	class Data:
		## From alchemist.h:
        	ADM_TYPE_UNKNOWN = 0
        	ADM_TYPE_LIST    = 1
        	ADM_TYPE_COPY    = 2
        	ADM_TYPE_INT     = 3
        	ADM_TYPE_FLOAT   = 4
        	ADM_TYPE_BOOL    = 5
        	ADM_TYPE_STRING  = 6
        	ADM_TYPE_BASE64  = 7

		def __init__ (self, thing):
			self._dat = thing;

		def getContainer (self):
			return _mkData (data_getContainer (self._dat))

		def getContext (self):
			return Context(ctx = data_getContext (self._dat))

		def getType (self):
			return data_getType (self._dat)

		def isAlive (self):
			return data_isAlive (self._dat)

		def unlink (self):
			data_unlink (self._dat)

		def getName (self):
			return data_getName (self._dat)

		def setName (self, name):
			data_setName (self._dat, name)

		def getSource (self):
			return data_getSource (self._dat)

		def setSource (self, src):
			data_setSource (self._dat, src)

		def isProtected (self):
			return data_isProtected (self._dat)

		def setProtected (self, prot):
			data_setProtected (self._dat, prot)

		def getPos (self):
			return data_getPos (self._dat)

		def isIdentical(self, other):
			return data_isIdentical(self._dat, other._dat)

	class ListData (Data):
		def isAnonymous (self):
			return list_isAnonymous (self._dat)

		def setAnonymous (self, anon):
			list_setAnonymous (self._dat, anon)

		def isAtomic (self):
			return list_isAtomic (self._dat)

		def setAtomic (self, atomic):
			list_setAtomic (self._dat, atomic)

		def isPrepend (self):
			return list_isPrepend (self._dat)

		def setPrepend (self, prep):
			list_setPrepend (self._dat, prep)

		def getNumChildren (self):
			return list_getNumChildren (self._dat)

		def getChildByIndex (self, index):
			return _mkData(list_getChildByIndex (self._dat,
								index))

		def getChildByName (self, name):
			return _mkData (list_getChildByName (self._dat,
								name))

		def hasChildNamed (self, name):
			return list_hasChildNamed (self._dat, name)

		def addChild (self, type, name):
			return _mkData (list_addChild (self._dat, type,
							  name))

		def moveChild (self, datum, index):
			list_moveChild (self._dat, datum._dat, index)

		def copyData (self, datum):
			return _mkData (list_copyData (self._dat,
							  datum._dat))

	class CopyData (Data):
		def getValue (self):
			return copy_getValue (self._dat)

		def setValue (self, v):
			copy_setValue (self._dat, v)

	class IntData (Data):
		def getValue (self):
			return int_getValue (self._dat)

		def setValue (self, v):
			int_setValue (self._dat, v)

	class FloatData (Data):
		def getValue (self):
			return float_getValue (self._dat)

		def setValue (self, v):
			float_setValue (self._dat, v)

	class BoolData (Data):
		def getValue (self):
			return bool_getValue (self._dat)

		def setValue (self, v):
			bool_setValue (self._dat, v)

	class StringData (Data):
		def getValue (self):
			return string_getValue (self._dat)

		def setValue (self, v):
			string_setValue (self._dat, v)

	class Base64Data (Data):
		def getValue (self):
			return base64_getValue (self._dat)

		def setValue (self, v):
			base64_setValue (self._dat, v)

	class Identity:
		def __init__ (self, id):
			self._id = id

		def getParentA (self):
			A_id = identity_getParentA (self._id)
			if A_id == None:
				return None
			return Identity (A_id)

		def getParentB (self):
			B_id = identity_getParentB (self._id)
			if B_id == None:
				return None
			return Identity (B_id)

		def getName (self):
			return identity_getName (self._id)

		def setName (self, name):
			identity_setName (self._id, name)

		def getSerial (self):
			return identity_getSerial (self._id)

		def setSerial (self, serial):
			identity_setSerial (self._id, serial)

		def isAlive (self):
			return identity_isAlive (self._id)

		def isIdentical (self, other):
			return identity_isIdentical(self._id, other._id)

	class Context:
		def __init__(self, name = None, serial = None, ctx = None, xml = None):
			if ctx != None:
				self._ctx = ctx
				return None

			if xml != None:
				self._ctx = context_fromXML(xml)
				return None

			if name != None and serial != None:
				self._ctx = context_create (name, serial)
				return None

			raise ContextError, "Illegal constructor parameters"

		def copy (self):
			return Context(ctx = context_copy (self._ctx))

		def flatten (self):
			context_flatten (self._ctx)

		def toXML (self):
			return context_toXML (self._ctx)

		def getDelete (self, index):
			return context_getDelete (self._ctx, index)

		def setDelete (self, path):
			context_setDelete (self._ctx, path)

		def clearDeleteByIndex (self, index):
			context_clearDeleteByIndex (self._ctx, index)

		def clearDeleteByString (self, path):
			context_clearDeleteByString (self._ctx, path)

		def getNumDeletes (self):
			return context_getNumDeletes (self._ctx)

		def getIdentityRoot (self):
			return Identity(context_getIdentityRoot (self._ctx))

		def getDataRoot (self):
			return _mkData(context_getDataRoot (self._ctx))

		def getDataByPath (self, path):
			return _mkData(context_getDataByPath (self._ctx, path))

		def isIdentical(self, other):
			return context_isIdentical(self._ctx, other._ctx)

	def merge (name, serial, ctxA, ctxB):
		return Context(ctx = context_merge (name, serial, ctxA._ctx, ctxB._ctx))



def validateBoxCfg (box_cfg):
	"""
	validataBoxCfg: throws exceptions on invalid box_cfgs
	@box_cfg: A box_cfg @AdmList, to be checked for conformance.

	This function validates a box_cfg element, and throws a @BlackBoxError
	if it is an invalid element.

	box_cfg elements are defined as:
	Living, non-anonymous AdmList elements, containing a AdmString child
	named 'box_type', which specifies which type of BlackBox this box_cfg
	configures.

	Why, you may ask, do box_cfg elements not just have a cache optional
	child, that is itself a box_cfg element? Because then caches could
	have caches, and that way lies madness.

	throws: @ValueError if anything is wrong with the box_cfg
	"""
	if box_cfg == None:
		raise ValueError, "'None' passed as box_cfg"
	if box_cfg.__class__ != ListData:
		raise ValueError, "box_cfg is not an AdmList element"
	if not box_cfg.isAlive():
		raise ValueError, "Dead node passed as box_cfg"
	if box_cfg.isAnonymous():
		raise ValueError, "box_cfg is an annonymous AdmList element"
	try:
		box_type = box_cfg.getChildByName("box_type")
	except KeyError, e:
		raise ValueError, "box_cfg contains no 'box_type' child"
	if box_type.__class__ != StringData:
		raise ValueError, "box_cfg's box_type child is not an AdmString element"

class BlackBox:
	"""
	The BlackBox base class provides a generic class for Alchemist Data
	Library BlackBox modules to inherit. 
	"""
	def __init__ (self, box_cfg):
		"""
		__init__: Initialize a BlackBox
		@self: the class instance
		@box_cfg: a box_cfg conformant AdmList element

		This function is the initializer for BlackBoxes, it, and
		functions which overload it, must not keep references to,
		or modify in any way, the box_cfg it is passed.

		It is also a good idea if modules call validateBoxCfg on their
		box_cfgs before touching them, so that we get uniform error
		raising on broken data.
		"""
		self.me = self.__class__.__module__
		self.status = 0
		self._errNo = 0
		self._errStr = None		
		self.readable = 0
		self.writable = 0

		validateBoxCfg(box_cfg)

	def getStatus (self):
		"""
		getStatus: returns a BlackBox dependent status value.
		@self: this BlackBox instance
		"""
		return self.status

	def errNo (self):
		"""
		errNo: returns a BlackBox dependent error number.
		@self: this BlackBox instance
		"""
		return self._errNo

	def strError (self):
		"""
		strError: returns a BlackBox dependent error string.
		@self: this BlackBox instance
		"""
		return str(self._errStr)

	def isReadable (self):
		"""
		isReadable: if a read were attempted now, would it succede?
		@self: this BlackBox instance
		"""
		return self.readable

	def isWritable (self):
		"""
		isWritable: if a write were attempted now, would it succede?
		@self: this BlackBox instance
		"""
		return self.writable

	def read (self):
		"""
		read: read the contents of the BlackBox
		@self: this BlackBox instance

		This function must be callable multiple times, and if it cannot
		succede on a given call, it should return None. It should not
		cache returns information in the normal sense, unless the data
		is not dynamic. And it must not keep a reference to the
		AdmContext it returns.
		"""
		return None

	def version(self):
		"""
		version: returns the version of the context held in a black box.
		@self: this BlackBox instance

		This function should be overridden by all subclassess so that it
		returns a version number that is identical to the serial number
		of the context that /would/ have been returned had a read() call
		benn made instead of the version() call.
		"""
		return 0

	def readVersion (self,version):
		"""
		readVersion: reads a specific version of a BlackBox
		@self: this BlackBox instance

		This is a per-BlackBox function, and implementors should not
		provide it unless they can guarantee that the version read will
		be a perfect copy of the last context returned by 'read' for the
		version called, or None.

		A context's version is the serial number of the root node of
		it's identity tree.
		"""
		return None

	def write (self, context):
		"""
		write: write the contents of the BlackBox
		@self: this BlackBox instance

		This function must be callable multiple times. It writes a
		Context out to where ever the box does it, if it does anything.
		It must return 0 on failure, and a non-zero, positive integer
		on success.
		"""
		return 0


# We preload FileBlackBox, because we need it for bootstrap
# NOTE!: Because of the unique way in which python handles imports,
# This import MUST be after the BlackBox deffinition.
import FileBlackBox
from FileBlackBox import ReadContextFromFile, WriteContextToFile
ImportedBoxes = {"FileBlackBox" : FileBlackBox }

def getBox (box_cfg):
	"""
	getBox: automagically finds and loads an arbitrary BlackBox
	@box_cfg: a box_cfg conformant AdmList element

	This function takes a box_cfg conformant AdmList element, extracts
	its box_type child, reads the box type specified in it, and loads
	and configures the appropriate box, if the neccesary module can be
	found.

	Modules providing BlackBoxes must define a function getBox() which
	takes a box_cfg and returns None, or a configured BlackBox.

	returns: a configured BlackBox, or None, if no BlackBox can be found
	"""
	validateBoxCfg(box_cfg)

	# pull the type
	box_type = box_cfg.getChildByName("box_type").getValue()

	# Search for an appropriate module.
	# because it is always loaded Note that if we get this far, we
	# either succed, or return None. We swallow exceptions.
	if ImportedBoxes.has_key(box_type):
		# We've already loaded this module, lets not look for it again
		# We don't catch exceptions here, because we know that the module
		# exists, and any exceptions thrown should be config exceptions,
		# which we should let through.
		return ImportedBoxes[box_type].getBox(box_cfg)
	else:
		# new box, lets try to find it.
		try:
			box_mod_info = imp.find_module(box_type)
		except:
			return None

		if box_mod_info[0] != None:
			# if we find a path to load, try to load it.
			try:
				box_mod = imp.load_module(box_type,
							  box_mod_info[0],
							  box_mod_info[1],
							  box_mod_info[2])
				if box_mod_info[0] != None:
					box_mod_info[0].close()
				ImportedBoxes[box_type] = box_mod
			except:
			# if loading fails, we return None, not an exception
				return None
		
			return box_mod.getBox(box_cfg)
	
def validateBoxEntry (box_entry):
	"""
	validateBoxEntry: throws exceptions on invalid box_entrys
	@box_entry: A box_entry conformant @AdmList element, to be checked

	box_entry elements are defined as:
	Living, non-anonymous AdmList elements, containing a box_cfg child
	named 'box', and an optional box_cfg child named 'cache'. If cache
	exists, it must be a box_cfg element

	throws: @BlackBoxError if anything is wrong with the box_cfg
	"""
	if box_entry == None:
		raise ValueError, "'None' passed as box_entry"
	if box_entry.__class__ != ListData:
		raise ValueError, "box_entry is not an AdmList element"
	if not box_entry.isAlive():
		raise ValueError, "Dead node passed as box_entry"
	if box_entry.isAnonymous():
		raise ValueError, "box_entry is an annonymous AdmList element"
	try:
		box = box_entry.getChildByName("box")
		validateBoxCfg(box)
	except KeyError, e:
		raise ValueError, "box_entry contains no 'box' child"
	try:
		cache = box_entry.getChildByName("cache")
		validateBoxCfg(cache)
	except KeyError, e:
		pass

	return None

def validateNamespaceCfg (namespace_cfg):
	"""
	validateNamespaceCfg: throws exceptions on invalid namespace_cfgs
	@namespace_cfg: a namespace_cfg conformant @AdmList, to be checked.

	namespace_cfg elements are defined as:
	Living, non-anonymous AdmList elements, containing a non-anonymous
	AdmList child named "input_set", an optional non-anonymous AdmList
	child named "output_set", and an optional box_cfg child named "cache"

	"input_set" (and "output_set", if it exists), must be non-anonymous
	AdmList elements containing only box_entrys, and must be non-empty.

	Note that this is not an exclusive set, and config tools are free to
	add whatever additional children they want. However, the child
	"_namespace_config_" is reserved for future expansion.
	"""
	if namespace_cfg == None:
		raise ValueError, "'None' passed as namespace_cfg"
	if namespace_cfg.__class__ != ListData:
		raise ValueError, "namespace_cfg is not an AdmList element"
	if not namespace_cfg.isAlive():
		raise ValueError, "Dead node passed as namespace_cfg"
	if namespace_cfg.isAnonymous():
		raise ValueError, "namespace_cfg is an anonymous AdmList element"

	try:
		# validate input_set
		input_set = namespace_cfg.getChildByName("input_set")
		k = input_set.getNumChildren()
		if k == 0:
			raise ValueError, "namespace_cfg has an empty input_set"
		for i in xrange(k):
			box_entry = input_set.getChildByIndex(i)
			validateBoxEntry(box_entry)
			try:
				box_entry.getChildByName("cache")
			except KeyError, e:
				raise ValueError, "input set box_entry contains no 'cache' child"

	except KeyError, e:
		raise ValueError, "namespace_cfg contains no input_set"

	try:
		# validate output_set
		output_set = namespace_cfg.getChildByName("output_set")
		k = output_set.getNumChildren()
		if k == 0:
			raise ValueError, "namespace_cfg has an empty output_set"
		for i in xrange(k):
			validateBoxEntry(output_set.getChildByIndex(i))

	except KeyError, e:
		pass

	try:
		validateBoxCfg(namespace_cfg.getChildByName("cache"))
	except KeyError, e:
		pass

	return None
		

def validateMetaCtx (meta_context):
	"""
	validateMetaCtx: throws exceptions on invalid meta_contexts
	@meta_context: a meta_context conformant @AdmContext, to be checked.

	meta_context elements are defined as:
	AdmContexts, whose data tree root contains only valid namespace_cfg
	elements, or the reserved child "_switchboard_config_", which needs
	not be a valid namespace_cfg.
	"""
	if meta_context == None:
		raise ValueError, "'None' passed as meta_context"
	if meta_context.__class__ != Context:
		raise ValueError, "meta_context is not an AdmContext element"
	root = meta_context.getDataRoot()
	for i in xrange(root.getNumChildren()):
		child = root.getChildByIndex(i)
		if child.getName() != "_switchbord_config_":
			validateNamespaceCfg(child)

	return None

def readBox (box_entry):
	"""
	readBox: reads an arbitrary @BlackBox, with caching
	@box_entry: a box_entry conformant @AdmList element

	This function takes a box_entry element, and attempts to @getBox() it.
	If the @getBox() fails, it returns None. This allows configurations to
	fail silently over non-existant components, and is a general win. If
	it succedes, it attempts to read the box. If the read succedes, it writes
	to the cache box, if it is defined and @getBox() can find it. If the read
	fails, it reads from the cache box, if it is defined and @getBox can find
	it. Returns whatever Context was read, or None, on failure.

	returns: a Context, or None on failure
	"""
	validateBoxEntry(box_entry)

	# Fail silently if we don't have this box
	# This allows us to configure fpr undeployed systems.
	box = getBox(box_entry.getChildByName("box"))
	if box == None:
		return None

	context = box.read()

	# Try to load this box's cache
	try:
		cache = getBox(box_entry.getChildByName("cache"))
	except KeyError, e:
		cache = None

	# if the cache loads, do the right thing with it.
	if cache != None:
		if context != None:
			cache.write(context)
		else:
			context = cache.read()

	return context

def writeBox (box_entry, context):
	"""
	writeBox: writes to an arbitrary @BlackBox
	@box_entry: a box_entry conformant @AdmList element
	@context: an @AdmContext

	This function takes a box_entry element, and attempts to @getBox() it.
	If the @getBox() fails, it returns 0. This allows configurations to
	fail silently over non-existant components, and is a general win. If
	it succedes, it attempts to write the box, and returns the result of
	the write. The write will always return 0 on failure, or a positive
	non-zero integer on success.

	Specifics of which integer, and what it means, are box dependent.

	returns: 0 on failure, positive non-zero integer on success
	"""
	validateBoxEntry(box_entry)

	# Fail silently if we don't have this box
	# This allows us to configure fpr undeployed systems.
	box = getBox(box_entry.getChildByName("box"))
	if box == None:
		return 0

	return box.write(context)

class Switchboard:
	"""
	The Switchboard class provides a convienient collection of merge
	and cache logic, which interoperating with BlackBox modules and
	Alchemist Data Model elements forms the Alchemist Data Library.

	Switchboard instances are stateless, and can be reconfigured on
	the fly by altering their meta_context. However, since this is
	not the normal behaviour, and validation is very expensive, we
	only call validateMetaCtx() at init time. Modules altering the
	meta context outside that wish to validate more often can set
	validate = 1 on any method to force a validateMetaCtx call.

	The Switchboard deals with data in terms of Namespaces, which in this
	application are defined a ordered set of BlackBox supplied AdmContexts,
	their optional caches, the optional cache for the product of a cascade
	merge of the set, and an optional output set of consumers, specified as
	BlackBoxes.
	"""
	def __init__(self, meta_context = None, file_path = None):
		"""
		__init__: Initialize a Switchboard
		@self: this Switchboard instance
		@meta_context = None: a meta_context conforming AdmContext
		@file_path = None: a file path to load a meta_context from

		We used named parameters to specify which construction method
		we want. If they pass us a meta_context, we validate it and
		wire it up. If they pass us a file_path, we call the
		ReadContextFromFile function that the FileBlackBox module
		provided, validate the result, and wire it up. If we get
		nothing, we throw a ValueError exception.

		meta_context and file_path default to 'None'
		"""
		if meta_context != None:
			self.meta_context = meta_context
			validateMetaCtx(self.meta_context)
			return None

		if file_path != None:
			self.meta_context = ReadContextFromFile(file_path)
			validateMetaCtx(self.meta_context)
			return None

		raise ValueError, "Illegal Constructor parameters"

	def listNamespaces(self, validate = None):
		"""
		listNamespaces: list all Namespaces defined in the meta_context
		@self: this Switchboard instance
		@validate = None: a flag that can be set to force validation.

		returns: a list of all namespaces defined in the meta_context
		"""
		if validate:
			validateMetaCtx(self.meta_context)

		list = []
		root = self.meta_context.getDataRoot()
		for i in xrange(root.getNumChildren()):
			data_name = root.getChildByIndex(i).getName()
			if data_name != "_switchboard_config_":
				list.append(data_name)

		return list
		
	def readNamespaceCfg(self, name, validate = None):
		"""
		readNamespaceCfg: examine a namespace_cfg defined in the meta_context
		@self: this Switchboard instance
		@name: the name of the namespace you are requesting
		@validate = None: a flag that can be set to force validation.

		Gets the namespace_cfg from the meta_context, if it exists. Programs
		should always use this function, as it masks the reserved name,
		"_switchboard_config_", and will always work accross future changes
		in the meta_context format.
		"""
		if validate:
			validateMetaCtx(self.meta_context)

		if name == "_switchboard_config_":
			return None
		try:
			return self.meta_context.getDataByPath("/" + name)
		except KeyError, e:
			raise KeyError, "No such namespace"

	def cascadeNamespace(self, name, depth = None, validate = None):
		"""
		cascadeNamespace: cascade a namespace
		@self: this Switchboard instance
		@name: the name of a namespace to cascade
		@depth = None: an optional depth
		@validate = None: a flag that can be set to force validation.

		This function cascade merges a namespace's input set, and returns
		the result of the cascade. If a depth is specified, it cascades
		only to that depth, or the full set, which ever is least.

		To get the contexts to merge in the cascade, it performs a
		pullBox() call on each box_entry in the input_set, which may
		provide a cached copy, or may provide none at all. It cascades
		silently past empty pulls, and if it has nothing at the end, it
		builds a blank context, and gives you that.

		depth counting starts at 1, and goes up, in the same way that
		number of children starts at 1.
		"""
		if validate:
			validateMetaCtx(self.meta_context)

		namespace_cfg = self.readNamespaceCfg(name)

		input_set = namespace_cfg.getChildByName("input_set")

		# figure out how far to go.
		k = input_set.getNumChildren()
		if depth != None:
			k = min(depth, k)

		context_A = None
		# cascade merge the boxes
		for i in xrange(k):
			if context_A == None:
				# Search for a non-empty box
				context_A = readBox(input_set.getChildByIndex(i))
			else:
				context_B = readBox(input_set.getChildByIndex(i))
				if context_B != None:
					# We can't recover if this fails, so we dont catch the exception.
					# and we need the traceback to get back to the developers
					context_A = merge ("cascade_merge", 0, context_A, context_B)

		# Make sure we return something, even if it is an empty context.
		if context_A == None:
			context_A = Context(name = "cascade_merge", serial = 0)

		return context_A

	def isNamespaceDirty(self, name, validate = None):
		"""
		isNamespaceDirty: checks to see if a namespace is dirty
		"""
		if validate:
			validateMetaCtx(self.meta_context)

		namespace_cfg = self.readNamespaceCfg(name)

		input_set = namespace_cfg.getChildByName("input_set")
		for i in xrange(input_set.getNumChildren()):
			box_entry = input_set.getChildByIndex(i)

			# We fail silently on unavailable boxes
			box = getBox(box_entry.getChildByName("box"))
			if box == None:
				continue

			bversion = box.version()
			if bversion == None:
				continue

			# But we die on unavailable caches
			cache = getBox(box_entry.getChildByName("cache"))
			if cache == None:
				raise ValueError, "'cache' entry unavailable"

			cversion = cache.version()
			if cversion == None:
				# The box has not been cached, it must be dirty
				return 1

			if bversion > cversion:
				return 1

		return 0


	def readNamespace(self, name, force = None, validate = None):
		"""
		readNamespace: read a namespace
		@self: this Switchboard instance
		@name: the name of the namespace
		@force = None: an optional tag to force a fresh read
		@validate = None: a flag that can be set to force validation.

		This function reads a namespace from a full cascade of it's input set,
		or from its cache, if one is available. It does not write the cache.
		The force flag, if true, causes readNamespace to ignore its cache.

		returns: a flattend AdmContext.

		"""
		if validate:
			validateMetaCtx(self.meta_context)

		namespace_cfg = self.readNamespaceCfg(name)

		context = None
		# try to read the cache, but don't flatten it, as it is already flat
		if force == None:
			try:
				cache_box = getBox(namespace_cfg.getChildByName("cache"))
				if cache_box != None:
					context = cache_box.read()
			except KeyError, e:
				pass

		# if that failed, or we were forced, pull a cascade.
		if context == None:
			context = self.cascadeNamespace(name)
			if context != None:
				context.flatten()

		return context

	def writeNamespace(self, name, force = None, validate = None):
		"""
		writeNamespace: write a namespace to its consumers
		@self: this Switchboard instance
		@name: the name of the namespace to write.
		@force = None: an optional flag to force a cache flush
		@validate = None: a flag that can be set to force validation.

		This function pulls a namespaces cache, or a full cascade of the
		input set if the cache is empty, does not exist, or the force
		flag is set. It then writes out the cache (if it exists, and
		wasn't just read), and then writes to every box in the
		output set (if it exists).
		"""
		if validate:
			validateMetaCtx(self.meta_context)

		namespace_cfg = self.readNamespaceCfg(name)

		cache_read = None
		context = None

		# try to find the cache
		try:
			cache_box = getBox(namespace_cfg.getChildByName("cache"))
		except KeyError, e:
			cache_box = None

		# if we aren't forced, try to pull the cache
		if not force:
			if cache_box:
				context = cache_box.read()
				if context:
					cache_read = 1

		# if we still have nothing, cascade the namespace
		if context == None:
			context = self.cascadeNamespace(name)
			context.flatten()

		# make sure we dont write out a cache we just read
		if not cache_read and cache_box:
			# Version the context before we write it
			context.getIdentityRoot().setSerial(int(time.time()))
			cache_box.write(context)

		# write to the output set, if it exists.
		try:
			output_set = namespace_cfg.getChildByName("output_set")
			for i in xrange(output_set.getNumChildren()):
				writeBox(output_set.getChildByIndex(i), context)
		except KeyError, e:
			pass

		return context


if __name__ == '__main__':
	def test():
		ctx = Context(name='local', serial=1)
		data = ctx.getDataRoot()
		list = data.addChild(Data.ADM_TYPE_LIST, 'buz')
		for i in xrange(100000):
			list.addChild(Data.ADM_TYPE_INT, "n"+str(i)).setValue(i)

	test()
	#import cProfile
	#import pstats

	#cProfile.run('test()', 'Alchemist.py.prof')
	#p = pstats.Stats('Alchemist.py.prof')
	#p.sort_stats('time').print_stats()

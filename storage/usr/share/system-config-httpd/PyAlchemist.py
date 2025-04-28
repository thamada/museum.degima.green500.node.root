#! /usr/bin/python

## Alchemist - The core component of the system config tools package
## Copyright (C) 2000 Red Hat, Inc.
## Copyright (C) 2000-2009 Philipp Knirsch
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



import sys
import string
import gzip
from types import *
import xml.sax.handler



class Entity:
        """Base Entity Class for all our classes

        Our base Entity class from which all other objects are derived. All
	entities have 3 attributes.

        Derived classes may define other additional attributes and/or
	operations. C specific API calls are not implemented.

        Attributes:
	- @b name
		- Semantic name of the entity. (E.g. "apache" or "vh").
	- @b type
		- Entity type which specifies if it is e.g. a list or a scalar.
	- @b source
		- Place from where the entity came from (the origin context)
"""

	def __init__(self, n=''):
		"""
		Public constructor

		Initializes the base entity. Inits the name, type and source
		which are common attributes to all entities.

		@param self	Instance of class object
		@param n	Optional name of entity. Default is the empty
				string
"""
		self.name    = n
		"""Name of this Entity.

		Should be related to the purpose of the entity resp. it's use.
"""
		self.type    = None
		"""Type of this Entity.

		One of 'string' , 'base64' , 'int' , 'float' , 'bool' , 'copy' or 'list'
"""
		self.source  = None
		"""Source of this Entity.

		Usually something like "RHN" or "Local"
"""

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		@param	self	Instance of class object
		@return	New instance with copy of given object
"""
		n = Entity()
		n.copy(self)
		return n

	def copy(self, other=None):
		"""
		Copy operator

		The copy() method initializes the instance from another
		instance. Similart to the copy operator in C++.

		@param	self	Instance of class object
		@param	other	Instance of class object from which self is
				being initialized
"""
		if other == None:
			return self.__copy__()

		self.name   = other.name
		self.type   = other.type
		self.source = other.source

	def setName(self, n):
		"""
		Name attribute mutator method

		Mutator method for setting the name attribute of this entity.

		@param	self	Instance of class object
		@param	n	New name of this entity
		@see	getName()
"""
		self.name = n

	def getName(self):
		"""
		Name attribute accessor method

		Accessor method for getting the name of this entity.

		@param	self	Instance of class object
		@return	@c string Name of this Entity
		@see	setName()
"""
		return self.name

	def setType(self, t):
		"""
		Type attribute mutator method

		Mutator method for setting the type attribute of this entity.
		Valid types are the following:
			- string
			- base64
			- int
			- float
			- bool
			- copy
			- list

		@param	self	Instance of class object
		@param	t	New type of this entity
		@see	getType()
"""
		self.type = t

	def getType(self):
		"""
		Type attribute accessor method

		Accessor method for getting the type of this entity.

		@param	self	Instance of class object
		@return	@c string Type of this Entity
		@see setType()
"""
		return self.type

	def setSource(self, s):
		"""
		Source attribute mutator method

		Mutator method for setting the source attribute of this entity.
		A source is meant to be a unique identifier which specifies
		from where the information originated. Usually something like
		'RHN' or 'local' or 'proc' .

		@param	self	Instance of class object
		@param	s	New source of this entity
		@see setSource()
"""
		self.source = s

	def getSource(self):
		"""
		Source attribute accessor method

		Accessor method for getting the source of this entity.

		@param	self	Instance of class object
		@return	@c string Source of this Entity
		@see getSource()
"""
		return self.source

	def isIdentical(self, other):
		"""
		Identical comperator method

		Comperator method for evaluating if self is identical to other

		@param	self	Instance of class object
		@param	other	Instance of class object to compare with
		@return	@b bool Truth value if self is identical to other
"""
		return self == other

	def isAlive(self):
		"""
		Alive check

		Accessor method to verify if entity is alive.

		@param	self	Instance of class object
		@return	@b bool Truth value if self is alive
"""
		return True



class ContextHandler(xml.sax.handler.ContentHandler):
	"""
	XML SAX2 content handler for Contexts
"""
	def __init__(self, ctx, data, delete, id):
		self.ctx = ctx
		self.data = data
		self.delete = delete
		self.id = id
		self.currentity = None
		"""XML parser entity storage

		Reference to current entity during XML parsing.
"""
		self.currtype   = None
		"""XML parser type storage

		Type of current entity during XML parsing.
"""
		self.currstate  = ''
		self.currlevel  = 0

	def startElement(self, name, attrs):
		"""
		Private XML decoding SAX parser start element callback

		This is the wrapper callback method for our SAX parser for
		start elements. As we have to deal with 3 different types of
		information contained in the root element adm_context we use a
		form of state machine in order to know where we are and in turn
		what real start element method we have to call.

		The three different types of information contained in the
		root element of our XML encoded Context are these:

		  'delete'   -- A single delete set entry. Simple element which
				contains a path to be deleted. Multiple root
				entries may exits.
		  'id'       -- Identity tree element which describes the
				merge history of the Context. Only 1 root id
				element may exist.
		  'datatree' -- The "real" content of the Context. Here all the
				configuration information is stored. Only 1
				root datatree may exist.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of opening element
			'attrs'	-- Python dictionary of attributes of this element

		**SEE:**
			'' -- "Context.fromXML()":#Context.fromXML
			'' -- "Context.__deleteStartElement()":#Context.__deleteStartElement
			'' -- "Context.__idStartElement()":#Context.__idStartElement
			'' -- "Context.__dataStartElement()":#Context.__dataStartElement
"""
		if   self.currstate == '':
			if self.currlevel > 1:
				raise TypeError, 'Wrong level in root element parsing: '+str(self.currlevel)
			if   name == 'delete':
				self.currstate = 'delete'
				self.__deleteStartElement(name, attrs)
			elif name == 'id':
				self.__idStartElement(name, attrs)
				self.currstate = 'id'
				self.currlevel = self.currlevel + 1
			elif name == 'datatree':
				self.__dataStartElement(name, attrs)
				self.currstate = 'data'
				self.currlevel = self.currlevel + 1
			elif name == 'adm_context':
				self.currlevel = 1
			else:
				raise NameError, 'Root start element not one of delete, id, data or adm_context: '+name
		elif self.currstate == 'id':
			self.__idStartElement(name, attrs)
			self.currlevel = self.currlevel + 1
		elif self.currstate == 'data':
			self.__dataStartElement(name, attrs)
			self.currlevel = self.currlevel + 1
		else:
			raise TypeError, 'Unkown state of XML parser: '+self.currstate

	def endElement(self, name):
		"""
		Private XML decoding SAX parser end element callback

		Same as for the start element SAX parser callback method, it's
		again just a wrapper for our state machine. It's a lot easier
		as we only have to deal with closing elements and therefore
		no newly created entities or anything else complex.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of closing element (unused)

		**SEE:**
			'' -- "Context.fromXML()":#Context.fromXML
"""
		if   self.currstate == '':
			if name == 'adm_context':
				self.currlevel = self.currlevel - 1
			else:
				raise NameError, 'Root end element not one of delete or adm_context: '+name
		elif self.currstate == 'delete':
			self.__deleteEndElement(name)
			self.currstate = ''
		elif self.currstate == 'id':
			self.__idEndElement(name)
			self.currlevel = self.currlevel - 1
			if self.currlevel == 1:
				self.currentity = None
				self.currtype   = None
				self.currstate = ''
		elif self.currstate == 'data':
			self.__dataEndElement(name)
			self.currlevel = self.currlevel - 1
			if self.currlevel == 1:
				self.currentity = None
				self.currtype   = None
				self.currstate = ''
		else:
			raise TypeError, 'Unkown state of XML parser: '+self.currstate

        def characters(self, data):
		"""
		Private XML decoding SAX parser chardata callback

		The last of the three needed SAX parser callback methods this
		one handles the character data of an element. And again just
		like for the start element and end element callbacks this one
		is only a wrapper for the state machine.

		Currently char data is only used by the scalar data types, but
		we do in order to keep it correctly we do it in a well defined
		manner here.

		**PARAMS:**
			'self'	-- Instance of class object
			'data'	-- Character data of the current element

		**SEE:**
			'' -- "Context.fromXML()":#Context.fromXML
"""
		if   self.currstate == 'delete':
			self.__deleteCharData(data)
		elif self.currstate == 'id':
			self.__idCharData(data)
		elif self.currstate == 'data':
			self.__dataCharData(data)

	def __deleteStartElement(self, name, attrs):
		"""
		Private XML decoding SAX parser delete set start element callback

		Nothing has to be done here.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of opening element
			'attrs'	-- Python dictionary of attributes of this element

		**SEE:**
			'' -- "Context.__StartElement()":#Context.__StartElement
"""
		pass

	def __deleteEndElement(self, name):
		"""
		Private XML decoding SAX parser delete set end element callback

		Nothing has to be done here.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of closing element

		**SEE:**
			'' -- "Context.__EndElement()":#Context.__EndElement
"""
		pass

	def __deleteCharData(self, data):
		"""
		Private XML decoding SAX parser delete set chardata callback

		As the whole delete set handling is very simple, so are the
		state machine callback methods for it. This is actually the
		only method for the delete set doing anything. It just sets
		the delete set path value for the given chardata.

		**PARAMS:**
			'self'	-- Instance of class object
			'data'	-- Character data of the current element

		**SEE:**
			'' -- "Context.__CharData()":#Context.__CharData
"""
		self.setDelete(data)

	def __idStartElement(self, name, attrs):
		"""
		Private XML decoding SAX parser identity tree start element callback

		This SAX parser start element callback method is similar to the
		one for the data tree, only that it is less complex.

		The first identity element we find will be the identity of this
		Context. All other identity elements should appear in the tree
		under this first identity element and will be treated as the
		parents of this Context.

		All parent identites are handled the same way, so we can
		always use the same logic for the real parsing of the elements.

		The two differences between the data tree parser and this one
		are that the identity tree never contains character data and
		that we don't have the backwards reference as with our data
		tree.

		The first thing doesn't concern us, it just simplyfies the
		chardata callback method for the identity tree (basically
		it's empty).

		The second one though is a smaller problem as we need to climb
		up the tree again when an identity element has been processed.

		We do this by using the self.currentity variable as a
		dictionary of parents. That way it always contains all the
		parents of the current tree and we can easily trace back during
		sequential parsing.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of opening element
			'attrs'	-- Python dictionary of attributes of this element

		**SEE:**
			'' -- "Context.__StartElement()":#Context.__StartElement
"""
		if self.currentity == None:
			self.id.setName(attrs['NAME'])
			self.id.setSerial(attrs['SERIAL'])
			self.currentity = {}
			self.currentity[self.currlevel] = self.id
			return

		if name == 'null':
			return

		nid = Identity(attrs['NAME'], attrs['SERIAL'])

		if self.currentity[self.currlevel-1].getParentA() == None:
			self.currentity[self.currlevel-1].setParentA(nid)
		else:
			self.currentity[self.currlevel-1].setParentB(nid)

		self.currentity[self.currlevel] = nid

	def __idEndElement(self, name):
		"""
		Private XML decoding SAX parser identity tree end element callback

		Again a very simple method, as the end element callback hardly
		ever does anything really complicated. We just make sure here
		that the entity for the current level is reset so that if we
		ever have a damaged tree we will get an exception.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of closing element

		**SEE:**
			'' -- "Context.__EndElement()":#Context.__EndElement
"""
		if name == 'null':
			return
		self.currentity[self.currlevel] = None

	def __idCharData(self, data):
		"""
		Private XML decoding SAX parser identity tree chardata callback

		The SAX parser chardata callback for the identity tree doesn't
		do anything as we never store any information on the chardata
		for the identity tree but keep it all in attributes.

		**PARAMS:**
			'self'	-- Instance of class object
			'data'	-- Character data of the current element

		**SEE:**
			'' -- "Context.__CharData()":#Context.__CharData
"""
		pass

	def __dataStartElement(self, name, attrs):
		"""
		Private XML decoding SAX parser data start element callback

		SAX XML parser handler for start tags. Will be called for every
		start of an element in our XML stream.
		In order to keep symmetry with encoding and decoding we do a
		small trick here: The name of the Context is being encoded as
		the root element of our XML stream in toXML(). So the first
		element we encounter will be our Context name. Every other
		element contained inside this one will be part of the data List
		and parsed into that. Other than that we simply add a new child
		to the current data entity, set all attributes (depending on
		the type) and switch the current type and data entity to the
		newly created.
		Sanity checks should be but in to make sure that the XML stream
		meets the following conditions:
		 - Only data enities of type 'LIST' may contain other entities
		 - Only our supported data types should be allowed
		 - Only our supported attributes for the specific types should
		   be allowd
		This would basically be the sanity and verification step where
		we can verify that the data structure is well formed. This is
		different from the possible XML based DTD check which is
		application specific and not part of the Alchemist (actually
		currently not being done either).

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of opening element
			'attrs'	-- Python dictionary of attributes of this element

		**SEE:**
			'' -- "Context.fromXML()":#Context.fromXML
"""
		#
		# Check if we just started processing. In that case our current
		# entity will still be none and we do the following things:
		#  - Set the name of this Context to the name of the element as
		#    this is has been encoded that way.
		#  - Set the current entity to the root List to reflect that we
		#    are now actually beginning to parse the content.
		#  - Set the current type to 'LIST', which is what our root
		#    List should be ;)
		if self.currentity == None:
			self.ctx.setName(name)
			self.currentity = self.data
			self.currtype = 'LIST'
			return

		type  = attrs['TYPE']

		if attrs.has_key('VALUE'):
			value = attrs['VALUE']
		else:
			value = None

		child = self.currentity.addChild(type, name)

		if attrs.has_key('SOURCE'):
			child.setSource(attrs['SOURCE'])
		if attrs.has_key('PROTECTED'):
			child.setProtected(attrs['PROTECTED'])

		if type == 'LIST':
			if attrs.has_key('ANONYMOUS'):
				child.setAnonymous(attrs['ANONYMOUS'])
			if attrs.has_key('ATOMIC'):
				child.setAtomic(attrs['ATOMIC'])
			if attrs.has_key('PREPEND'):
				child.setPrepend(attrs['PREPEND'])
		else:
			child.setValue(value)

		self.currentity = child
		self.currtype   = type

        def __dataEndElement(self, name):
		"""
		Private XML decoding SAX parser data end element callback

		When we reach the end of an element we don't have to do an
		awfull lot anymore. The attributes have already been processed
		during the start of the element, the value of the entity has
		been processed in the __dataCharData() method, so the only
		thing we have to make sure here is to "go up" one level again.

		**PARAMS:**
			'self'	-- Instance of class object
			'name'	-- Name of closing element (unused)

		**SEE:**
			'' -- "Context.fromXML()":#Context.fromXML
"""
		self.currentity = self.currentity.getContainer()
		self.currtype   = self.currentity.getType()

        def __dataCharData(self, data):
		"""
		Private XML decoding SAX parser data chardata callback

		Here we actually set the value of our current data entity. This
		only happens for scalar data entities though, so if we should
		come in here for a list or even during the startup (which could
		happen) we simply ignore that data as Lists cannot contain
		anything else than other data entites and all character data
		therefor is simply filler stuff.

		**PARAMS:**
			'self'	-- Instance of class object
			'data'	-- Character data of the current element

		**SEE:**
			'' -- "Context.fromXML()":#Context.fromXML
"""
		if self.currentity == None:
			return

		if self.currtype == 'LIST':
			return

		self.currentity.setValue(data)



class Context(Entity):
	"""
	Root structure for our information storage

	A Context is our information "root" structure. Each merge will be done
	on a Context, which in turn will then merge the data trees of the two
	Contexts and update the merge history in the Identity tree.
"""
        def __init__ (self, name='', serial=0, ctx=None, xml=None):
		"""
		Public constructor

		Initializes all of our Context specific things. A Context
		contains a few more things than a simple entity:
        		'data'		-- A List of the contents of this
					context
        		'delete'	-- A python list of strings of
					references to be deleted
        		'id'		-- The Identity tree of this context
					(containing it's own Identity as root
					node)

		It also supports a copy constructore equivalent from C++ where 
        	you can specify another Context from which this one gets
		initialized. Otherwise an empty Context will be created with no
		name, a empty Identity and empty data and delete lists.

		**PARAMS:**
			'self'	-- Instance of class object
			'vals'	-- Dictionary of variable args. Parsed in order to decided what kind of constructor to use
"""
		Entity.__init__(self)
		self.setType('context')
		self.use_xmllib = 0
		"""XML LIB Sax parser usage flag

		Flag to indicate wether we want to use the slow but rocksolid
		xmllib XML parser or the PyExpat one.
"""
		self.data       = None
		"""List data container

		List container for complete data content of this Context.
"""
		self.delete     = None
		"""Python list of deletes

		Python list of strings of references to be deleted.
"""
		self.id         = None
		"""Identity tree of this Context

		Contains the complete merge history and the Identity of this
		Context.
"""

		if ctx != None:
			self.copy(ctx)
			return

		if xml != None:
			self.__init__(name='', serial=0)
			self.fromXML(xml)
			return

		if name != None and serial != None:
			self.setName(name)
			self.id     = Identity(self.getName(), serial)
			self.delete = []
			self.data   = ListData()
			self.data.setContainer(self.data)
			self.data.setSource(self.getName())
			self.data.setContext(self)
			return

		raise ContextError, "Illegal constructor parameters"

	def __getitem__(self, key):
		"""
		Implementation of Python sequence index accessor

		Override of __getitem__() operator for Python sequences.
		Basically the sequence accessor method for Python sequences.
		That way a Context can be handled similarily like a sequence.
		This allows us to write a little nicer looking code when
		accessing the data of a Context.

		**PARAMS:**
			'self'	-- Instance of class object
			'key'	-- Index to be accessed. One of 'data' ,
				'delete' or 'id'

		**RETURNS:**
			*ref*	-- Reference to the requested data

		**EXCEPTIONS:**
			*KeyError*	-- Raised if none of the valid keys was
					tried to accessed

		**SEE:**
			'' -- "Context.__setitem__()":#Context.__setitem__
"""
		if   key == 'data':
			return self.data
		elif key == 'delete':
			return self.delete
		elif key == 'id':
			return self.id
		else:
			raise KeyError

	def __setitem__(self, key, value):
	   	"""
		Implementation of Python sequence index mutator

		Override of __setitem__() operator for Python sequences. This
		is the mutator method for Python sequences. It shoudldn't be
		used too often as the behaviour hasn't been defined, but for
		symmetry reasons we provide it here.

		**PARAMS:**
			'self'	-- Instance of class object
			'key'	-- Index to be accessed. One of 'data' , 'delete' or 'id'
			'value'	-- Value to which the element at key should be set.

		**EXCEPTIONS:**
			*KeyError* -- Raised if none of the valid keys was tried to accessed

		**SEE:**
			'' -- "Context.__getitem__()":#Context.__getitem__
"""
		if   key == 'data':
			self.data = value
		elif key == 'delete':
			self.delete = value
		elif key == 'id':
			self.id = value
		else:
			raise KeyError

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Context* --	New instance with copy of given object
"""
		n = Context({'name':self.id.getName(), 'serial':self.id.getSerial()})
		n.copy(self)
		return n

	def copy(self, other=None):
		"""
		Copy operator

		Copy operator, like in the Entity class. First calls it's
		parent copy operator and then copies the rest of the data over
		to itself.

		**PARAMS:**
			'self'	-- Instance of class object
			'other'	-- Instance of Context to copy from
"""
		if other == None:
			return self.__copy__()

		Entity.copy(self, other)
		self.data   = other.data.__copy__()
		self.delete = other.delete[:]
		self.id     = other.id.__copy__()

	def create(self, n='', ser=0):
		"""
		Context creation method

		For completeness of the API we provide another way of creating
		a Context in the procedural way (not by using a constructor).

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Context* -- Newly created empty Context instance

		**SEE:**
			'' -- "Context.__init__()":#Context.__init__
"""
		return Context(n, ser)

	def merge(self, name, serial, other):
		"""
		Merthod to merge two contexts

		This method is the starting point for all merges. A merge
		should always be invoked by an application using the Context
		merge call, never on Lists alone.

		**PARAMS:**
			'self'	-- Instance of first Context to merge
			'serial -- Serial number of the context
			'other'	-- Instance of second Context to merge

		**RETURNS:**
			*Context* --	Newly created Context containing
					merge result

		**SEE:**
			'' -- "List.merge()":#List.merge
"""
		nc = self.__copy__()
		nc.setName(name)
		id = nc.getIdentityRoot()
		id.setSerial(serial)
		id.setName(name)
		id.setParentA(self.getIdentityRoot())
		id.setParentB(other.getIdentityRoot())

		for i in xrange(other.getNumDeletes()):
			try:
				c = nc.getDataByPath(other.getDelete(i))
				if c.isProtected() == 0:
					p = c.getContainer()
					p.delChild(c.getPos())
			except:
				nc.setDelete(other.getDelete(i))

		nc.getDataRoot().setSource(nc.getName())
		nc.data = nc.getDataRoot().merge(other.getDataRoot())

		return nc

	def flatten(self):
		"""
		Flatten resp. process a context

		Flattens or rather processes the Context and resolves all
		references and deletes. Usually called before merging two
		Contexts on both Contexts.

		**PARAMS:**
			'self'	-- Instance of Context to be flattened/processed
"""
		self.delete = []
		self.__flattenCopies(self.getDataRoot())

	def __flattenCopies(self, data):
		if data.getType() == Data.ADM_TYPE_LIST:
			i = 0
			while i < data.getNumChildren():
				child = data.getChildByIndex(i)
				if child.getType() == Data.ADM_TYPE_LIST:
					self.__flattenCopies(data.getChildByIndex(i))
				if child.getType() == Data.ADM_TYPE_COPY:
					data.delChild(child)
				i = i + 1

	def toXML(self):
		"""
		Public XML encoding method

		Our public interface for encoding the the complete Context
		to XML. Calls the internal private methods __idToXML(),
		__deleteToXML() and __dataToXML() which actually perform the
		real work for the specific parts. This method only outputs the
		XML header as that is pretty much content independant. :)

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*string* -- XML encoded string of this Context

		**SEE:**
			'' -- "Context.__idToXML()":#Context.__idToXML
			'' -- "Context.__deleteToXML()":#Context.__deleteToXML
			'' -- "Context.__dataToXML()":#Context.__dataToXML
"""
		ret = '<?xml version="1.0"?>\n'
		ret = ret + '<adm_context VERSION="0">\n'
		ret = ret + self.__idToXML(self.getIdentityRoot())
		ret = ret + self.__deleteToXML()
		ret = ret + self.__dataToXML(self.getDataRoot())
		ret = ret + '</adm_context>\n'
		return ret

	def __idToXML(self, data, depth=1):
		"""
		Private XML identity tree encoding method

		This method encods our identity tree the same way the C
		Alchemist does. Similar to the __dataToXML() method only a
		little simpler. Just as there subtrees are encoded exactly the
		same as our main tree. This symmetry makes creation really
		easy.

		**PARAMS:**
			'self'	-- Instance of class object
			'data'	-- Identity tree to be encoded
			'depth'	-- Current list depth

		**RETURNS:**
			*string* -- XML encoded string of this Identity tree

		**SEE:**
			'' -- "Context.toXML()":#Context.toXML
"""
		if data == None:
			return '    '*depth + '<null/>\n'

		ret = '    '*depth + '<id NAME="' + data.getName() + '" SERIAL="' + str(data.getSerial()) + '">\n'
		ret = ret + self.__idToXML(data.getParentA(), depth+1)
		ret = ret + self.__idToXML(data.getParentB(), depth+1)
		ret = ret + '    '*depth + '</id>\n'
		return ret

	def __deleteToXML(self):
		"""
		Private XML delete set encoding method

		XML encodes all delete sets of this Context. Extremely simple,
		just creates a list of <delete> elements containing the
		references.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*string* -- XML encoded string of this delete set

		**SEE:**
			'' -- "Context.toXML()":#Context.toXML
"""
		ret = ''
		for i in xrange(self.getNumDeletes()):
			ret = ret +  '    <delete PATH="' + self.getDelete(i) + '"/>\n'
		return ret

	def __dataToXML(self, data, depth=1):
		"""
		Private XML data encoding method

		Private method which recursively creates our XML encoded output
		of our internal data structure. Doesn't use any of the xmllib
		or modules but does it on the fly on it's own.

		**PARAMS:**
			'self'	-- Instance of class object
			'data'	-- Data object to be encoded
			'depth'	-- Current list depth

		**RETURNS:**
			*string* -- XML encoded string of this Data object

		**SEE:**
			'' -- "Context.toXML()":#Context.toXML
"""
		ret = '    '*depth + '<'

		if depth == 1:
			ret = ret + 'datatree'
		else:
			ret = ret + data.getName()
			ret = ret + ' TYPE="' + Data.ADM_XML_TYPES[data.getType()] + '"'

		if depth > 1 and data.getSource() != None and data.getSource() != self.getName():
			ret = ret + ' SOURCE="' + data.getSource() + '"'
		if data.isProtected():
			ret = ret + ' PROTECTED="TRUE"'

		if data.getType() == Data.ADM_TYPE_LIST:
			if data.isAnonymous():
				ret = ret + ' ANONYMOUS="TRUE"'
			if data.isAtomic():
				ret = ret + ' ATOMIC="TRUE"'
			if data.isPrepend():
				ret = ret + ' PREPEND="TRUE"'
			ret = ret + '>\n'
			for index in range(data.getNumChildren()):
				ret = ret + self.__dataToXML( \
					data.getChildByIndex(index), depth + 1)
			ret = ret + '    '*depth + '</'
			if depth == 1:
				ret = ret + 'datatree'
			else:
				ret = ret + data.getName()
			ret = ret + '>\n'
		else:
			ret = ret + ' VALUE="' + str(data.getValue()) + '"/>\n'

		return ret

	def fromXML(self, xmlstr):
		"""
		Public XML decoding method

		The symmetrical call for XML decoding is fromXML(). That one
		actually uses a SAX parser to do the work. The magic lies in
		the handle methods we set for the parsing. It's fairly
		efficient and quick by still keeping it pretty simple.

		**PARAMS:**
			'self'	-- Instance of class object
			'xml'	-- XML string of data to be decoded into this
				Context

		**SEE:**
			'' -- "Context.__StartElement()":#Context.__StartElement
			'' -- "Context.__EndElement()":#Context.__EndElement
			'' -- "Context.__CharData()":#Context.__CharData
"""
		p = xml.sax.make_parser()
		handler = ContextHandler(self, self.data, self.delete, self.id)
		p.setContentHandler(handler)
		p.feed(xmlstr)

	def setDelete(self, ref):
		"""
		Delete set mutator method

		Mutator method for delete set of this Context. As due to
		efficiency we don't want to keep the delete references inside
		of our data tree we store them inside a simple Python list. A
		delete reference can only appear once per Context, therefore we
		only add it once to the delete list.

		**PARAMS:**
			'self'	-- Instance of class object
			'ref'	-- Reference to data entity to be deleted

		**SEE:**
			'' -- "Context.getDelete()":#Context.getDelete
			'' -- "Context.clearDeleteByIndex()":#Context.clearDeleteByIndex
			'' -- "Context.clearDeleteByString()":#Context.clearDeleteByString
			'' -- "Context.getNumDeletes()":#Context.getNumDeletes
"""
		if self.delete.count(ref) > 0:
			return

		self.delete.append(ref)

	def getDelete(self, pos):
		"""
		Delete set accessor method

		Accessor method by index for delete se of this Context. Simply
		returns the reference at the given position. Might raise a
		KeyError exception in case we try to access a non existing
		delete reference.

		**PARAMS:**
			'self'	-- Instance of class object
			'pos'	-- Index of delete reference to be returned

		**RETURNS:**
			*string* -- String of reference of delete set at given position

		**EXCEPTIONS:**
			*KeyError* -- Raised if index is out of bounds

		**SEE:**
			'' -- "Context.setDelete()":#Context.setDelete
			'' -- "Context.clearDeleteByIndex()":#Context.clearDeleteByIndex
			'' -- "Context.clearDeleteByString()":#Context.clearDeleteByString
			'' -- "Context.getNumDeletes()":#Context.getNumDeletes
"""
		return self.delete[pos]

	def clearDeleteByIndex(self, idx):
		"""
		Delete set removal by index method

		Removes a delete reference at a certain position from the
		delete set.

		**PARAMS:**
			'self'	-- Instance of class object
			'idx'	-- Index of the delete reference to be removed

		**EXCEPTIONS:**
			*KeyError* -- Raised if index is out of bounds

		**SEE:**
			'' -- "Context.setDelete()":#Context.setDelete
			'' -- "Context.getDelete()":#Context.getDelete
			'' -- "Context.clearDeleteByString()":#Context.clearDeleteByString
			'' -- "Context.getNumDeletes()":#Context.getNumDeletes
"""
		self.delete.pop(idx)

	def clearDeleteByString(self, ref):
		"""
		Delete set removal by name method

		Removes a delete reference with a certain name from the delete
		set.

		**PARAMS:**
			'self'	-- Instance of class object
			'ref'	-- Reference name to be deleted from the delete set

		**EXCEPTIONS:**
			*KeyError* -- Raised if index is out of bounds

		**SEE:**
			'' -- "Context.setDelete()":#Context.setDelete
			'' -- "Context.getDelete()":#Context.getDelete
			'' -- "Context.clearDeleteByIndex()":#Context.clearDeleteByIndex
			'' -- "Context.getNumDeletes()":#Context.getNumDeletes
"""
		self.delete.remove(ref)

	def getNumDeletes(self):
		"""
		Number of delete set entries aggregate method

		Aggregation method to return the number of elements in our
		delete set.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*int*	-- Number of elements in our delete set

		**SEE:**
			'' -- "Context.setDelete()":#Context.setDelete
			'' -- "Context.getDelete()":#Context.getDelete
			'' -- "Context.clearDeleteByIndex()":#Context.clearDeleteByIndex
			'' -- "Context.clearDeleteByString()":#Context.clearDeleteByString
"""
		return len(self.delete)

	def getIdentityRoot(self):
		"""
		Identity root accessor method

		Accessor method for the Identity tree of this Context. The
		Identity tree, or short id, of a Context is simply speaking
		it's merge history. If a Context is created its Identity tree
		will contain only single Identity with no parents. If this
		Context is being involved in some mergeing later one it's
		Identity will be either updated or (if it is a parent of a
		merge) will be part of the parents of a merged Context.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Identity* -- Root node of Identity tree of this Context

		**SEE:**
			'' -- "Identity":#Identity
"""
		return self.id

	def getDataRoot(self):
		"""
		Data root accessor method

		Accessor method for the root List of this Context. The root
		List contains all data stored inside a context and can never be
		deleted. The root List has a couple of properties that make it
		a little unique (although it is still a normal List):

		 - The parent of the root List is the root List itself.
		 - The name of the root List is "". This is a reserved name for
			the root List.
		 - The root List is created during creation of the associated
			Context and is therefore always connected with that
			Context.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*List* -- Root node of data List of this Context

		**SEE:**
			'' -- "List":#List
"""
		return self.data

	def getDataByPath(self, path):
		"""
		Data entity accessor by path

		In order to have an easy interface to access data entities of
		our data set in the tree we provide an additional access
		method where we can specify the complete path into our tree
		at which we want to access an element.

		**PARAMS:**
			'self'	-- Instance of class object
			'path'	-- Path to data entity we want to access

		**RETURNS:**
			*Data*	-- Reference to Data entity pointed to by path

		**EXCEPTIONS:**
			*KeyError* -- Raised if no entity with that path exists

		**SEE:**
			'' -- "List.__getitem__()":#List.__getitem__
"""
		if path[0] != '/':
			raise KeyError

		keys = string.split(path[1:], '/')
		data = self.getDataRoot()
		for i in keys:
			data = data[i]

		return data



class Identity(Entity):
	"""
	Identity information of a Context

The Identity class is used for merge contexts and merge contex
identification. Each Context has one unique Identity and (if it is the product
of a merge) has the corresponding Identities as parents (A and B).
That way we sort of build the merge history tree from ground up and can
later on see what was merged and when.

Example:
            ID1     ID2
              \     /
               \   /
                ID4    ID3
                  \    /
                   \  /
                    ID5
"""
	def __init__(self, n='', serial=0):
		"""
		Public constructor

		Initializes the base entity. Inits the name, type and source
		which are common attributes to all entities.

		**PARAMS:**
			'self'	--	Instance of class object
			'n'	--	Optional name of Identity. Default is
					the empty string
"""
		Entity.__init__(self, n)
		self.setType('id')
		self.parentA = None
		"""First parent of this Identity

		Each Identity has up to two parents. This attribute contains
		the first parent of the Identity.
"""
		self.parentB = None
		"""Second parent of this Identity

		The other possible parent of the Identity. Using both parents
		we have sorft of a reversed merge tree (upside down).
"""
		self.serial  = serial
		"""Serial number of the Identity

		Contains the serial number of an Identity. Should be unique
		but it's up to the Identity and the application to set and use
		it, it's currently not used internally by the algorithms.
"""

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Identity* --	New instance with copy of given object
"""
		n = Identity()
		n.copy(self)
		return n

	def copy(self, other=None):
		"""
		Copy operator

		Data entity copy operator. Similar to the copy operator of C++,
		this one takes 2 arguments and copies the other into this
		(self).

		**PARAMS:**
			'self'	-- Instance of class object
			'other'	-- Instance of Identity to copy from
"""
		if other == None:
			return self.__copy__()

		Entity.copy(self, other)
		self.parentA = other.parentA
		self.parentB = other.parentB
		self.serial  = other.serial

	def setParentA(self, p):
		"""
		parentA attribute mutator method

		Mutator method to set the first parent of this Identity.

		**PARAMS:**
			'self'	-- Instance of class object
			'p'	-- Reference to Identity object of first parent

		**SEE:**
			'' -- "Identity.getParentA()":#Identity.getParentA
"""
		self.parentA = p

	def getParentA(self):
		"""
		parentA attribute accessor method

		Accessor method for first parent of this Identity.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*ref*	-- Reference to Identity object of first parent

		**SEE:**
			'' -- "Identity.setParentA()":#Identity.setParentA
"""
		return self.parentA

	def setParentB(self, p):
		"""
		parentB attribute mutator method

		Mutator method to set the second parent of this Identity.

		**PARAMS:**
			'self'	-- Instance of class object
			'p'	-- Reference to Identity object of second parent

		**SEE:**
			'' -- "Identity.getParentB()":#Identity.getParentB
"""
		self.parentB = p

	def getParentB(self):
		"""
		parentB attribute accessor method

		Accessor method for second parent of this Identity.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*ref*	-- Reference to Identity object of second parent

		**SEE:**
			'' -- "Identity.setParentB()":#Identity.setParentB
"""
		return self.parentB

	def setSerial(self, s):
		"""
		serial number attribute mutator mthod

		Mutator method to set the serial number of this Identity.

		**PARAMS:**
			'self'	-- Instance of class object
			's'	-- New serial number of this Identity

		**SEE:**
			'' -- "Identity.getSerial()":#Identity.getSerial
"""
		self.serial = s

	def getSerial(self):
		"""
		serial number attribute accessor mthod

		Accessor method for serial number of this Identity.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*int*	-- Serial number of this Identity

		**SEE:**
			'' -- "Identity.setSerial()":#Identity.setSerial
"""
		return self.serial



class Data(Entity):
	"""
	Base Data Entity class

The Data class represents an entity which will actually contain data
and appear only in the data tree of a Context. These will be scalar types and
lists.

Each Data entity will have several common attributes and the accompanying
mutator/accessor methods.

The following common attributes for Data entities exist in addition to the
Entity attributes:

                  'parent'      --      Parent of this Data entity
                  'context'     --      Context of this Data entity
                  'protected'   --      Flag wether this Data entity is
                                        protected or not
                  'value'       --      Value of this Data entity
"""
	## From alchemist.h:
	ADM_TYPE_UNKNOWN = 0
	"""Alchemist Data Model unknown type constant
"""
	ADM_TYPE_LIST    = 1
	"""Alchemist Data Model list type constant
"""
	ADM_TYPE_COPY    = 2
	"""Alchemist Data Model copy type constant
"""
	ADM_TYPE_INT     = 3
	"""Alchemist Data Model int type constant
"""
	ADM_TYPE_FLOAT   = 4
	"""Alchemist Data Model float  type constant
"""
	ADM_TYPE_BOOL    = 5
	"""Alchemist Data Model bool type constant
"""
	ADM_TYPE_STRING  = 6
	"""Alchemist Data Model string type constant
"""
	ADM_TYPE_BASE64  = 7
	"""Alchemist Data Model base64 type constant
"""
	ADM_XML_TYPES    = ('UNKNOWN', 'LIST', 'COPY', 'INT', 'FLOAT', 'BOOL', 'STRING', 'BASE64')
	"""Alchemist Data Model XML encoded data type list
"""

	def __init__(self, n=''):
		"""
		Public constructor

		Initializes data entity specific attributes. Additional to the
		Entity attributes these are the new ones:

		  'parent'	--	Parent of this Data entity
		  'context'	--	Context of this Data entity
		  'protected'	--	Flag wether this Data entity is
					protected or not
		  'value'	--	Value of this Data entity

		**PARAMS:**
			'self'	--	Instance of class object
			'n'	--	Optional name of Identity. Default is
					the empty string
"""
		Entity.__init__(self, n)
		self.parent    = None
		"""Parent of this Data entity

		The parent attribute contains a reference to a Data entity
		which contains this object. That way a Data entity can easily
		walk the complete data tree up and downwards. Every Data entity
		has a parent which has to be a List. The only slightly special
		case is the root List of a Context. That List has itself as a
		parent. That way the rule holds for every Data entity and we
		can easily check wether we are at the root List or not (by
		comparing the parent with the current object or by checking
		wether the name is "" as that is the reserved name of the
		root List entity).
"""
		self.context   = None
		"""Context of this Data entity

		Each Data entity has to be linked/contained to/in a Context.
		As children usually get added to a Context's content via the
		addChild() method of the List data type it is automatically
		linked there. No Data entity should exists in "empty" space,
		meaning having no parent or not linked to any context.
"""
		self.protected = 0
		"""Flag wether this Data entity is protected or not

		The protected attribute is the first Data entity and merge
		algorithm specific attribute. It is used to specify wether a
		Data entity may be overwritten or not. If it is set then the
		Data entity will not be modified during merging. For List
		entities this means that if the List is protected no changes
		whatsoever will be done to it during a merge which effectively
		then disables merges with this List. For scalar/atmoic values
		this has the logical behaviour of a protected value not being
		overwritable and therefore winning during a merge.
"""
		self.value     = None
		"""Value of this Data entity

		The value attribute is also common to all Data entities,
		although for some entities this doesn't have a real meaning,
		e.g. for Lists. Usually though it will contain the value to
		which the Data entity has been set. Each derived class may
		do verifications during the setValue() method in order to
		allow only legal values. This is not done for the general
		implementation however as there are no boundaries for the
		general case.
"""

	def __copy__(self):
		n = Data()
		n.copy(self)
		return n

	def copy(self, other=None):
		"""
		Copy operator

		Data entity copy operator. Similar to the copy operator of C++,
		this one takes 2 arguments and copies the other into this
		(self).

		**PARAMS:**
			'self'	-- Instance of class object
			'other'	-- Instance of Context to copy from
"""
		if other == None:
			return self.__copy__()

		Entity.copy(self, other)
		self.parent    = other.parent
		self.context   = other.context
		self.protected = other.protected
		self.value     = other.value

	def merge(self, other):
		"""
		Data entity merge method

		In order to have a unified way of merging without having to
		worry which data type we are trying to merge we use the simple
		OO technique of basic class implementations and overrides in
		derived classes for special data types (like Lists). The basic
		implementation returns a copy of either self or other,
		depending on the protected status of self.

		**PARAMS:**
			'self'	-- Instance of first data entity to merge
			'other'	-- Instance of second data entity to merge with

		**RETURNS:**
			*Data*	-- A reference to a copy of either self (if
				protected) or other
"""
		if self.isProtected():
			return self.__copy__()
		else:
			return other.__copy__()

	def setContainer(self, p):
		"""
		Container attribute mutator method

		Mutator method to set the container of this Data entity. This
		is valid for all Data enties as they need to have a parent.
		The only special case is the root Data entity of a Context.
		The parent of that Data entity is itself.

		**PARAMS:**
			'self'	-- Instance of class object
			'p'	-- Reference to Data object of container

		**SEE:**
			'' -- "Data.getContainer()":#Data.getContainer
"""
		self.parent = p

	def getContainer(self):
		"""
		Container attribute accessor method

		Accessor method to get the reference to the Data object of the
		container of the this object.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Data*	-- A reference to the container Data entity of
				this object

		**SEE:**
			'' -- "Data.setContainer()":#Data.setContainer
"""
		return self.parent

	def setContext(self, c):
		"""
		Context attribute mutator method

		Mutator method to set the Context in which this Data entity
		resides. Each Data entity has to exist in a Context (linked
		with it). If a Data entity is created it's always done with
		the addChild() method of our List class which will
		automatically link it to the Context to which the List belongs
		to which we add this new Data entity.

		**PARAMS:**
			'self'	-- Instance of class object
			'c'	-- Reference to Context object to which we link
				this object

		**SEE:**
			'' -- "Data.getContext()":#Data.getContext
"""
		self.context = c

	def getContext(self):
		"""
		Context attribute accessor method

		Accessor method to get the reference to the Context object to
		which this object is linked.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Context* -- A reference to the Context object to which
				this object is linked

		**SEE:**
			'' -- "Data.setContext()":#Data.setContext
"""
		return self.context

	def setProtected(self, f):
		"""
		Protected attribute mutator method

		Mutator method to set the protected flag for this Data entity.

		**PARAMS:**
			'self'	-- Instance of class object
			'f'	-- Boolean wether the Data object should be
				protected or not

		**SEE:**
			'' -- "Data.getProtected()":#Data.getProtected
"""
		self.protected = f

	def isProtected(self):
		"""
		Protected attribute validation method

		Validation method to check wether this Data entity is protected
		or not. A protected Data entity may not be overwritten and a
		merge with it therefor will return a copy of iself only.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Bool*	-- Boolean indication wether this Data object
				is protected or not

		**SEE:**
			'' -- "Data.setProtected()":#Data.setProtected
"""
		return self.protected

	def setValue(self, v):
		"""
		Value attribute mutator method

		Mutator method to set the value of this Data entity. It's
		basically up to the application to decide what to put in here,
		but a derived Data entity might implement a check here to
		verify the input and reject it if it is not valid.

		**PARAMS:**
			'self'	-- Instance of class object
			'v'	-- Value which should be set for this Data
				object

		**SEE:**
			'' -- "Data.getValue()":#Data.getValue
"""
		self.value = v

	def getValue(self):
		"""
		Value attribute accessor method

		Accessor method to get the value for this Data object. Some
		Data entites don't actually have values, like the List entity,
		so a value might have not actual meaning for some Data
		entities.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*ref*	-- A reference to the value for this Data
				object

		**SEE:**
			'' -- "Data.setValue()":#Data.setValue
"""
		return self.value

	def getPos(self):
		"""
		Position index in container

		As each Data entity is contained in a container and we often
		have to access entities by their position this is another
		convenience method which returns the position of a Data
		entity inside it's parent container.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*int*	-- Position of this object in it's parent.

		**EXCEPTIONS:**
			*NameError* -- Raised if entity has no parent
			*IndexError* -- Raised if entity is not a child of its parent

		**SEE:**
			'' -- "List.getChildByIndex()":#List.getChildByIndex

"""
		parent = self.getContainer()
		if parent == None:
			raise NameError, 'Data entity has no parent.'

		for i in xrange(parent.getNumChildren()):
			if parent.getChildByIndex(i) is self:
				return i

		raise IndexError

	def unlink(self):
		"""
		Data removal method

		Removes this data element from it's parent
"""
		parent = self.getContainer()
		if parent == None:
			raise NameError, 'Data entity has no parent.'

		parent.delChild(self)



class ListData(Data):
	"""
	List Data Entity class

The List entity is probably our single most important entity and data type
so we have to take care to do a pretty good (and fast) job with it.
Lists will be used as our general container type for all data we operate on.
It is basically a ordered set of entities with some special attributes:

  'anoymous'	--	An anonymous List is a List which may contain children
			with equal names. Children in an anonymous List cannot
			be referenced (and therefore not deleted either).
			During a merge equally named children will not be
			overwritten but appended.
			Handled by the List itself.

  'atomic'	--	Specifies that during a merge this list will either be
			replaced completely or not be changed (sort of a
			scalar-ization of a list).
			Only used by merge algorithm, not by the List itself.

  'prepend'	--	Defines wether during a merge the children of this List
			should appear at the front or at the back of the
			merged context.
			Only used by merge algorithm, not by the List itself.


Internally we use some very fancy data structures in order to achive the speed
we need and to offer constant insert, find and delete operation times ( O(1) is
guaranteed with this implementation for most of our API methods (With the
exception of delChild(), but this shouldn't be called that often anyway)).
"""
	def __init__(self, n=''):
		"""
		Public constructor

		Initilaizes the various List related attributes. Additional to
		the Entity and Data class attributes are the following
		attributes:

		  Anonymous	-- Specifies wether this List is an anonymous
				List or not.
		  Atomic	-- Specifies wether this List is an atmoic List
				or not.
		  Prepend	-- Specifies wether this List should be
				prepended or not.
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_LIST)
		self.anonymous = 0
		"""Anonymous List flag

		Indicates wether this List is anonymous. Anonymous Lists may
		contain multiple children with the same name. There can be no
		reference to a child inside an anonymous List.
"""
		self.atomic    = 0
		"""Atomic List flag

		Indicates wether this List is atomic. Atomic List do not merge
		their contents but rather are either replaced completely or
		are not changed at all. Or to put it differently, they merge
		like atomic scalars, either one or the other wins.
"""
		self.prepend   = 0
		"""Prepend List flag

		Indicates wether a List is set to prepend. A List that is set
		to prepend will appear at the front of the merge List during a
		merge operation.
"""
		self.pvalue    = []
		"""Python list of references to children by position (index)

		This python list contains references to all children. Due to
		the nature of lists in Python they are accessible only by index
		resp. position. This one is needed for indexed access to
		children.
"""
		self.nvalue    = {}
		"""Python dictionary with names containing lists of references to children.

		A little more complicated structure to offer fast access to
		the children by name and optionally the n-th child with the
		same name. This enables to to work efficiently based on names
		even with anonymous Lists.
"""

	def __len__(self):
		"""
		Overloaded Python sequence length operator

		Returns the number of children of this list. Overloads the
		Python operator for that so that we can use our List class just
		like a Python sequence.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*int*	-- Number of children of this List
"""
		return self.getNumChildren()

	def __getitem__(self, key):
		"""
		Python sequence accessor operator overload

		In order to have a nice interface to our Lists we not only
		provide the standard defined API but also the Python specific
		seqeuence index accessor operator with which we can access the
		children of a list in the following manner:

		  *integer*	--	Access the n-th element of the List
		  *string*	--	Access the first child with given name
		  *string/integer* --	Access the n-th child with given name

		Especially the last one is quite nice as it allows us to easily
		walk anonymous Lists (to be explained later).

		**PARAMS:**
			'self'	-- Instance of class object
			'key'	-- Child index we want to access

		**RETURNS:**
			*Data*	-- Reference to the child specified by the
				given key

		**EXCEPTIONS:**
			*KeyError*	-- Raised if index is out of bounds or
					invalid
"""
		if type(key) == StringType:
			return self.getChildByName(key)
		else:
			return self.getChildByIndex(key)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*List* --	New instance with copy of given object
"""
		n = ListData()
		n.copy(self)
		return n

	def copy(self, other=None):
		"""
		Copy operator

		List entity copy operator. Similar to the copy operator of C++,
		this one takes 2 arguments and copies the other into this
		(self). Special case for List type as we need to copy all
		the children as well.

		**PARAMS:**
			'self'	-- Instance of class object
			'other'	-- Instance of Context to copy from
"""
		if other == None:
			return self.__copy__()

		Data.copy(self, other)
		self.parent    = other.parent
		self.context   = other.context
		self.protected = other.protected
		self.anonymous = other.anonymous
		self.atomic    = other.atomic
		self.prepend   = other.prepend

		for i in range(other.getNumChildren()):
			self.addChild(other.getChildByIndex(i).__copy__())

	#
	# This is the engine core. The basic List merging is being done in
	# this method, based on the various attributes and logic operations
	# defined upon them.
	#
	# @params	self	List instance of first List to be merged
	# @params	other	List instance of second List to be merged
	# @returns	Merged List with self having priority over other
	#
	def merge(self, other):
		"""
		List merge method

		This is probably the single most important method of the whole
		Alchemist. It merges two given List objects and returns the
		merged result.

		The logic is pretty straight forward and defined by the setting
		of the various attributes of the given Lists:

		 - If self is protected return a copy of self.
		 - If self is atomic but not protected return a copy of other.
		 - Set the insertion point according to the prepend attribute
		   of other.
		 - If self is anonymous simply insert all children of other at
		   the insertion point and return the new List.
		 - If self is not anonymous copy self to a new List and for
		   each element in other check wether it exists in self or not
		   and merge the two and put the result in place.
		   All remaining elements of other are simply inserted at the
		   insertion point.

		The whole thing sounds more complex than it is, we just have to
		be very carefull to do the right thing for the various
		combinations of attributes.

		**PARAMS:**
			'self'	-- Instance of List object to be merged
			'other'	-- Instance of List object to merge with

		**RETURNS:**
			*List*	-- New List with merge result of the two Lists
"""
		if self.getType() != other.getType():
			raise TypeError, "Data types of entites don't match: "+self.getType()+" != "+other.getType()

		if self.isProtected():
			return self.__copy__()

		if self.isAtomic():
			return other.__copy__()

		if other.isPrepend():
			p = 0
		else:
			p = self.getNumChildren()

		nl = self

		if self.isAnonymous():
			for i in range(other.getNumChildren()):
				oi = other.getChildByIndex(i)
				if other.isPrepend():
					nl.addChild(oi.__copy__(), pos=p)
				else:
					nl.addChild(oi.__copy__())
				p = p + 1
		else:
			for i in range(other.getNumChildren()):
				oi = other.getChildByIndex(i)
				try:
					c = nl.getChildByName(oi.getName())
					c = c.merge(oi)
					nl.addChild(c, pos=p)
					p = p + 1
				except KeyError:
					nl.addChild(oi, pos=p)
					p = p + 1

		return nl

	def setAnonymous(self, f):
		"""
		Anonymous attribute mutator method

		Mutator method for the anonymous flag of this List. An
		anonymous List is a List which can contain multiple children
		with the same name.

		There are a couple of restrictions on anonymous Lists:

		 - No references can be made to children inside an anonymous
		   List.
		 - As a result no delete can be done on a single child inside
		   an anonymous List.
		 - Merges between anonymous Lists will always result in simply
		   pre- or appending the second List to the first List.
		 - Anonymous Lists can logically not be reverted to non
		   anonymous Lists.

		**PARAMS:**
			'self'	-- Instance of class object
			'f'	-- Flag wether the List should be anonymous or
				not

		**SEE:**
			'' -- "List.isAnonymous()":#List.isAnonymous
"""
		self.anonymous = f

	def isAnonymous(self):
		"""
		Anonymous attribute validation method

		Validation method to check wether this List entity is anonymous
		or not.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Bool*	-- Boolean indication wether this List object
				is anonymous or not

		**SEE:**
			'' -- "List.setAnonymous()":#List.setAnonymous
"""
		return self.anonymous

	def setAtomic(self, f):
		"""
		Atomic attribute mutator method

		Mutator method for the atomic flag of this List. An atmoic List
		is bascially a List that behaves like an atomic scalar data
		type. Therefore during merges it is either completely replaced
		or mot changed at all.

		**PARAMS:**
			'self'	-- Instance of class object
			'f'	-- Flag wether the List should be atomic or not

		**SEE:**
			'' -- "List.isAtomic()":#List.isAtomic
"""
		self.atomic = f

	def isAtomic(self):
		"""
		Atomic attribute validation method

		Validation method to check wether this List entity is atomic or
		not.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Bool*	-- Boolean indication wether this List object
				is atomic or not

		**SEE:**
			'' -- "List.setAtomic()":#List.setAtomic
"""
		return self.atomic

	def setPrepend(self, f):
		"""
		Prepend attribute mutator method

		Mutator method for the prepend flag of this List. This
		attribute again affects the merge beahviour of the List. During
		a merge if that List is set to prepend all elements will be
		put in front instead of being appended. 

		Usually the second List of a merge decides wether it will be
		prepended or not.

		Also this logically will only have an effect if the first List
		is neither protected (in which case the second List will be
		ignored completely) nor atomic (which would produce a copy of
		either the first or the second List).

		**PARAMS:**
			'self'	-- Instance of class object
			'f'	-- Flag wether the List should be set to
				prepend or not

		**SEE:**
			'' -- "List.isPrepend()":#List.isPrepend
"""
		self.prepend = f

	def isPrepend(self):
		"""
		Prepend attribute validation method

		Validation method to check wether this List entity is set to
		prepend or not.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*Bool*	-- Boolean indication wether this List object
				is set to prepend or not

		**SEE:**
			'' -- "List.setPrepend()":#List.setPrepend
"""
		return self.prepend

	def addChild(self, t, n='', v='', pos=-1):
		"""
		Add a child to the List object

		This method is our main interface to add new children to a
		List. By API definition it appends a new child with the given
		type, optional name and optional value at the end of the List.

		We have exteneded the Python interface with 2 additional
		features which are NOT standard API calls but Python specific:

		If the first parameter (or rather the type) is not a String it
		is assumed to be a valid Data entity and will be added instead
		of creating a new one. This allows us to write stuff like

		'child = list.addChild(StringData('foo', 'bar'))

		which is more OO like (as we are using classes here anyway).

		The second addition is the optional position where we want the
		child to be added. By default it is appended but a position can
		be used to insert it at any place. This feature is used for
		moving children around in a List and should not be relied upon
		on in other languages to exist.

		**PARAMS:**
			'self'	-- Instance of class object
			't'	-- Type of the new child. Optional Data entity object
			'n'	-- optional name of the new child
			'v'	-- Optional value of the new child
			'pos'	-- Index where child should be added into List

		**RETURNS:**
			*Data*	-- Reference to newly added child entity
"""
		if   type(t) == StringType or type(t) == UnicodeType:
			tstr = t.upper()
			if   tstr == 'STRING':
				t = StringData(n, v)
			elif tstr == 'INT':
				t = IntData(n, v)
			elif tstr == 'BASE64':
				t = Base64Data(n, v)
			elif tstr == 'FLOAT':
				t = FloatData(n, v)
			elif tstr == 'BOOL':
				t = BoolData(n, v)
			elif tstr == 'COPY':
				t = CopyData(n, v)
			elif tstr == 'LIST':
				t = ListData(n)
			else:
				raise TypeError
		elif type(t) == IntType:
			if   t == Data.ADM_TYPE_STRING:
				t = StringData(n, v)
			elif t == Data.ADM_TYPE_INT:
				t = IntData(n, v)
			elif t == Data.ADM_TYPE_BASE64:
				t = Base64Data(n, v)
			elif t == Data.ADM_TYPE_FLOAT:
				t = FloatData(n, v)
			elif t == Data.ADM_TYPE_BOOL:
				t = BoolData(n, v)
			elif t == Data.ADM_TYPE_COPY:
				t = CopyData(n, v)
			elif t == Data.ADM_TYPE_LIST:
				t = ListData(n)
			else:
				raise TypeError

		n  = t.getName()
		nv = self.nvalue

		#
		# Anonymous is basically the only attribute of the List that
		# it takes care of by itself. When a List is anonymous it can
		# have multiple childs with the same name.
		# We use a neat trick to do this: If the item is new both
		# are treated the same.
		# In case we have an entry already though in the case of the
		# non anonymous list we first remove that entry from our List.
		# The effect is that in non anonymous Lists we will never have
		# more than 1 entry per nv[name] list, which is exactly what
		# we want.
		#
		if not nv.has_key(n):
			nv[n] = []
		elif not self.isAnonymous() and len(nv[n]) > 0:
			self.delChild(nv[n][0])
                nv[n].append(t)

		#
		# 11/17/00 PK: the addChild() function should not use the
		# prepend attribute to decide where to put the new child but
		# rather leave it up to the merge algorithm to move things
		# around (it's up to the 'external' objects to use the
		# attribute, but it's not the List's responsibility to use it
		# internally, just like with most other attributes)
		#
		if pos == -1:
			self.pvalue.append(t)
		else:
			self.pvalue.insert(pos, t)

		t.setContainer(self)
		if t.getSource() == '':
			t.setSource(self.getSource())
		t.setContext(self.getContext())

		return t

	def getChildByName(self, key):
		"""
		Child accessor method by name

		Accessor method that returns a child by a given name. For an
		anonymous List this method returns the first child found that
		matches the given name.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Name of the child to be accessed

		**RETURNS:**
			*Data*	-- Reference to child entity for given name

		**EXCEPTIONS:**
			*KeyError*	-- Raised if index is out of bounds or
					invalid

		**SEE:**
			'' -- "List.__getitem__()":#List.__getitem__
"""
		if '/' in key:
			pos   = string.index(key, '/')
			name  = key[:pos]
			index = int(key[pos+1:])
		else:
			name = key
			index = 0

		return self.nvalue[name][index]

	def getChildByIndex(self, key):
		"""
		Child accessor method by position

		Accessor method that returns a child by a given index.

		**PARAMS:**
			'self'	-- Instance of class object
			'idx'	-- Index of the child to be accessed

		**RETURNS:**
			*Data*	-- Reference to child entity for given name

		**EXCEPTIONS:**
			*KeyError*	-- Raised if index is out of bounds

		**SEE:**
			'' -- "List.__getitem__()":#List.__getitem__
"""
		return self.pvalue[key]

	def getNumChildren(self):
		"""
		Number of children aggregate method

		Aggregation method to return the number of children in our
		List object.

		**PARAMS:**
			'self'	-- Instance of class object

		**RETURNS:**
			*int*	-- Number of children in our List object
"""
		return len(self.pvalue)

	def moveChild(self, e, p):
		"""
		Child movement method

		Moves the given child (which has to be an element of the List)
		to the given position.

		**PARAMS:**
			'self'	-- Instance of class object
			'e'	-- Reference to child to be moved
			'p'	-- Position where to move the child

		**RETURNS:**
			*Data*	-- Reference to the moved child (should be same
				as 'e'
"""
		self.delChild(e)
		self.addChild(e, pos=p)

	def copyData(self, e):
		"""
		Child copy and append method

		Creates a copy of the given Data entity and appends it to the
		List.

		**PARAMS:**
			'self'	-- Instance of class object
			'e'	-- Reference to child to be copied and appended

		**RETURNS:**
			*Data*	-- Reference to the newly appended child
"""
		self.addChild(e.__copy__())

	def delChild(self, e):
		"""
		Private child removal method

		Removes the given child from the List. Can be done either by
		position or by Data entity reference.

		**PARAMS:**
			'self'	-- Instance of class object
			'e'	-- Position or reference to child to be deleted
"""
		if type(e) == IntType:
			etmp = self.pvalue[e]
		else:
			etmp = e

		self.nvalue[etmp.getName()].remove(etmp)
		self.pvalue.remove(etmp)



class StringData(Data):
	"""
	String Data Entity class

Our String scalar basic type. Nothing fancy here.
"""
	def __init__(self, n='', v=''):
		"""
		Public constructor

		Initializes the String entity. Sets the type, optional name and
		optional value accordingly.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Optional initial name of the Data entity
			'v'	-- Optional initial value of the Data entity
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_STRING)
		self.setValue(v)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*String* --	New instance with copy of given object
"""
		n = StringData()
		n.copy(self)
		return n



class Base64Data(Data):
	"""
	Base64 Data Entity class

Our Base64 scalar basic type. Nothing fancy here.
"""
	def __init__(self, n='', v=''):
		"""
		Public constructor

		Initializes the Base64 entity. Sets the type, optional name
		and optional value accordingly.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Optional initial name of the Data entity
			'v'	-- Optional initial value of the Data entity
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_BASE64)
		self.setValue(v)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Base64* --	New instance with copy of given object
"""
		n = Base64Data()
		n.copy(self)
		return n



class IntData(Data):
	"""
	Int Data Entity class

Our Int scalar basic type. Nothing fancy here.
"""
	def __init__(self, n='', v=0):
		"""
		Public constructor

		Initializes the Int entity. Sets the type, optional name and
		optional value accordingly.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Optional initial name of the Data entity
			'v'	-- Optional initial value of the Data entity
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_INT)
		self.setValue(v)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Int*	--	New instance with copy of given object
"""
		n = IntData()
		n.copy(self)
		return n

	def setValue(self, v):
		"""
		Value attribute mutator method

		Mutator method to set the value of this Data entity. It's
		basically up to the application to decide what to put in here,
		but a derived Data entity might implement a check here to
		verify the input and reject it if it is not valid.

		**PARAMS:**
			'self'	-- Instance of class object
			'v'	-- Value which should be set for this Data
				object

		**SEE:**
			'' -- "Data.getValue()":#Data.getValue
"""
		if   type(v) == IntType:
			self.value = v
		elif (type(v) == StringType or type(v) == UnicodeType) and v != "":
			self.value = int(v)
		else:
			self.value = 0



class FloatData(Data):
	"""
	Float Data Entity class

Our Float scalar basic type. Nothing fancy here.
"""
	def __init__(self, n='', v=0.0):
		"""
		Public constructor

		Initializes the Float entity. Sets the type, optional name and
		optional value accordingly.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Optional initial name of the Data entity
			'v'	-- Optional initial value of the Data entity
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_FLOAT)
		self.setValue(v)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Float*	--	New instance with copy of given object
"""
		n = FloatData()
		n.copy(self)
		return n

	def setValue(self, v):
		"""
		Value attribute mutator method

		Mutator method to set the value of this Data entity. It's
		basically up to the application to decide what to put in here,
		but a derived Data entity might implement a check here to
		verify the input and reject it if it is not valid.

		**PARAMS:**
			'self'	-- Instance of class object
			'v'	-- Value which should be set for this Data
				object

		**SEE:**
			'' -- "Data.getValue()":#Data.getValue
"""
		try:
			self.value = float(v)
		except:
			self.value = 0.0



class BoolData(Data):
	"""
	Bool Data Entity class

Our Bool scalar basic type. Nothing fancy here.
"""
	def __init__(self, n='', v=0):
		"""
		Public constructor

		Initializes the Bool entity. Sets the type, optional name and
		optional value accordingly.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Optional initial name of the Data entity
			'v'	-- Optional initial value of the Data entity
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_BOOL)
		self.setValue(v)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Bool*	--	New instance with copy of given object
"""
		n = BoolData()
		n.copy(self)
		return n

	def setValue(self, v):
		"""
		Value attribute mutator method

		Mutator method to set the value of this Data entity. It's
		basically up to the application to decide what to put in here,
		but a derived Data entity might implement a check here to
		verify the input and reject it if it is not valid.

		**PARAMS:**
			'self'	-- Instance of class object
			'v'	-- Value which should be set for this Data
				object

		**SEE:**
			'' -- "Data.getValue()":#Data.getValue
"""
		if type(v) == StringType or type(v) == UnicodeType:
			if v.lower() == "true" or v.lower() == "on" or v != "0":
				self.value = True
			else:
				self.value = False
		else:
			try:
				self.value = bool(v)
			except:
				self.value = False



class CopyData(Data):
	"""
	Copy Data Entity class

Our Copy scalar basic type. Nothing fancy here.
"""
	def __init__(self, n='', v=''):
		"""
		Public constructor

		Initializes the Copy entity. Sets the type, optional name and
		optional value accordingly.

		**PARAMS:**
			'self'	-- Instance of class object
			'n'	-- Optional initial name of the Data entity
			'v'	-- Optional initial value of the Data entity
"""
		Data.__init__(self, n)
		self.setType(Data.ADM_TYPE_COPY)
		self.setValue(v)

	def __copy__(self):
		"""
		Private copy operator

		This method creates a copy of this object and returns the new
		object.

		**PARAMS:**
			'self'	--	Instance of class object

		**RETURNS:**
			*Copy*	--	New instance with copy of given object
"""
		n = CopyData()
		n.copy(self)
		return n



#
# Global module procedures
#



def merge(name, ser, ctx1, ctx2):
	"""
	Merge two contexts

	This global procedure merges the two given Contexts and sets the name
	and serial number of the newly created returned Context correspondigly.

	**PARAMS:**
		'name'	--	Name of the new Context
		'ser'	--	Serial number of the new Context
		'ctx1'	--	First Context to be merged
		'ctx2'	--	Second Context to be merged with the first

	**RETURNS:**
		*Context* --	New instance with a new Context with the given name and serial number containing the merge of the two Contexts
"""
	cret = ctx1.merge(name, ser, ctx2)
	return cret



#
# Check if we let the Alchemist run in 'standalone' mode and not load it as
# a module. In that case run some tests to see what we are doing.
#
if __name__ == '__main__':
	#
	# Pretty neat little test to actually build up a Context that looks
	# similar to what we will be using for bootstrapping BlackBoxes.
	# Contains most of the data types and combinations (except the 
	# Protected attribute which really only makes sense for merging).
	# Also uses the toXML() and fromXML() calls to feedback verify that
	# the encoding functions do the right thing.
	# Merging is tested as well by merging the same Context with itself,
	# so reference problems should show up fairly quickly.
	#
	def test():
		ctx = Context(name='local', serial=1)
		bs = ctx.data
		bs.setSource('Local')
		boxes = bs.addChild ('list', 'boxes')
		input1 = boxes.addChild ('list', 'input1')
		input1.addChild ('string', 'location', 'input1.py')
		config = input1.addChild ('list', 'config')
		input2 = boxes.addChild ('list', 'input2')
		input2.addChild ('string', 'location', 'input2.py')
		config = input2.addChild ('list', 'config')
		apps = bs.addChild ('list', 'apps')
		test = apps.addChild ('list', 'test')
		inputs = test.addChild ('list', 'inputs')
		inputs.setAnonymous(1)
		inputs.addChild ('string', 'boxname', 'input1')
		inputs.addChild ('string', 'boxname', 'input2')

#		print bs['apps']['test']['inputs']
#		print inputs
#		print inputs[0]
#		print inputs['boxname/0']
#		print inputs[1]
#		print inputs['boxname/1']

		test.addChild ('string', 'output', 'forge')
		testrev = apps.addChild ('list', 'testrev')
		inputs = testrev.addChild ('list', 'inputs')
		inputs.addChild ('string', 'boxname', 'input2')
		inputs.addChild ('string', 'boxname', 'input1')
		testrev.addChild ('string', 'output', 'forge')

		tst = ctx.__copy__()
#		print tst.toXML()

		xml = ctx.toXML()
		#print xml

		ctx2 = Context(name='local', serial=1)
		ctx2.fromXML(xml)
		print ctx2.toXML()

		ctx3 = ctx.merge(name='local', serial=1, other=ctx2)
		#print ctx3.toXML()

		return ctx

	#
	# First test of co
	def test2():
		c2 = Context(name='Bar', serial=1)
		c = Context(ctx=c2)
		c2.setName('Foo')
		c.setDelete('/apache/vh/1')
		print 'Context reference:      ' + str(c)
		print 'Context getDelete(0):   ' + c.getDelete(0)
		print 'Context c["delete"][0]: ' + c['delete'][0]
		print 'Context Name:           ' + c.getName()
		print 'Context2 Name:          ' + c2.getName()

		d = c['data']
		print d

		c = Context(name='MyBootStrap', serial=2)
		d = c['data']

		fbb = d.addChild(ListData('FileBlackBox'))

		fbb.addChild(StringData('dirname')).setValue('Log')
		fbb.addChild(StringData('user')).setValue('harald')
		fbb.addChild(IntData('port')).setValue(10)
		fbb.addChild(StringData('user')).setValue('florian')

		max = fbb.getNumChildren()
		for i in range(max):
			print fbb[i].getName() + ': ' + `fbb[i].getValue()`

	#
	# Tiny test to verify that merging is actually doing the right thing.	
	# Not a very deep and thorough test, mind you, but it's a start for
	# 'usual case' behaviour test.
	# The Test.py will contain a lot more corner cases and boundary checks
	# for that which we can verify. This one here only give a quick'n'dirty
	# way to see if anything is working at all quickly.
	#
	def test3():
		c1 = Context(name='Foo', serial=1)
		c2 = Context(name='Bar', serial=2)

		d1 = c1.getDataRoot()
		d2 = c2.getDataRoot()

		l1 = d1.addChild(Data.ADM_TYPE_LIST, 'buz')
		l1.setProtected(1)
		l1.setAnonymous(0)
		l1.setAtomic(0)
		l1.setPrepend(0)

		x1 = l1.addChild(Data.ADM_TYPE_STRING, 'abra', 'l1')
		x1.setProtected(0)
		x2 = l1.addChild(Data.ADM_TYPE_STRING, 'cada', 'l2')

		l2 = d2.addChild(Data.ADM_TYPE_LIST, 'buz')
		l2.setProtected(0)
		l2.setAnonymous(0)
		l2.setAtomic(0)
		l2.setPrepend(0)

		x2 = l2.addChild(Data.ADM_TYPE_STRING, 'abra', 'l2')
		x2.setProtected(0)


		c3 = merge('Joe', 3, c1, c2)
		c3.setDelete('abra')
		print c3.toXML()

		c4 = Context(name='Jack', serial=4)
		c4.fromXML(c3.toXML())
		print c4.toXML()

	def test4():
		try:
                	ctx = Context(name = " asdsa", serial = 1)
        	except ContextError, e:                           
                	pass                                      
        	ctx = Context (name = 'name', serial = 1)         
        	ctxc = ctx.copy ()                                

        	ctx = Context (name = 'name', serial = 1)
        	ctxc = ctx.copy ()                       
        	ctxcc = ctxc.copy ()                     
        	ctxcc.flatten ()                         
        	xml = ctxcc.toXML ()                     
        	ctxml = Context (xml = xml)              
        	ctxcc.setDelete ('/blah')                
        	delete = ctxcc.getDelete (0)             
        	ctxcc.clearDeleteByIndex (0)             
        	ctxcc.setDelete ('/blah')                
        	n = ctxcc.getNumDeletes ()               
        	ctxcc.clearDeleteByString ('/blah')      
        	id = ctxcc.getIdentityRoot ()            
        	ida = ctxcc.getIdentityRoot ()           
        	if id.isIdentical(ida):                  
                	print "success!"                 
        	a = id.getParentA ()                     
        	b = id.getParentB ()                     
        	id.setName ('myname')                    
        	n = id.getName ()                        
        	id.setSerial (1)                         
        	s = id.getSerial ()                      
        	id.isAlive ()                            
        	l = ctxcc.getDataRoot ()                 
        	lb = ctxcc.getDataRoot ()                
        	if l.isIdentical(lb):                    
                	print "yay!"                     
        	ctxr = l.getContext()                    
        	if ctxr.isIdentical(ctxcc):              
                	print "woopie"                   
        	t = l.getType ()                         
        	n = l.getNumChildren ()                  
        	c = l.getContext ()                      
        	l.isAlive ()                             
        	c = l.addChild (Data.ADM_TYPE_INT, 'int')
        	c = l.getChildByIndex (0)                
        	c = l.getChildByName ('int')             
        	print c.getPos ()                              
        	print c.setValue (1)                           
        	print c.getValue ()                            
        	d = l.addChild (Data.ADM_TYPE_BOOL, 'bool')
        	print d.setValue (0)                             
        	print d.getValue ()           
		print l[0], l[1]
        	print l.moveChild (c, 1)
		print l[0], l[1]
        	ll = l.addChild (Data.ADM_TYPE_LIST, 'list')
        	ll.setProtected (0)                         
        	ll.isProtected ()
        	ll.setAnonymous (1)
        	ll.isAnonymous ()
        	ll.setAtomic (0)
        	ll.isAtomic ()
        	ll.setPrepend (0)
        	ll.isPrepend ()
        	ll.setSource ('src')
        	ll.getSource ()
        	ll.setName ('newname')
        	ll.getName ()
        	c = ll.addChild (Data.ADM_TYPE_INT, 'int')
        	ll.copyData (c)
        	ctr = ll.getContainer ()
        	#ll.unlink ()
        	c = l.addChild (Data.ADM_TYPE_FLOAT, 'float')
        	c.setValue (0.0)
        	c.getValue ()
        	c = l.addChild (Data.ADM_TYPE_STRING, 'string')
        	c.setValue ('string')
        	c.getValue ()
        	c = l.addChild (Data.ADM_TYPE_BASE64, 'base64')
        	c.setValue ('YmFzZTY0')
        	c.getValue ()
        	c = l.addChild (Data.ADM_TYPE_COPY, 'copy')
        	c.setValue ('/blah')
        	c.getValue ()
        	x = ctxcc.getDataByPath ('/int')
        	m = merge ('merged', 1, ctxc, ctxcc)
		print m.toXML()
        	print ctxcc.toXML()
        	print ctxc.toXML()
        	print ctx.toXML()

	#
	# Small profiling test. We might want to do this sometime later when
	# we really know that the system is doing the right thing(tm) but need
	# a little more performance in order to squeeze a little more out of
	# our algorithms and data structures.
	#
	def profile():
		import profile
		import pstats

		profile.run('test()', 'Alchemist.py.prof')
		p = pstats.Stats('Alchemist.py.prof')
		p.sort_stats('time').print_stats()


	#
	# Call our main test function
	#
	c = Context(name='Foo', serial=1)
	test4()

#!/usr/bin/python
import Alchemist
import time
import urllib
import gzip

def getBox(box_cfg):
	return URLBlackBox(box_cfg)

class URLBlackBox(Alchemist.BlackBox):
	def __init__ (self, box_cfg):
		self.status = 0
		self.me = self.__class__.__module__
		self._errNo = 0
		self._errStr = None
		self.readable = 1
		self.writable = 0
	
		Alchemist.validateBoxCfg(box_cfg)
	
		try:
			self.url = box_cfg.getChildByName("url").getValue()
		except:
			raise ValueError, "URLBlackBox box_cfgs must contain a 'url' element"

	def read (self):
		try:
			ufile = urllib.urlopen(self.url)
			gfile = gzip.GzipFile(fileobj = ufile)
			xml_str = gfile.read()
			gfile.close()
		
			context = Alchemist.Context(xml = xml_str)
			return context
		except:
			return None

	def version(self):
		return time.time() - time.timezone


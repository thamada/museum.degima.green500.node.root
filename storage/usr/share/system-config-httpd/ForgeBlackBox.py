#!/usr/bin/python
import Alchemist
import os
import re
import stat
from xml.xslt.Processor import Processor

def getBox(box_cfg):
    """
    getBox: get a BlackBox from this module
    @box_cfg: a box_cfg conformant AdmList element containing
    the following elements:
    path: type string, the path to the context file (required)
    returns: Forge object
    """
    if box_cfg == None:
        raise ValueError
    return ForgeBlackBox(box_cfg)



class ForgeBlackBox(Alchemist.BlackBox):
    """o
    The ForgeBlackBox is the class which handles converting the xml with a XSLT
    stylesheet and writing this as a configuration file
    """

    def __init__(self,box_cfg):
        """
        __init__: Initialize a ForgeBlackBox
        @self: the class instance
        @box_cfg: a box_cfg conformant AdmList element containing
                  the following elements:
                  xslstylesheetpath: a string
                  configfilepath: a string
                  mode: an integer
        """
        
        self.status=0
        self.me=self.__class__.__module__
        self._errNo=0
        self._errStr=None
        self.readable=0
        self.writable=1
        Alchemist.validateBoxCfg(box_cfg)
        
        self.sspath=box_cfg.getChildByName("xslstylesheetpath").getValue()
        try:
            if os.access(self.sspath, os.R_OK):
                mode = os.stat(self.sspath)[stat.ST_MODE]
                if (not stat.S_ISREG(mode)):
                    raise ValueError
        except:
            raise ValueError, "ForgeBlackBox box_cfg must contain a 'xslstylesheetpath' entry pointing at a readable file (" + self.sspath + ")"

        try:
            self.cfgpath=box_cfg.getChildByName("configfilepath").getValue()
            if self.cfgpath=="SPLITFILES":
                self.splitfiles=1
            else:
                self.splitfiles=0
            
        except:
            raise ValueError, "ForgeBlackBox box_cfg must contain a 'configfilepath' entry"
        try:
            self.mode=box_cfg.getChildByName("mode").getValue()
        except:
            raise ValueError, "ForgeBlackBox box_cfg must contain a 'mode' entry"


   
    def write (self,context):
        """
        Extract xml, stylesheetpath and target file from the context
        and create the configuration file.
        @self: the class instance
        @context: the context from which to extract information
        """

        xml_string = context.toXML()
        if (not xml_string):
            return 0

        processor=Processor()
        processor.appendStylesheetFile(self.sspath)
        result=processor.runString(xml_string)
        if (self.splitfiles==0):
            fd = os.open(self.cfgpath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, self.mode)
            file = os.fdopen(fd, "w")
            file.write(result)
            file.close()
        else:
            myreg=re.compile(r'^--------CUTFILEHERE: (?P<filename>.*?)$(?P<content>.*?)^--------ENDFILEHERE?(?P<remaining>.*)',re.MULTILINE|re.DOTALL)
            match=1
            while match:
                match=myreg.search(result)
                if not match:
                    break
                else:
                    result=match.group("remaining")
                    fd = os.open(match.group("filename"), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, self.mode)
                    file = os.fdopen(fd, "w")
                    file.write(match.group("content"))
                    file.close()
                    
            

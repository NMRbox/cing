'''
Nijmegen Tools utilities, the extensions.

NTutils imports these extensions after it loads it's own code.

Meant to delineate the classes.
'''
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTcodeerrorT
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdebugT
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTdetailT
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTerrorT
from cing.Libs.NTutils import NTexception
from cing.Libs.NTutils import NTexceptionT
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageList
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTmessageNoEOLT
from cing.Libs.NTutils import NTmessageT
from cing.Libs.NTutils import NTnothingT
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NTwarningT
from cing.Libs.NTutils import getDeepByKeysOrAttributes
from cing.Libs.NTutils import readTextFromFile
from cing.Libs.NTutils import sprintf
from cing.Libs.fpconst import isNaN
from cing.core.constants import * #@UnusedWildImport
from random import randint
from random import seed
from string import join
from traceback import format_exc
import datetime
import inspect
import math
import os
import re
import sys
import time

class NTlistOfLists(NTlist):
    """
    Generate a NTlist of NTlist's of rowSize, colSize filled with default's
    """

    def __init__( self, rowSize, colSize, default=None ):
        NTlist.__init__( self )
        for _i in range(rowSize):
            self.append(NTfill(default, colSize))
        self.rowSize = rowSize
        self.colSize = colSize
    #end def

    def getRow( self, rowIndex ):
        """Get a row (trivial!)
        Return None on error
        """
        if rowIndex < 0 or rowIndex > len(self):
            return None
        return self[rowIndex]
    #end def

    def getColumn( self, columnIndex ):
        """Get a column (trivial!)
        Return None on error
        """
        if columnIndex < 0 or columnIndex > self.colSize:
            return None
        result = NTlist()
        for row in self:
            result.append( row[columnIndex] )
        return result
    #end def

    def getDiagonal(self):
        """Get the diagonal of a square NTlistOfLists
        return NTlist instance or None on error
        """
        if self.rowSize != self.colSize:
            NTerror('NTlistOflists.getDiagonal: unequal number of rows (%d) and collumns (%d)', self.rowSize, self.colSize)
            return None
        result = NTlist()
        for i in range(self.rowSize):
            result.append(self[i][i])
        #end for
        return result
    #end def

    def format( self, fmt = '%s' ):
        result = ''
        for i in range(self.rowSize):
            result = result + self[i].format(fmt=fmt) + '\n'
        return result
    #end def
#end class

def addStreamNTmessageList(stream):
    for NTm in NTmessageList:
#        print "EEE: starting addStream to %s" % NTm
        NTm.addStream(stream)
def removeStreamNTmessageList():
    for NTm in NTmessageList:
#        print "EEE: starting removeStream to %s" % NTm
        NTm.removeStream()

def teeToFile(logFile):
    '''Starts to tee the different verbosity messages to a possibly existing file
    Return True on failure.
    '''
#    logFile = '/Users/jd/Library/Logs/weeklyUpdatePdbjMine.log'
    stream = None
    try:
        stream = open(logFile, 'a')
    except:
        NTtracebackError()
        return True
    NTnothingT.stream = stream
    NTerrorT.stream = stream
    NTcodeerrorT.stream = stream
    NTexceptionT.stream = stream
    NTwarningT.stream = stream
    NTmessageT.stream = stream
    NTdetailT.stream = stream
    NTdebugT.stream = stream
    NTmessageNoEOLT.stream = stream
    NTnothingT.stream = stream


#class NTmessage2(PrintWrap):
#    def __init__(self):
#        PrintWrap.__init__(self, stream, autoFlush, verbose, noEOL, useDate, useProcessId, doubleToStandardStreams, prefix)
#    def __call__(self):
#

def NTtracebackError():
    traceBackString = format_exc()
#    print 'DEBUG: NTtracebackError: [%s]' % traceBackString
    if traceBackString == None:
        traceBackString = 'No traceback error string available.'
    NTerror(traceBackString)

_outOutputStreamContainerList = [ NTmessageNoEOL, NTdebug, NTdetail, NTmessage, NTwarning ]
_errOutputStreamContainerList = [ NTerror, NTcodeerror, NTexception ]

"""To dump some output to never see again"""
_bitBucket = open('/dev/null', 'aw')
"Regular output at the start of the program"
_returnMyStdOut = sys.stdout
"Error output at the start of the program"
_returnMyStdErr = sys.stderr

def _setStdOutStreamsTo(stream):
    return _setOutStreamList(stream, _outOutputStreamContainerList)

def _setStdErrStreamsTo(stream):
    return _setOutStreamList(stream, _errOutputStreamContainerList)

def _setOutStreamList(stream, outputStreamContainerList):
    for outputStreamContainer in outputStreamContainerList:
#        print "Setting the outputStreamContainer [%s] stream to: %s" % (outputStreamContainer, stream)
        outputStreamContainer.flush()
        outputStreamContainer.stream = stream



def switchOutput( showOutput, doStdOut=True, doStdErr=False):
    """
    Switch away from output. Might be useful to silence verbose part of code or external program.

    False: store original stream and switch to bit bucket.
    True: return to original stream.
    """
    if showOutput:
        if doStdOut:
            sys.stdout = _returnMyStdOut
            _setStdOutStreamsTo( _returnMyStdOut )
#            print "1DEBUG: enabled stdout"
        if doStdErr:
            sys.stderr = _returnMyStdErr
            _setStdErrStreamsTo( _returnMyStdErr )
#            print "1DEBUG: enabled stderr"
        return
    if doStdOut:
#        print "1DEBUG: disabling stdout"
        sys.stdout = _bitBucket
        _setStdOutStreamsTo( _bitBucket )
    if doStdErr:
#        print "1DEBUG: disabling stderr"
        sys.stderr = _bitBucket
        _setStdErrStreamsTo( _bitBucket )

class MsgHoL(NTdict):
    def __init__(self):
        NTdict.__init__(self)
        self[ ERROR_ID ] =  NTlist()        
        self[ WARNING_ID ] =  NTlist()
        self[ MESSAGE_ID ] =  NTlist()
        self[ DEBUG_ID ] =  NTlist()

    def appendError(self, msg):
        self[ ERROR_ID ].append(msg)
    def appendWarning(self, msg):
        self[ WARNING_ID ].append(msg)
    def appendMessage(self, msg):
        self[ MESSAGE_ID ].append(msg)
    def appendDebug(self, msg):
        self[ DEBUG_ID ].append(msg)

    def showMessage( self, MAX_ERRORS = 5, MAX_WARNINGS = 5, MAX_MESSAGES = 5, MAX_DEBUGS = 20 ):
        "Limited printing of errors and the like; might have moved the arguments to the init but let's not waste time."

        typeCountList = { ERROR_ID: MAX_ERRORS, WARNING_ID: MAX_WARNINGS, MESSAGE_ID: MAX_MESSAGES, DEBUG_ID: MAX_DEBUGS }
        typeReportFunctionList = { ERROR_ID: NTerror, WARNING_ID: NTwarning, MESSAGE_ID: NTmessage,  DEBUG_ID: NTdebug }

        for type in typeCountList:
            if not self.has_key(type):
                continue

            typeCount = typeCountList[ type ]
            msgList = self[type]
            typeReportFunction = typeReportFunctionList[ type ]
            msgListLength = len(msgList)
#            NTdebug("now for typeCount: %d found %d" % (typeCount, msgListLength))
            for i in range(msgListLength):
                if i >= typeCount:
                    typeReportFunction("and so on for a total of %d messages" % len(msgList))
                    break
                typeReportFunction(msgList[i])
    #end def
# end classs

class BitSet(NTlist):
    """From Java for Stereo"""
    def __init__(self):
        NTlist.__init__(self)

    def get(self, idx):
        if idx >= self.n:
            return False
        return self[idx]


def isAlmostEqual( ntList, epsilon):
    e = ntList[0] - ntList[1]
    e = math.fabs(e)
    if e < epsilon:
        return True
    return False
# end def

def toPoundedComment(str):
    result = []
    for line in str.split('\n'):
#        NTdebug("Processing line: [%s]" % line)
        result.append( '# %s' % line )
    resultStr = join(result, '\n')
    return resultStr

def NTlist2dict(lst):
    """Takes a list of keys and turns it into a dict where the values are counts of how many times the key ocurred."""

    dic = {}
    for k in lst:
        if dic.has_key(k):
            dic[k] = dic[k] + 1
        else:
            dic[k] = 1
    return dic
list2dict = NTlist2dict

def getKeyWithLargestCount(count):
    """Return the key in the hashmap of count for which the value
    is the largest.
    Return None if count is empty.
    """
    countMax = -1
    for v in count:
        countV = count[v]
#        NTdebug("Considering key/value %s/%s" % (v,countV))
        if countV > countMax:
            countMax = countV
            vMax = v
#            NTdebug("Set max key/value %s/%s" % (vMax,countMax))
    if countMax < 0: # nothing found
        return None
    return vMax

def grep(fileName, txt, resultList = None, doQuiet=False, caseSensitive=True):
    """
    Exit status is 0 if selected lines are found and 1 if none are found.
    Exit status 2 is returned if an error occurred, unless the -q or --quiet or --silent option is used and a selected line is found.
    Instead of printing, a resultList will be filled if provided.
    """
    if not os.path.exists(fileName):
        return 2
    if not caseSensitive:
        txt = txt.lower()

    matchedLine = False
    for line in open(fileName):
        if len(line):
            line = line[:-1] # must be at least 1 char long
        else:
            NTcodeerror("Fix code in grep")
        lineMod = line
        if not caseSensitive:
            lineMod = lineMod.lower()
        if txt in lineMod:
#            NTdebug("Matched line in grep: %s" % lineMod)
            if resultList != None:
                resultList.append(line)
            if doQuiet:
                # important for not scanning whole file.
                return 0
            matchedLine = True
    if matchedLine:
        return 0
    return 1

def timedelta2HoursMinutesAndSeconds( s ):
    'Returns integer numbers for number of minutes and seconds of given float of seconds; may be negative'
    result = [0, 0, 0]
    t = s
    result[0] = int(t / 3600)
    t -= 3600 * result[0]
    result[1] = int(t / 60)
    t -= 60 * result[1]
    result[2] = int(t)
    return tuple(result)

def lenNonZero(l, eps=EPSILON_RESTRAINT_VALUE_FLOAT):
    'Counts the non zero eelements when compared to epsilon'
    if l == None:
        return 0
#    if len(l) == 0:
#        return 0
    n = 0
    for item in l:
        if math.fabs(item) > eps:
            n += 1
    return n

def stringMeansBooleanTrue(inputStr):
    """
    Returns True if it's a string that is either 1 (any non-zero), True, etc.
    Optimized for speed. See unit test.
    """
    if inputStr == None:
        return False
    if not isinstance(inputStr, str):
        return False
    inputStrlower = inputStr.lower()
    if inputStrlower == 'true':
        return True
    if inputStrlower == 'false':
        return False
    if inputStrlower == 't':
        return True
    if inputStrlower == 'f':
        return False
    if inputStrlower == 'y':
        return True
    if inputStrlower == 'n':
        return False
    if inputStrlower == 'yes':
        return True
    if inputStrlower == 'no':
        return False

    try:
        inputInt = int(inputStr)
    except:
        NTwarning("Failed to get integer after testing string possibilities")
        inputInt = 0

    if inputInt:
        return True
    return False
# end def

def truthToInt(i):
    if i == None:
        return None
    if i:
        return 1
    return 0
# end def

def getCallerName():
    return inspect.stack()[1][3]
# end def

def getRandomKey(size=6):
    """Get a random alphanumeric string of a given size"""
    ALPHANUMERIC = [chr(x) for x in range(48, 58) + range(65, 91) + range(97, 123)]
    #random.shuffle(ALPHANUMERIC)

    n = len(ALPHANUMERIC) - 1
    seed(time.time()*time.time())

    return ''.join([ALPHANUMERIC[randint(0, n)] for x in range(size)])
# end def

def isNoneorNaN(value):
    if value == None:
        return True
    return isNaN(value)
# end def



def getUniqueName(objectListWithNameAttribute, baseName, nameFormat = "%s_%d" ):
    """
    Return unique name or False on error.
    E.g. for ResonanceSources object in which the ResonanceList objects have a name attribute.

    nameFormat may be specified to receive a string and an integer argument.
    Works on any NTlist that has name attributes in each element.
    """
    nameList = objectListWithNameAttribute.zap( NAME_STR )
#    NTdebug("Already have names: %s" % str(nameList))

    nameDict = NTlist2dict(nameList)
    if not nameDict.has_key( baseName):
        return baseName
    i = 1
    while i < MAX_TRIES_UNIQUE_NAME: # This code is optimal unless number of objects get to 10**5.
        newName = sprintf( nameFormat, baseName, i)
        if not nameDict.has_key( newName ):
            return newName
        i += 1
# end def

def getObjectByName(ll, name):
    """
    Return list by name or False.
    Works on any NTlist that has name attributes in each element.

    E.g. for ResonanceSources object in which the ResonanceList objects have a name attribute.
    """
#    NTdebug("Working on ll: %s" % str(ll))
#    NTdebug("ll[0].name: %s" % ll[0].name)
    names = ll.zap('name')
#    NTdebug("names: %s" % str(names))
    idx = names.index(name)
    if idx < 0:
        return
    return ll[idx]
# end def

def getObjectIdx(ll, l):
    """
    Return list by name or False.
    Works on any NTlist that has name attributes in each element.
    """
    name = l.name
    names = ll.zap('name')
    return names.index(name)
# end def


def filterListByObjectClassName( l, className ):
    'Return new list with only those objects that have given class name.'
    result = []
    if l == None:
        return result
    if not isinstance(l, list):
        NTerror('Input is not a list but a %s' % str(l))
        return result
#    if len(l) == 0:
#        return result
    for o in l:
        oClassName = getDeepByKeysOrAttributes(o, '__class__', '__name__' )
#        NTdebug("oClassName: %s" % oClassName)
        if oClassName == className:
            result.append(o)
    return result
# end def

def getRevisionAndDateTimeFromCingLog( fileName ):
    """Return int revision and date or None on error."""
    txt = readTextFromFile(fileName)
    if txt == None:
        NTerror("In %s failed to find %s" % ( getCallerName(), fileName))
        return None
    # Parse
##======================================================================================================
##| CING: Common Interface for NMR structure Generation version 0.95 (r972)       AW,JFD,GWV 2004-2011 |
##======================================================================================================
#User: i          on: vc (linux/32bit/8cores/2.6.4)              at: (10370) Sat Apr 16 14:24:12 2011
    txtLineList = txt.splitlines()
    if len(txtLineList) < 2:
        NTerror("In %s failed to find at least two lines in %s" % ( getCallerName(), fileName))
        return None
    txtLine = txtLineList[1]
    reMatch = re.compile('^.+\(r(\d+)\)') # The number between brackets.
    searchObj = reMatch.search(txtLine)
    if not searchObj:
        NTerror("In %s failed to find a regular expression match for the revision number in line %s" % ( getCallerName(), txtLine))
        return None
    rev = int(searchObj.group(1))

    if len(txtLineList) < 4:
        NTerror("In %s failed to find at least four lines in %s" % ( getCallerName(), fileName))
        return None
    txtLine = txtLineList[3]
    reMatch = re.compile('^.+\(\d+\) (.+)$') # The 24 character standard notation from time.asctime()
    searchObj = reMatch.search(txtLine)
    if not searchObj:
        NTerror("In %s failed to find a regular expression match for the start timestamp in line %s" % ( getCallerName(), txtLine))
        return None
    tsStr = searchObj.group(1) #    Sat Apr 16 14:24:12 2011
    try:
#        struct_timeObject = time.strptime(tsStr)
        dt = datetime.datetime(*(time.strptime(tsStr)[0:6]))
#        dt = datetime.datetime.strptime(tsStr)
    except:
        NTtracebackError()
        NTerror("Failed to parse datetime from: %s" % tsStr )
        return None

    return rev, dt
# end def

def execfile_(filename, globals_=None, locals_=None):
    "Carefull this program can kill."
    if globals_ is None:
        globals_ = globals()
    if locals_ is None:
        locals_ = globals_
    text = file(filename, 'r').read()
    exec text in globals_, locals_
# end def

def NTflatten(obj):
    'Returns a tuple instead of the more commonly used NTlist or straight up list because this is going to be used for formatted printing.'
    if not isinstance(obj, (list, tuple)):
        NTerror("Object is not a list or tuple: %s", obj)
        return None
    result =[]
    for element in obj:
        if isinstance(element, (list, tuple)):
            elementFlattened = NTflatten(element)
            if not isinstance(elementFlattened, (list, tuple)):
                NTerror("ElementFlattened is not a list or tuple: %s", obj)
                return None
            result += elementFlattened
        else:
            result.append(element)
        # end if
    # end for
    return tuple( result )
# end def

def transpose(a):
    '''Compute the transpose of a matrix. Moved from svd package where it was disabled.'''
    m = len(a)
    n = len(a[0])
    at = []
    for i in range(n): at.append([0.0]*m)
    for i in range(m):
        for j in range(n):
            at[j][i]=a[i][j]
    return at
# end def


def lenRecursive(obj, max_depth = 5):
    """Count the number of values recursively. Walk thru any children elements that are also of type dict
    {a:{b:None, c:None} will give a length of 2
    """
    if not isinstance(obj, (list, tuple, dict)):
        NTerror("In lenRecursive the input was not a dict or list instance but was a %s" % str(obj))
        return None
    count = 0    
    eList = obj
    if isinstance(obj, dict):
        eList = obj.values()        
    for element in eList:
        if element == None:
            count += 1
            continue
        if isinstance(element, (list, tuple, dict)):
            new_depth = max_depth - 1
            if new_depth < 0:
                count += 1 # still count but do not go to infinity and beyond
                continue 
            count += lenRecursive(element, new_depth)
            continue
        count += 1        
    # end for
    return count
# end def

def setToSingleCoreOperation():
    'Set the cing attribute .ncpus to 1'
    if cing.ncpus > 1:
        NTmessage("Scaling back to single core operations")
        cing.ncpus = 1
        return
    NTmessage("Maintaining single core operations")
# end def
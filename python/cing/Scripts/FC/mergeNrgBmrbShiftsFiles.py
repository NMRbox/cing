__author__ = 'tjr22'

#@PydevCodeAnalysisIgnore # pylint: disable-all
"""
Use akin linkNmrStarData.py, so e.g.:

python -u $CINGROOT/python/cing/Scripts/FC/mergeNrgBmrbShifts.py 1ieh.tgz -bmrbCodes bmr4969_21.str -raise -force
"""

from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
#from cing.NRG.doAnnotateNrgCing import bmrbDir
from cing.NRG.settings import dir_S
from cing.NRG.shiftPresetDict import presetDict
from cing.core.classes import Project
from memops.general.Io import saveProject
#from pdbe.adatah.Generic import DataHandler
#from pdbe.adatah.NmrRestrGrid import nmrGridDataDir #@UnusedImport
from pdbe.adatah.NmrStar import NmrStarHandler
#from pdbe.adatah.Util import runConversionJobs #@UnusedImport
#from recoord2.pdbe.Constants import projectDirectory as loadDir
#from pdbe.adatah.Bmrb    import bmrbArchiveDataDir #@UnresolvedImport


import sys, os, time, traceback, shutil

# Import Api and related
from memops.api import Implementation
from memops.universal.Util import drawBox

from ccpnmr.format.process.matchResonToMolSys import matchResonToMolSys
from ccpnmr.format.process.sequenceCompare import SequenceCompare


#####################################
# Generic dataHandling code/classes #
#####################################

class MergeNrgBmrbShifts(NmrStarHandler):

    baseName = 'nrgBmrbMerge' # default for ccpn top directory

    # List of formats used
    formatList = ['NmrStar']
    bmrbFileFormat = "%s_21.str" # Used indirectly as well perhaps.
    # These can be reset if necessary... not part of main class
#    loadDir = cingDirTmp
#    projectDirectory = os.path.join(archivesCcpnDataDir, 'nrgBmrbMerge')
    projectDirectory = cingDirTmp
    presetDict = presetDict

#####################################################################################################################################
    errorFileFormat = '%s.errors.'
    fileWrittenNameFormat = '%s.DONE'
    noExperimentalDataName = 'NO_EXP_DATA'
    logFileFormat = '%s.log'

    class DataHandlerError(StandardError):

        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

  #
  # Initialisation
  #

    def __init__(self,setupArgs):

        self.curStdout = sys.stdout # Track current output to reset later
        (raiseError,forceWrite,timeFlag) = self.handleArguments(setupArgs) # Handle input arguments for setting up script...
        self.setBaseName() # In case need to tweak baseName, can do this here...
        self.initialiseVars() # Initialise some vars (needs to be set up in subclass!)

        # Decide whether current pdb code should be converted or not,
        # and set up output files if necessary
        skipEntry = self.setupConversion(forceWrite = forceWrite)
        if not skipEntry:
            try:
                self.runSpecific()
                self.writeDoneFile()
            except:
                self.catchError(raiseError,timeFlag)

        sys.stdout = self.curStdout # Always reset output...


    def setBaseName(self):
        return


    def initialiseVars(self):
        '''
        Sets up some file information - can be set to 'pass' if none of these required.
        '''

        self.errorFile = self.errorFileFormat % self.baseName                      # Name of the error file generated by this script
        self.fileWrittenName = self.fileWrittenNameFormat % self.baseName          # Name of the file written in entry-specific directory when script finished
        self.logFile = self.logFileFormat % self.baseName                          # File to write the log info to


    def loadProject(self):
        '''
        Can put in function in subclasses to load data if available here...
        '''
        return False


    def handleArguments(self,sysArgs):
        '''
        Initialize script based on arguments that are passed in
        '''
        if not len(sysArgs) >= 2:
            sys.exit()

        self.compressedCcpnProject = sysArgs[1] # First argument should always be PDB code
        self.idCode = self.compressedCcpnProject.split('.')[0]

        # Raise error (effectively crashes script if something goes wrong)
        if '-raise' in sysArgs:
            raiseError = True
        else:
            raiseError = False


        # Force writing (even if DONE file written)
        if '-force' in sysArgs:
            forceWrite = True
        else:
            forceWrite = False

        # Do not write out files - depends on implementation which files, if any!
        if '-noWrite' in sysArgs:
            self.writeFiles = False
        else:
            self.writeFiles = True

        # Loading only mode (not always implemented!)
        if '-load' in sysArgs:
            self.loadOnly = True
        else:
            self.loadOnly = False

        # Test mode (not always implemented!)
        if '-test' in sysArgs:
            self.testMode = True
        else:
            self.testMode = False

        # Interact via GUI or not?
        if '-noGui' in sysArgs:
            self.guiRoot = None
        else:
            import Tkinter
            self.guiRoot = Tkinter.Tk()

        # Class specific arguments
        self.handleSpecificArguments(sysArgs)
        timeFlag = time.strftime("%Y-%b-%d.%H.%M", time.gmtime(time.time()))
        self.timeFlag = timeFlag

        return (raiseError,forceWrite,timeFlag)


    def handleSpecificArguments(self,sysArgs):
        pass


    def conversionPrecheck(self):
        skipFlag = False
        if not self.idCode:
            skipFlag = True
        return skipFlag


    def setupConversion(self,forceWrite = False):

        # Precheck in case argument handling failed
        skipFlag = self.conversionPrecheck()

        # Set up entry, load if possible
        if not skipFlag:
            # Code to set up the files for a conversion.
            self.entryDir = os.path.join(self.projectDirectory,self.idCode)
            self.presets = {}

            # Check if can load the project, if defined in subclass...
            # Also remove project if already exists
            if not forceWrite:
                if self.loadProject():
                    skipFlag = True

            else:
                ccpnProjectDir = os.path.join(self.entryDir,self.baseName)
                if os.path.exists(ccpnProjectDir):
                    print "Removing existing project..."
                    shutil.rmtree(ccpnProjectDir)

        # Proceed with creating this entry
        if not skipFlag:

            # First check if exists, create if not
            if not os.path.exists(self.entryDir):
              os.mkdir(self.entryDir)

            # Check if idCode needs to be handled, if it does then set up necessary info
            if os.path.isdir(self.entryDir):
                if not forceWrite:
                    skipFlag = self.setSkipFlag()
                if not skipFlag:
                    self.curStdout.write("Doing %s...\n" % self.idCode)
                    self.curStdout.flush()
                    self.setPresets()
                    self.setOutput(forceWrite)
        return skipFlag


    def setSkipFlag(self):

        skipFlag = False
        tempFiles = os.listdir(self.entryDir)
        if self.projectDone(tempFiles = tempFiles):
            self.curStdout.write("Bypassing %s...\n" % self.idCode)
            skipFlag = True
        if 'SKIP' in tempFiles:
            self.curStdout.write("Skipping %s...\n" % self.idCode)
            skipFlag = True
        # SKIPTEMP: only when e.g. mapping has already been found
        if 'SKIPTEMP' in tempFiles:
            self.curStdout.write("Skipping temporarily %s...\n" % self.idCode)
            skipFlag = True
        return skipFlag


    def projectDone(self,tempFiles = None):

        projectDone = False

        if not tempFiles:
            if os.path.exists(self.entryDir):
                tempFiles = os.listdir(self.entryDir)
            else:
                tempFiles = []

        if self.fileWrittenName in tempFiles:
            projectDone = True

        return projectDone


    def setPresets(self):

        if self.presetDict.has_key(self.idCode):
            self.curStdout.write("  Using preset values...\n")
            self.presets = self.presetDict[self.idCode]

            # Print out comment if available
            if self.presetDict[self.idCode].has_key('comment'):
                commentLines = self.presetDict[self.idCode]['comment'].split("\n")
                for commentLine in commentLines:
                    self.curStdout.write("    > %s\n" % commentLine)


    def setOutput(self,forceWrite):

        fileWrittenPath = os.path.join(self.entryDir,self.fileWrittenName)
        if os.path.exists(fileWrittenPath):
            os.remove(fileWrittenPath)

        if forceWrite != -1:
            fout = open(os.path.join(self.entryDir,self.logFile),'w')

        if forceWrite != -1:
            sys.stdout = fout

    def setupProject(self):

        # Create a CCPN project (defined locally in script!)
        self.ccpnProject = Implementation.MemopsRoot(name = self.idCode)
        self.nmrProject = self.ccpnProject.newNmrProject(name = self.ccpnProject.name)

        # Tag with the data (new as of 17/11/2008)
        appDataCreationDate = Implementation.AppDataString(application = "DataHandler", keyword = 'creationDate', value = self.timeFlag)
        self.nmrProject.addApplicationData(appDataCreationDate)

    def initialiseCcpn(self):

        self.setupProject()
        self.setupMolSystem()

        # Set up the formatConverter stuff
        self.createFormatObjects()

    def setupMolSystem(self):

        # Create a molSystem for the PDB information
        self.molSystem = self.ccpnProject.newMolSystem(code = self.idCode)

    def setupEntry(self,studyTitle,entryTitle,entryDetails,textArgs = None,entryName = None):

        if not textArgs:
            textArgs = (self.idCode,)

        if not entryName:
            entryName = self.baseName

        # Set up the NMR entry store
        nmrEntryStore = self.ccpnProject.currentNmrEntryStore
        if not nmrEntryStore:
            nmrEntryStore = self.ccpnProject.findFirstNmrEntryStore()
        if not nmrEntryStore:
            nmrEntryStore = self.ccpnProject.newNmrEntryStore(name = self.ccpnProject.name)

        # Set up a study
        if studyTitle.count("%"):
            studyName = studyTitle % textArgs
        else:
            studyName = studyTitle

        study = nmrEntryStore.findFirstStudy(name = studyName)
        if not study:
            study = nmrEntryStore.newStudy(name = studyName,studyType = 'NMR')

        # Create a new entry
        self.entry = nmrEntryStore.newEntry(
                               molSystem = self.molSystem,
                               name = '%s_%s' % (entryName,'_'.join(textArgs)),
                               title = entryTitle % textArgs,
                               details = entryDetails % textArgs,
                               study = study)

    def setupStructureGeneration(self,strucGenName = 'Original constraints'):
        '''
        Create a structure generation for the coordinates and an nmrConstraintStore for the constraints...
        '''

        nmrConstraintStore = self.ccpnProject.newNmrConstraintStore(nmrProject = self.nmrProject)

        self.strucGen = self.nmrProject.newStructureGeneration(name = strucGenName, nmrConstraintStore = nmrConstraintStore)
        self.entry.addStructureGeneration(self.strucGen)


    def createFormatObjects(self):

        if self.guiRoot:
            allowPopups = True
        else:
            allowPopups = False

        self.formatObjectDict = {}

        for format in self.formatList:
            formatModule = __import__('ccpnmr.format.converters.%sFormat' % format,{},{},'%sFormat' % format)
            formatClass = getattr(formatModule,'%sFormat' % format)
            formatObject = formatClass(self.ccpnProject,self.guiRoot,verbose = 1,allowPopups = allowPopups)

            self.formatObjectDict[format] = formatObject


    def runLinkResonances(self, useAmbiguity = True, resonanceType = 'fixed', formatName = 'NmrStar', assignFormat = 'nmrStar', nmrConstraintStore = None, runs = 1):

        keywds = {}

        # Get relevant info from presets
        if self.presets.has_key('linkResonances'):
          scriptPresets = self.presets['linkResonances']
          if scriptPresets.has_key('runs'):
              runs = scriptPresets['runs']
          if scriptPresets.has_key('keywds'):
              keywds = scriptPresets['keywds']

      # Define type of info to be linked...
        if resonanceType == 'fixed':
            if not nmrConstraintStore:
                if hasattr(self,'strucGen'):
                    strucGen = self.strucGen
                else:
                    strucGen = self.entry.findFirstStructureGeneration()
                nmrConstraintStore = strucGen.nmrConstraintStore

            if not nmrConstraintStore:
                nmrConstraintStore = self.nmrProject.findFirstNmrConstraintStore()

            resonances = nmrConstraintStore.sortedFixedResonances()

            keywds['globalStereoAssign'] = True
            keywds['nmrConstraintStore'] = nmrConstraintStore

        elif resonanceType == 'nmr':
            strucGen = None
            resonances = self.entry.root.currentNmrProject.sortedResonances()
            keywds['globalStereoAssign']    = False

        # Set default keywords - can be reset in specificLinkResonancesSettings!
        keywds['setSingleProchiral']    = True
        keywds['setSinglePossEquiv']    = True
        keywds['minimalPrompts']        = True
        keywds['useCommonNames']        = False
        keywds['useAmbiguity']          = useAmbiguity
        keywds['useLinkResonancePopup'] = False
        keywds['useEmptyNamingSystems'] = False

        if formatName[1:] != assignFormat[1:]:
            keywds['assignFormat'] = assignFormat

        # Specific things to do before running linkResonances
        self.specificLinkResonancesSettings(keywds)

        # Check if need to do automapping
        if not keywds.has_key('forceDefaultChainMapping') and not keywds.has_key('forceChainMappings'):
            self.drawBoxDelimiter("Attempting automatic chain mapping (no valid presets available)")
            # Use automapping in this case
            forceChainMappings = matchResonToMolSys(resonances,self.molSystem,assignFormat = assignFormat,test=self.testMode)
            if forceChainMappings:
                keywds['forceChainMappings'] = forceChainMappings
                print "  Automatically setting chain mappings to %s" % str(forceChainMappings)
            else:
                # Try more refined mapping - this is run afterwards because it will give different results, should
                # only be run for new cases.
                sequenceComparison = SequenceCompare()

                # Set CCPN info
                sequenceComparison.createCcpnChainInformation(self.molSystem.sortedChains())
                sequenceComparison.getFormatFileInformation(resonances,assignFormat)

                # Write out error file if no data available...
                if not sequenceComparison.formatFileResidueDict:
                    self.writeNoExperimentalDataFile()
                    forceChainMappings = {}

                else:
                    sequenceComparison.createFormatFileChainInformation()
                    # Now run the comparison...
                    forceChainMappings = sequenceComparison.compareFormatFileToCcpnInfo()

                if forceChainMappings:
                    keywds['forceChainMappings'] = forceChainMappings
                    print "  Automatically setting chain mappings by alignment to %s" % str(forceChainMappings)

        # Run linkResonances
        for i in range(0,runs):
            #print keywds
            self.formatObjectDict[formatName].linkResonances(**keywds)

    def specificLinkResonancesSettings(self,keywds):
        '''
        Can redefine things in here for specific import
        '''
        pass


    def checkAssignmentLevel(self, resonancesStore):

        allResonances = 0
        assignedResonances = 0

        if resonancesStore.className == 'NmrProject':
            resonances = resonancesStore.resonances
        else:
            resonances = resonancesStore.fixedResonances

        for resonance in resonances:
            allResonances += 1
            if resonance.resonanceSet:
                assignedResonances += 1

        if not assignedResonances:
            raise self.DataHandlerError("No assigned resonances present - entry ignored.")

        elif (assignedResonances * 1.0 / allResonances) < 0.98:
            raise self.DataHandlerError("Less than 98% of resonances assigned - entry ignored.")


    def setCcpnProjectRepository(self,ccpnDir = 'ccpn'):

        # Replaces setCcpnProjectPaths
        outputPath = os.path.join(self.entryDir,ccpnDir)

        # In new API have to make sure that old files are removed first!
        if os.path.exists(outputPath):
          shutil.rmtree(outputPath)

        repository = self.ccpnProject.findFirstRepository(name = 'userData')
        repository.url = Implementation.Url(path = outputPath)


    def writeNoExperimentalDataFile(self):

        noExpDataFile = open(os.path.join(self.entryDir,self.noExperimentalDataName),'w')
        noExpDataFile.write(time.strftime("%Y-%b-%d.%H.%M", time.gmtime(time.time())))
        noExpDataFile.close()


    def writeDoneFile(self):

        # Write out final information
        doneFile = open(os.path.join(self.entryDir,self.fileWrittenName),'w')
        doneFile.write(time.strftime("%Y-%b-%d.%H.%M", time.gmtime(time.time())))
        doneFile.close()


    def drawBoxDelimiter(self,boxText):

        print
        print drawBox(boxText)
        print


    def catchError(self,raiseError,timeFlag):

        if raiseError:
            raise
        else:
            error = "    %s" % traceback.format_exception_only(sys.exc_type,sys.exc_value)[-1]
            ferrors = open(os.path.join(self.projectDirectory,self.idCode,self.errorFile + timeFlag),'w')
            ferrors.write(self.idCode)
            ferrors.write(error)
            ferrors.write(os.linesep)
            ferrors.flush()
            ferrors.close()
            sys.stdout = self.curStdout
            print error

#####################################################################################################################################


    def setBaseName(self):
        self.baseName = self.idCode


    def loadProject(self):
        modelCount = 1
        ccpnFile = self.compressedCcpnProject
        project = Project.open(self.idCode, status='new')
        # Can read tgz files.
        if project.initCcpn(ccpnFolder=ccpnFile, modelCount=modelCount) == None:
            nTerror("Failed to read: %s" % ccpnFile)
            return True
#        self.ccpnProject = loadCcpnTgzProject(os.path.join(self.loadDir, self.idCode, 'linkNmrStarData'))
        self.ccpnProject = project.ccpn


    def runSpecific(self):
        """ Returns True on error """
        entryCodeChar2and3 = self.idCode[1:3]
        projectDirectory = os.path.join(dir_S, entryCodeChar2and3, self.idCode)
        os.chdir(projectDirectory)
        curDir = os.getcwd() #@UnusedVariable
        nTdebug("curDir: %s" % curDir)
#        ccpnDir = self.baseName #@UnusedVariable

        # Read the existing CCPN project, set up format object dict
        self.loadProject()
        self.createFormatObjects()

        self.entry = self.ccpnProject.findFirstNmrEntryStore().findFirstEntry()
        self.molSystem = self.ccpnProject.findFirstMolSystem()
        self.nmrProject = self.ccpnProject.findFirstNmrProject()
        self.strucGen = self.nmrProject.findFirstStructureGeneration()

        bmrbCodesLength = len(self.bmrbCodes)
        if not bmrbCodesLength:
            nTerror("Not a single BMRB entry presented.")
            return
        if bmrbCodesLength > 1:
            nTwarning("Currently NRG-CING only loads a single BMRB entry's CS. Skipping others.")

        # Read the BMRB NMR-STAR file (only chem shift data)
#        for bmrbCode in self.bmrbCodes:
        bmrbFile = self.bmrbCodes[0]
        bmrbCode = bmrbFile.split('_')[0]
        self.initShiftPresets(bmrbCode)
    #          bmrbNmrStarFile = os.path.join(bmrbArchiveDataDir, self.bmrbFileFormat % bmrbCode)
#        bmrb_id = int(bmrbCode[3:])
#        digits12 = "%02d" % (bmrb_id % 100)
#        inputStarDir = os.path.join(bmrbDir, digits12)
#         inputStarDir = os.path.join(bmrbDir, bmrbCode)
#         if not os.path.exists(bmrbFile):
#             nTerror("Input star dir not found: %s" % bmrbFile)
#             return True
        inputStarFile = bmrbFile
        if not os.path.exists(inputStarFile):
            nTerror("inputStarFile not found: %s" % inputStarFile)
            return True
        nTdebug("Start readNmrStarFile")
        self.readNmrStarFile(inputStarFile, components=['measurements'])
        # Try to autoset mapping...
        nTdebug("Start setBmrbNmrStarMapping")
        self.setBmrbNmrStarMapping(inputStarFile)
        # Run linkResonances, using custom keywds set above
        nTdebug("Start runLinkResonances")
        self.runLinkResonances(resonanceType='nmr')
        # Save project in new location
        newPath = self.baseName
        nTmessage('Saving to new path: %s in cwd: %s' % (newPath, os.getcwd()))
        saveProject(self.ccpnProject, removeExisting=True, newPath=newPath, newProjectName=self.baseName)
        ccpnTgzFile = "%s.tgz" % self.idCode
        cmd = "tar -czf %s %s" % (ccpnTgzFile, newPath)
        if do_cmd(cmd):
            nTerror("Failed tar")
            return None
        nTmessage("Saved ccpn project to tgz: %s" % ccpnTgzFile)

    def initShiftPresets(self, bmrbCode):
        if not self.presetDict.has_key(bmrbCode):
            return
        sys.__stdout__.write("  Using shift preset values...\n")
        self.presets = self.presetDict[bmrbCode]
        # Print out comment if available
        if 1:
            sys.__stdout__.write("    > %s\n" % self.presets)
        else: # Just comments
            if self.presets.has_key('comment'):
                commentLines = self.presets['comment'].split("\n")
                for commentLine in commentLines:
                    sys.__stdout__.write("    > %s\n" % commentLine)

    def handleSpecificArguments(self, sysArgs):
        self.bmrbCodes = []
        if '-bmrbCodes' in sysArgs:
            for sysArgIndex in range(sysArgs.index("-bmrbCodes") + 1, len(sysArgs)):
                sysArgValue = sysArgs[sysArgIndex]
                if sysArgValue[0] == '-':
                    break
                self.bmrbCodes.append(sysArgValue)
        if not self.bmrbCodes:
            raise self.DataHandlerError, "Need to pass in at least one BMRB code with -bmrbCodes flag for this script to work!"


if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    MergeNrgBmrbShifts(sys.argv)
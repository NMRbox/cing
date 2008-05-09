from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.Imagery import convert2Web
from cing.Libs.Imagery import joinPdfPagesByGhostScript
from cing.Libs.NTplot import useMatPlotLib
from cing.Libs.NTutils import NTdebug
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)
    NTdebug("Using matplot (True) or biggles: %s", useMatPlotLib)

    def testConvert2Web(self):
        fn = "pc_nmr_11_rstraints.ps"
        self.assertTrue( os.path.exists( cingDirTestsData) and os.path.isdir(cingDirTestsData ) )
        inputPath = os.path.join(cingDirTestsData,fn)
        outputPath = cingDirTmp
        self.failIf( os.chdir(outputPath), msg=
            "Failed to change to temporary test directory for data: "+outputPath)
        fileList = convert2Web( inputPath, outputDir=outputPath )
        NTdebug( "Got back from convert2Web output file names: " + `fileList`)
        self.assertNotEqual(fileList,True)
        if fileList != True:
            for file in fileList:
                self.assertNotEqual( file, None)

        fn1 = "pc_nmr_11_rstraints.pdf"
        self.assertFalse( joinPdfPagesByGhostScript( [fn1,fn1], "pc_nmr_11_rstraints_echo.pdf"))

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
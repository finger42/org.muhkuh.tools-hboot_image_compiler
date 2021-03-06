import unittest

import os
import re
import shutil
import subprocess
import sys
import traceback

class TestExpectedBinaries(unittest.TestCase):

    def setUp(self):
        self.strTestsBaseDir = os.path.realpath(os.path.dirname(__file__))
        self.strOutputBaseDir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'targets', 'tests', 'output'))
        self.strHBootImageCompiler = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'targets', 'tests', 'bin', 'hboot_image_compiler', 'hboot_image_compiler'))
        self.strHBootNetx90AppImageCompiler = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'targets', 'tests', 'bin', 'hboot_image_compiler', 'hboot_image_compiler', 'netx90_app_image.py'))
        
    def __get_env_var(self, tMatch):
        strEnvKey = tMatch.group(1)
        if strEnvKey not in os.environ:
            raise Exception('Referened non-existing environment variable "%s".' % strEnvKey)
        return os.environ[strEnvKey]

    def __run_hboot_image_compiler(self, strCwd, strXml, strOutput, strNetx, atExtraArguments):
        # Save the current working directory for later.
        strOldPath = os.getcwd()

        # Change to the new working directory.
        os.chdir(strCwd)

        # Run the HBOOT image compiler.
        astrCmd = [
            sys.executable,
            self.strHBootImageCompiler,
            '--netx-type', strNetx
        ]
        if atExtraArguments is not None:
            tRe = re.compile('%%([\w]+)%%')
            # Replace all ENV vars in the extra arguments.
            for strArg in atExtraArguments:
                astrCmd.append(tRe.sub(self.__get_env_var, strArg))
        astrCmd.extend([
            strXml,
            strOutput
        ])

        subprocess.check_output(astrCmd)

        # Restore the old working directory.
        os.chdir(strOldPath)

    def __test_with_reference_bin(self, strInput, strReference, strNetx, atExtraArguments, atCopyFiles):
        strInputBase = os.path.basename(strInput)
        strInputPathFull = os.path.join(self.strTestsBaseDir, strInput)
        strInputDirectoryFull = os.path.dirname(strInputPathFull)

        strOutputDirectory = os.path.dirname(strReference)

        # Create the output folder.
        strOutputDirectoryFull = os.path.join(self.strOutputBaseDir, strOutputDirectory)
        if os.path.exists(strOutputDirectoryFull) == False:
            os.makedirs(strOutputDirectoryFull)
        strOutputPathFull = os.path.join(self.strOutputBaseDir, strReference)

        # Copy files.
        if atCopyFiles is not None:
            for strFile in atCopyFiles:
                strSrcAbs = os.path.join(self.strTestsBaseDir, strFile)
                strSrcDirAbs = os.path.dirname(strSrcAbs)
                strDstAbs = os.path.join(self.strOutputBaseDir, strFile)
                strDstDirAbs = os.path.dirname(strDstAbs)
                if os.path.exists(strSrcDirAbs) == False:
                    os.makedirs(strSrcDirAbs)
                if os.path.exists(strDstDirAbs) == False:
                    os.makedirs(strDstDirAbs)
                shutil.copy(strSrcAbs, strDstAbs)

        # Copy the input file to the working folder.
        shutil.copy(strInputPathFull, strOutputDirectoryFull)

        # The working folder is the test path.
        strCwd = strOutputDirectoryFull

        self.__run_hboot_image_compiler(strCwd, strInputPathFull, strOutputPathFull, strNetx, atExtraArguments)

        
        strRefPath = os.path.join(self.strTestsBaseDir, strReference)
        #print("Comparing: Ref: %s <-> Out: %s" % (strRefPath, strOutputPathFull))
        # Read the reference binary.
        tFile = open(strRefPath, 'rb')
        strBinReference = tFile.read()
        tFile.close()

        # Read the output.
        tFile = open(strOutputPathFull, 'rb')
        strBinOutput = tFile.read()
        tFile.close()

        self.assertEqual(strBinReference, strBinOutput)

    def __run_hboot_image_compiler_public(self, strCwd, strXml, strOutput, strNetx, atExtraArguments, strExpectedError = None):
        # Save the current working directory for later.
        strOldPath = os.getcwd()

        # Change to the new working directory.
        os.chdir(strCwd)

        # Run the HBOOT image compiler.
        astrCmd = [
            sys.executable,
            self.strHBootImageCompiler
        ]
        if strNetx:
            astrCmd.extend(['--netx-type-public', strNetx])
        if atExtraArguments is not None:
            tRe = re.compile('%%([\w]+)%%')
            # Replace all ENV vars in the extra arguments.
            for strArg in atExtraArguments:
                astrCmd.append(tRe.sub(self.__get_env_var, strArg))
        astrCmd.extend([
            strXml,
            strOutput
        ])

        if strExpectedError==None:
            subprocess.check_output(astrCmd)
        else:
            try:
                # If an exception occurs, the output is included in the exception as e.output.
                # stderr=subprocess.STDOUT appends the error messages to stdout.
                subprocess.check_output(astrCmd, stderr=subprocess.STDOUT)
            except Exception as e:
                print("Exception output:")
                print(e.output)
                if strExpectedError in e.output:
                    print("Found expected error message")
                else:
                    print('Did not find expected error message')
                    raise Exception('Did not find expected error message')

        # Restore the old working directory.
        os.chdir(strOldPath)

    def __test_with_reference_bin_public(self, strInput, strReference, strNetx, atExtraArguments, atCopyFiles, strExpectedError = None):
        strInputBase = os.path.basename(strInput)
        strInputPathFull = os.path.join(self.strTestsBaseDir, strInput)
        strInputDirectoryFull = os.path.dirname(strInputPathFull)

        strOutputDirectory = os.path.dirname(strReference)

        # Create the output folder.
        strOutputDirectoryFull = os.path.join(self.strOutputBaseDir, strOutputDirectory)
        if os.path.exists(strOutputDirectoryFull) == False:
            os.makedirs(strOutputDirectoryFull)
        strOutputPathFull = os.path.join(self.strOutputBaseDir, strReference)

        # Copy files.
        if atCopyFiles is not None:
            for strFile in atCopyFiles:
                strSrcAbs = os.path.join(self.strTestsBaseDir, strFile)
                strSrcDirAbs = os.path.dirname(strSrcAbs)
                strDstAbs = os.path.join(self.strOutputBaseDir, strFile)
                strDstDirAbs = os.path.dirname(strDstAbs)
                if os.path.exists(strSrcDirAbs) == False:
                    os.makedirs(strSrcDirAbs)
                if os.path.exists(strDstDirAbs) == False:
                    os.makedirs(strDstDirAbs)
                shutil.copy(strSrcAbs, strDstAbs)

        # Copy the input file to the working folder.
        shutil.copy(strInputPathFull, strOutputDirectoryFull)

        # The working folder is the test path.
        strCwd = strOutputDirectoryFull

        self.__run_hboot_image_compiler_public(strCwd, strInputPathFull, strOutputPathFull, strNetx, atExtraArguments, strExpectedError)

        
        strRefPath = os.path.join(self.strTestsBaseDir, strReference)
        #print("Comparing: Ref: %s <-> Out: %s" % (strRefPath, strOutputPathFull))
        # Read the reference binary.
        tFile = open(strRefPath, 'rb')
        strBinReference = tFile.read()
        tFile.close()

        # Read the output.
        tFile = open(strOutputPathFull, 'rb')
        strBinOutput = tFile.read()
        tFile.close()

        self.assertEqual(strBinReference, strBinOutput)

# ######################################################################## 
#                                   
# echo Build an image for intflash + SDRAM with empty code segments in SDRAM
# python "%TD%\app_image.py" ^
# -c %OC% -d %OD% -r %RE% ^                          - atExtraArguments
# -A tElf="%BD%\netx90_app_iflash_sdram-empty.elf" ^ - atExtraArguments
# -A headeraddress_extflash=0x64300000 ^             - atExtraArguments
# -A segments_intflash=".header,.code" ^             - atExtraArguments
# -A segments_extflash=".code_SDRAM1,.code_SDRAM2" ^ - atExtraArguments
# "%TD%\Linker\app_images_iflash_extflash.xml"       - strInput
# "%BD%\netx90_app_iflash_sdram-empty.nai" "%BD%\netx90_app_iflash_sdram-empty.nae"  - strReference
# 
# strNetx is currently not needed
# strReference may be multiple files

    def __run_app_hboot_image_compiler(self, strCwd, strXml, astrOutput, atExtraArguments, strExpectedError = None):
        
        # Save the current working directory for later.
        strOldPath = os.getcwd()

        # Change to the new working directory.
        os.chdir(strCwd)

        # Run the HBOOT image compiler.
        astrCmd = [
            sys.executable,
            self.strHBootNetx90AppImageCompiler,
        ]
        if atExtraArguments is not None:
            tRe = re.compile('%%([\w]+)%%')
            # Replace all ENV vars in the extra arguments.
            for strArg in atExtraArguments:
                astrCmd.append(tRe.sub(self.__get_env_var, strArg))
                
        astrCmd.append(
            strXml,
        )
        astrCmd.extend(astrOutput)

        if strExpectedError==None:
            subprocess.check_output(astrCmd)
        else:
            try:
                # If an exception occurs, the output is included in the exception as e.output.
                # stderr=subprocess.STDOUT appends the error messages to stdout.
                subprocess.check_output(astrCmd, stderr=subprocess.STDOUT)
            except Exception as e:
                print("Exception output:")
                print(e.output)
                if strExpectedError in e.output:
                    print("Found expected error message")
                else:
                    print('Did not find expected error message')
                    raise Exception('Did not find expected error message')

        # Restore the old working directory.
        os.chdir(strOldPath)

    def __test_netx90_appimg_with_reference_bin(self, strInput, astrReferences, atExtraArguments, atCopyFiles, strExpectedError = None):
        strInputBase = os.path.basename(strInput)
        strInputPathFull = os.path.join(self.strTestsBaseDir, strInput)
        strInputDirectoryFull = os.path.dirname(strInputPathFull)

        # Create the output folder, based on the parent directory of the first reference file.
        strReference = astrReferences[0]
        strOutputDirectory = os.path.dirname(strReference)
        strOutputDirectoryFull = os.path.join(self.strOutputBaseDir, strOutputDirectory)
        if os.path.exists(strOutputDirectoryFull) == False:
            os.makedirs(strOutputDirectoryFull)
            
        #strOutputPathFull = os.path.join(self.strOutputBaseDir, strReference)
        astrOutputPaths = []
        for strReference in astrReferences:
            if strReference != '':
                strOutputPathFull = os.path.join(self.strOutputBaseDir, strReference)
                astrOutputPaths.append(strOutputPathFull)
            else:
                astrOutputPaths.append(strReference)
        # Copy files.
        if atCopyFiles is not None:
            for strFile in atCopyFiles:
                strSrcAbs = os.path.join(self.strTestsBaseDir, strFile)
                strSrcDirAbs = os.path.dirname(strSrcAbs)
                strDstAbs = os.path.join(self.strOutputBaseDir, strFile)
                strDstDirAbs = os.path.dirname(strDstAbs)
                if os.path.exists(strSrcDirAbs) == False:
                    os.makedirs(strSrcDirAbs)
                if os.path.exists(strDstDirAbs) == False:
                    os.makedirs(strDstDirAbs)
                print("Copy file: %s -> %s" % (strSrcAbs, strDstAbs))
                shutil.copy(strSrcAbs, strDstAbs)

        # Copy the input file to the working folder.
        shutil.copy(strInputPathFull, strOutputDirectoryFull)

        # The working folder is the test path.
        strCwd = strOutputDirectoryFull

        print("CWD: %s" % strCwd)
        self.__run_app_hboot_image_compiler(strCwd, strInputPathFull, astrOutputPaths, atExtraArguments, strExpectedError = strExpectedError)
            
        # If an error is expected, do not try to verify the output files.
        if strExpectedError == None:
            for strReference in astrReferences:
                # Skip empty references.
                if strReference != '':
                    strRefPath = os.path.join(self.strTestsBaseDir, strReference)
                    strOutputPathFull = os.path.join(self.strOutputBaseDir, strReference)
                    print("Comparing: Ref: %s <-> Out: %s" % (strRefPath, strOutputPathFull))
                
                    # Read the reference binary.
                    tFile = open(strRefPath, 'rb')
                    strBinReference = tFile.read()
                    tFile.close()
            
                    # Read the output.
                    tFile = open(strOutputPathFull, 'rb')
                    strBinOutput = tFile.read()
                    tFile.close()
            
                    self.assertEqual(strBinReference, strBinOutput)
            
    # ######################################################################## 
    # Tests for netx90 APP images.
    # ELF_NETX90_APP_BLINKI_IFLASH etc. are the names of the blinki elf files, passed from SConstruct.
    
    # NXTHBOTIMG-47 test 2
    # a project that results in a single intflash boot image and specifies the segments to write to the boot image
    # NXTHBOTIMG-48 test 4a
    # no output file name is provided for NAE file. => NO NAE file is created. Create an ERROR, if a segment list is provided.
    def test_app_image_iflash(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            #'netx90_app_image/app_image_iflash.xml',
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash.nai',
                #''
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH%%',
                '-A', 'segments_intflash=.header,.code',
                '--sdram_split_offset', '0x400000',
            ],
            None
        )
        

    # NXTHBOTIMG-47 test 3
    # a project that results in a  single intflash boot image and specifies no segments. 
    # The boot image tool should use segments with the progbits flag set inside the elf file.

    def test_app_image_iflash_nosegments(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_image_iflash_nosegments.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_nosegments.nai'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH%%',
            ],
            None
        )
            
    # NXTHBOTIMG-47 test 1
    # a Project that results in two boot images, intflash + external flash
    # NXTHBOTIMG-48 test 1
    # an elf file that contains a section located in SDRAM
    # NXTHBOTIMG-61
    # The image contains a part that is loaded to the SDRAM which is split between COM and APP,
    # i.e. SDRAM address offset for the COM CPU is 0x400000
    def test_app_image_iflash_sdram(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_sdram.nai', 
                'netx90_app_image/netx90_app_iflash_sdram.nae'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH_SDRAM%%',
                '-A', 'headeraddress_extflash=0x64300000',
                '--sdram_split_offset', '0x400000',
                '-A', 'segments_intflash=.header,.code',
                '-A', 'segments_extflash=.code_SDRAM1,.code_SDRAM2',
            ],
            None
        )
        
    # NXTHBOTIMG-61
    # Same as above, except that the SDRAM is exclusive to the APP CPU
    # i.e. SDRAM address offset for the COM CPU is 0.
    def test_app_image_iflash_sdram_apponly(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_sdram_app.nai', 
                'netx90_app_image/netx90_app_iflash_sdram_app.nae'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH_SDRAM%%',
                '-A', 'headeraddress_extflash=0x64300000',
                '--sdram_split_offset', '0',
                '-A', 'segments_intflash=.header,.code',
                '-A', 'segments_extflash=.code_SDRAM1,.code_SDRAM2',
            ],
            None
        )

    # Build two images in Intflash:
    # Part 1 is at address 0 and contains only the vectors and image header,
    # Part 2 is at address 4K and contains the program itself.
    # This allows us to put an additional block (common header) between the vectors and the main program 
    # that is not included in the checksums/hashes.
    # Note: app_images_iflash_extflash and headeraddress_extflash/segments_extflash 
    #   are inadequately named in this case.
    def test_app_image_iflash_2part(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_part1_0x0000.nai', 
                'netx90_app_image/netx90_app_iflash_part2_0x1000.nai'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH_2PART%%',
                '-A', 'headeraddress_extflash=0x1000',
                '-A', 'segments_intflash=.header',
                '-A', 'segments_extflash=.code',
            ],
            None
        )
       
    # NXTHBOTIMG-48 test 2, segments for intflash specified
    #  an elf file that does not contain a section located in SDRAM 
    #  => create dummy NAE file (program inside INTflash ONLY)
    def test_app_image_iflash_nae_dummy(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_pseudo_sdram.nai', 
                'netx90_app_image/netx90_app_iflash_pseudo_sdram.nae'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH%%',
                '-A', 'headeraddress_extflash=0x64300000',
                '--sdram_split_offset', '0x400000',
                '-A', 'segments_intflash=.header,.code',
                '-A', 'segments_extflash=,',
            ],
            None
        )

    # NXTHBOTIMG-48 test 2, segments for intflash not specified
    #  an elf file that does not contain a section located in SDRAM 
    #  => create dummy NAE file (program inside INTflash ONLY)
    def test_app_image_iflash_nae_dummy_empty_segment_list(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_pseudo_sdram_no_seglist.nai', 
                'netx90_app_image/netx90_app_iflash_pseudo_sdram_no_seglist.nae'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH%%',
                '-A', 'headeraddress_extflash=0x64300000',
                '--sdram_split_offset', '0x400000',
                '-A', 'segments_intflash=',
                '-A', 'segments_extflash=,',
            ],
            None
        )

        
    # NXTHBOTIMG-48 test 4b
    # no output file name is provided for NAE file. => NO NAE file is created. Create an ERROR, if a segment list is provided.
    def test_app_image_iflash_nae_dummy_error(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_error.nai',
                #''
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH%%',
                '-A', 'headeraddress_extflash=0x64300000',
                '--sdram_split_offset', '0x400000',
                '-A', 'segments_intflash=.header,.code',
                '-A', 'segments_extflash=.some_segment',
            ],
            None,
            strExpectedError = "Output filename is empty but a segment list is specified"
        )

    # There should be an error if a segment containing loadable data is not used (code_SDRAM2)
    def test_app_image_iflash_unused_segment_error(self):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                'netx90_app_image/netx90_app_iflash_sdram_unused_segment_error.nai', 
                'netx90_app_image/netx90_app_iflash_sdram_unused_segment_error.nae'
            ],
            [   # extra args
                '-n', 'netx90_rev0',
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH_SDRAM%%',
                '-A', 'headeraddress_extflash=0x64300000',
                '--sdram_split_offset', '0x400000',
                '-A', 'segments_intflash=.header,.code',
                '-A', 'segments_extflash=.code_SDRAM1',
            ],
            None,
            strExpectedError = "There are unused segments containing data"
        )
    
    # NXTHBOTIMG-52
    # Test the -n/--netx command line arg by building the intflash image with different chip types 
    def __test_app_image_iflash(self, strNetxType, strOutputFile):
        self.__test_netx90_appimg_with_reference_bin(
            # XML file
            'netx90_app_image/app_images_iflash_extflash.xml',
            [   # output files
                strOutputFile, 
            ],
            [   # extra args
                '-n', strNetxType,
                '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
                '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH%%',
                '-A', 'segments_intflash=.header,.code',
            ],
            None
        )
        
    def test_app_image_iflash_netx90(self):
        self.__test_app_image_iflash('netx90', 'netx90_app_image/netx90_app_iflash_chiptype_netx90.nai')
        
    def test_app_image_iflash_netx90_mpw(self):
        self.__test_app_image_iflash('netx90_mpw', 'netx90_app_image/netx90_app_iflash_chiptype_netx90_mpw.nai')

    def test_app_image_iflash_netx90_rev0(self):
        self.__test_app_image_iflash('netx90_rev0', 'netx90_app_image/netx90_app_iflash_chiptype_netx90_rev0.nai')
        
    def test_app_image_iflash_netx90_rev1(self):
        self.__test_app_image_iflash('netx90_rev1', 'netx90_app_image/netx90_app_iflash_chiptype_netx90_rev1.nai')

        
        
    # The following tests (HWC for NXHX90-JTAG Rev. 3+4, start APP CPU) 
    # are used to run the APP boot images.
    # Write a hardware config to Intflash 0 offset 0 and netx90_COM_start_APP.nxi to offset 0x3000.
    
    def __app_image_hwc(self, strHwcName, strNetxType):
        self.__test_with_reference_bin(
            'netx90_app_image/hwc/hboot_image_hwc.xml',
            'netx90_app_image/hwc/%s.hwc' % strHwcName, 
            strNetxType, 
         ['-A', 'hw_config=../../../../../tests/netx90_app_image/hwc/%s.xml' % strHwcName], None)
    
    def test_hwc_nxhx90jtag_rev3_sdram_split(self):
        self.__app_image_hwc('next_chunk_hwc_nxhx90-jtag_rev3_hboot', 'NETX90')
    def test_hwc_nxhx90jtag_rev4_sdram_split(self):
        self.__app_image_hwc('next_chunk_hwc_nxhx90-jtag_rev4_hboot', 'NETX90B')
    def test_hwc_nxhx90jtag_rev3_sdram_app(self):
        self.__app_image_hwc('next_chunk_hwc_nxhx90-jtag_rev3_sdram_app_hboot', 'NETX90')
    def test_hwc_nxhx90jtag_rev4_sdram_app(self):
        self.__app_image_hwc('next_chunk_hwc_nxhx90-jtag_rev4_sdram_app_hboot', 'NETX90B')

    def test_start_app(self):
        self.__test_with_reference_bin('netx90_app_image/netx90_COM_start_APP.xml', 'netx90_app_image/netx90_COM_start_APP.nxi', 'NETX90', None, None)

    def test_data_concat(self):
        self.__test_with_reference_bin('data/data_concat.xml', 'data/data_concat.bin', 'NETX90_MPW', None, None)

    def test_data_file_alias(self):
        self.__test_with_reference_bin('data/data_file_alias.xml', 'data/data_file_alias.bin', 'NETX90', ['--alias', 'FillData=fill_data.bin'], ['data/fill_data.bin'])

    def test_data_hex(self):
        self.__test_with_reference_bin('data/data_hex.xml', 'data/data_hex.bin', 'NETX90_MPW', None, None)

    def test_data_uint08(self):
        self.__test_with_reference_bin('data/data_uint8.xml', 'data/data_uint8.bin', 'NETX90_MPW', None, None)

    def test_data_uint16(self):
        self.__test_with_reference_bin('data/data_uint16.xml', 'data/data_uint16.bin', 'NETX90_MPW', None, None)

    def test_data_uint32(self):
        self.__test_with_reference_bin('data/data_uint32.xml', 'data/data_uint32.bin', 'NETX90_MPW', None, None)

    def test_execute_file_elf(self):
        self.__test_with_reference_bin('execute/execute_file_elf.xml', 'execute/execute_file_elf.bin', 'NETX4000', ['--objcopy', '%%NETX4000_OBJCOPY%%', '--objdump', '%%NETX4000_OBJDUMP%%', '--readelf', '%%NETX4000_READELF%%', '--alias', 'Program=%%ELF_NETX4000_SKIP%%'], None)
        
    def test_binutils_path(self):
        fTestPassed = False
        strOldPath = os.getcwd()
        try:
            self.__test_with_reference_bin(
                'execute/execute_file_elf.xml', 'execute/execute_file_elf.bin', 'NETX4000', 
                ['--objcopy', '%%NETX4000_OBJCOPY%%_junk', # make the path invalid
                '--objdump', '%%NETX4000_OBJDUMP%%_junk', 
                '--readelf', '%%NETX4000_READELF%%_junk', 
                '--alias', 'Program=%%ELF_NETX4000_SKIP%%'], None)
        except Exception as e:
            print("Exception:")
            print(e)
            print("Exception output")
            print(e.output)
            strExpectedError = "Failed to call external program:"
            if strExpectedError in e.output:
                fTestPassed = True
                print("Found expected error message")
                
        os.chdir(strOldPath)
        assert fTestPassed, "Did not find expected error message"

    # NXTHBOTIMG-55
    # Build an execute_CA9 chunk with the target addresses both addresses set to 0. 
    def test_execute_enable_debugging_netx4000(self):
        self.__test_with_reference_bin(
            'execute/execute_CA9_enable_debugging_netx4000.xml',
            'execute/execute_CA9_enable_debugging_netx4000.bin', 
            'NETX4000', 
            [], None)

    def test_execute_address_netx90_mpw(self):
        self.__test_with_reference_bin('execute/execute_address_netx90_mpw.xml', 'execute/execute_address_netx90_mpw.bin', 'NETX90_MPW', None, None)

    def test_execute_address_netx90(self):
        self.__test_with_reference_bin('execute/execute_address_netx90.xml', 'execute/execute_address_netx90.bin', 'NETX90', None, None)

    def test_firewall_chunk(self):
        self.__test_with_reference_bin('firewall/firewall.xml', 'firewall/firewall.bin', 'NETX90', None, None)
    
    
    def test_header_NETX90_INTFLASH_flash_param_true(self):
        self.__test_with_reference_bin('header/header_NETX90_INTFLASH_flash_param_true.xml', 
        'header/header_NETX90_INTFLASH_flash_param_true.bin', 'NETX90', None, None)
        
    def test_header_NETX90_INTFLASH_flash_param_false(self):
        self.__test_with_reference_bin('header/header_NETX90_INTFLASH_flash_param_false.xml', 
        'header/header_NETX90_INTFLASH_flash_param_false.bin', 'NETX90', None, None)
        
    def test_header_NETX90_INTFLASH_empty(self):
        self.__test_with_reference_bin('header/header_NETX90_INTFLASH_empty.xml', 
        'header/header_NETX90_INTFLASH_empty.bin', 'NETX90', None, None)

    def test_header_NETX90_MPW_SQIROM_flash_param_true(self):
        self.__test_with_reference_bin('header/header_NETX90_MPW_SQIROM_flash_param_true.xml', 
        'header/header_NETX90_MPW_SQIROM_flash_param_true.bin', 'NETX90_MPW', None, None)
    
    def test_header_NETX4000_SQIROM0_flash_param_true(self):
        self.__test_with_reference_bin('header/header_NETX4000_SQIROM0_flash_param_true.xml', 
        'header/header_NETX4000_SQIROM0_flash_param_true.bin', 'NETX4000', None, None)
    
    
    def test_include_file_alias(self):
        self.__test_with_reference_bin('include/include_file_alias.xml', 'include/include_file_alias.bin', 'NETX4000', ['--alias', 'Data=data.xml'], ['include/data.xml'])
        
    def test_include_file_global_define(self):
        self.__test_with_reference_bin('include/include_file_global_define.xml', 'include/include_file_alias.bin', 'NETX90', ['-D', 'Data=data.xml'], ['include/data.xml'])
        
    def test_include_text_chunk_global_define(self):
        self.__test_with_reference_bin('include/include_text.xml', 'include/include_text.bin', 
        'NETX90', 
        ['-D', 'HWC_TYPE=MWC'], 
        ['include/text_placeholder.xml'])
        
    def test_include_text_chunk_parameter(self):
        self.__test_with_reference_bin('include/include_text_param.xml', 'include/include_text.bin', 
        'NETX90', 
        None,
        ['include/text_placeholder.xml'])
        
    def test_include_expressions(self):
        self.__test_with_reference_bin('include/expressions_top.xml', 'include/expressions.bin', 
        'NETX90', 
        None, 
        ['include/expressions_include.xml'])
        
    def test_include_conditionals(self):
        self.__test_with_reference_bin('include/conditionals_top.xml', 'include/conditionals.bin', 
        'NETX90', 
        None, 
        ['include/conditionals_include.xml'])
        
    def test_netx_types_netx4000(self):
        self.__test_with_reference_bin('netx_types/netx4000.xml', 'netx_types/netx4000.bin', 'NETX4000', None, None)

    def test_netx_types_netx4000_alternative(self):
        self.__test_with_reference_bin('netx_types/netx4000_alternative.xml', 'netx_types/netx4000_alternative.bin', 'NETX4000', None, None)

    def test_netx_types_netx4000_apply_port_control(self):
        self.__test_with_reference_bin('netx_types/netx4000_apply_port_control.xml', 'netx_types/netx4000_apply_port_control.bin', 'NETX4000', None, None)

    def test_netx_types_netx4000_relaxed_apply_port_control(self):
        self.__test_with_reference_bin('netx_types/netx4000_relaxed_apply_port_control.xml', 'netx_types/netx4000_relaxed_apply_port_control.bin', 'NETX4000_RELAXED', None, None)

    def test_netx_types_netx4100(self):
        self.__test_with_reference_bin('netx_types/netx4100.xml', 'netx_types/netx4100.bin', 'NETX4100', None, None)

    def test_netx_types_netx4100_alternative(self):
        self.__test_with_reference_bin('netx_types/netx4100_alternative.xml', 'netx_types/netx4100_alternative.bin', 'NETX4100', None, None)

    def test_netx_types_netx4100_apply_port_control(self):
        self.__test_with_reference_bin('netx_types/netx4100_apply_port_control.xml', 'netx_types/netx4100_apply_port_control.bin', 'NETX4100', None, None)

    def test_netx_types_netx90_alternative(self):
        self.__test_with_reference_bin('netx_types/netx90_alternative.xml', 'netx_types/netx90_alternative.bin', 'NETX90', None, None)

    def test_offset_decimal(self):
        self.__test_with_reference_bin('offset/offset_decimal.xml', 'offset/offset_decimal.bin', 'NETX90_MPW', None, None)

    def test_offset_hexadecimal(self):
        self.__test_with_reference_bin('offset/offset_hexadecimal.xml', 'offset/offset_hexadecimal.bin', 'NETX90_MPW', None, None)

    def test_offset_xip(self):
        self.__test_with_reference_bin('offset/offset_xip.xml', 'offset/offset_xip.bin', 'NETX90_MPW', None, None)

    def test_option_chunks_netx90_mpw_disable_iflash_redundancy(self):
        self.__test_with_reference_bin('option_chunks/netx90_mpw_disable_iflash_redundancy.xml', 'option_chunks/netx90_mpw_disable_iflash_redundancy.bin', 'NETX90_MPW', None, None)

    def test_option_chunks_netx90_options(self):
        self.__test_with_reference_bin('option_chunks/netx90_options.xml', 'option_chunks/netx90_options.bin', 'NETX90', None, None)

    def test_partial_images_full(self):
        self.__test_with_reference_bin('partial_images/full.xml', 'partial_images/full.bin', 'NETX90_MPW', None, None)

    def test_partial_images_no_header_no_end(self):
        self.__test_with_reference_bin('partial_images/no_header_no_end.xml', 'partial_images/no_header_no_end.bin', 'NETX90_MPW', None, None)

    def test_partial_images_no_header_with_end(self):
        self.__test_with_reference_bin('partial_images/no_header_with_end.xml', 'partial_images/no_header_with_end.bin', 'NETX90_MPW', None, None)

    def test_partial_images_with_header_no_end(self):
        self.__test_with_reference_bin('partial_images/with_header_no_end.xml', 'partial_images/with_header_no_end.bin', 'NETX90_MPW', None, None)

    def test_regi_chunk(self):
        self.__test_with_reference_bin('regi/regi.xml', 'regi/regi.bin', 'NETX90', None, None)

    def test_secure_ca9sw_file(self):
        self.__test_with_reference_bin('secure/ca9sw_file.xml', 'secure/ca9sw_file.bin', 'NETX4000', None, ['secure/fake_ca9sw.bin'])

    def test_secure_cr7sw_file(self):
        self.__test_with_reference_bin('secure/cr7sw_file.xml', 'secure/cr7sw_file.bin', 'NETX4000', None, ['secure/fake_cr7sw.bin'])

    def test_secure_license_cert_file(self):
        self.__test_with_reference_bin('secure/license_cert_file.xml', 'secure/license_cert_file.bin', 'NETX4000', None, ['secure/fake_license_cert.bin'])

    def test_secure_root_cert_file(self):
        self.__test_with_reference_bin('secure/root_cert_file.xml', 'secure/root_cert_file.bin', 'NETX4000', None, ['secure/fake_root_cert.bin'])



#    special test for a root certificate. It requires files, which are not part of the repository 
#    see commit 
#        Revision: 9238cfd7f7c4fafac3ddb6354b416bfdba6be6a1
#        Author: Christoph Thelen <doc_bacardi@users.sourceforge.net>
#        Date: 26.10.2017 16:13:02
#        Message:
#        Add deactivated root_cert test.
#        
#        ----
#        Modified: mbs
#        Modified: tests/tests.py
#        
#        
#    def test_secure_root_cert(self):
#        self.__test_with_reference_bin('secure/root_cert.xml', 'secure/root_cert.bin', 'NETX90_MPW', ['--keyrom', 'keyrom.xml', '--openssl-options=-rand', '--openssl-options=random.bin'], ['secure/demo_key_public.der', 'secure/keyrom.xml', 'secure/random.bin'])

    def test_skip_absolute(self):
        self.__test_with_reference_bin('skip/absolute.xml', 'skip/absolute.bin', 'NETX90_MPW', None, None)

    def test_skip_absolute_parameter(self):
        self.__test_with_reference_bin('skip/absolute_parameter.xml', 'skip/absolute_parameter.bin', 'NETX90', ['--define', 'skipUntil=0x1000'], None)

    def test_skip_absolute_file_bin(self):
        self.__test_with_reference_bin('skip/absolute_file_bin.xml', 'skip/absolute_file_bin.bin', 'NETX90_MPW', None, ['skip/fill_data.bin'])

    def test_skip_absolute_file_elf(self):
        self.__test_with_reference_bin('skip/absolute_file_elf.xml', 'skip/absolute_file_elf.bin', 'NETX90_MPW', ['--objcopy', '%%NETX90_OBJCOPY%%', '--objdump', '%%NETX90_OBJDUMP%%', '--readelf', '%%NETX90_READELF%%', '--alias', 'FillData=%%ELF_NETX4000_SKIP%%'], None)

    def test_skip_absolute_file_elf_sect(self):
        self.__test_with_reference_bin('skip/absolute_file_elf_sect.xml', 'skip/absolute_file_elf_sect.bin', 'NETX90_MPW', ['--objcopy', '%%NETX90_OBJCOPY%%', '--objdump', '%%NETX90_OBJDUMP%%', '--readelf', '%%NETX90_READELF%%', '--alias', 'FillData=%%ELF_NETX4000_SKIPSECT%%'], None)

    def test_skip_absolute_with_offset(self):
        self.__test_with_reference_bin('skip/absolute_with_offset.xml', 'skip/absolute_with_offset.bin', 'NETX90_MPW', None, None)

    def test_skip_file(self):
        self.__test_with_reference_bin('skip/file.xml', 'skip/file.bin', 'NETX90_MPW', None, ['skip/file.bin'])

    def test_skip_file_alias(self):
        self.__test_with_reference_bin('skip/file_alias.xml', 'skip/file_alias.bin', 'NETX90', ['--alias', 'FillData=fill_data.bin'], ['skip/fill_data.bin'])

    def test_skip_file_alias_multi(self):
        self.__test_with_reference_bin('skip/file_alias_multi.xml', 'skip/file_alias_multi.bin', 'NETX90', ['--alias', 'FillData0=fill_data.bin', '--alias', 'FillData1=fill_data2.bin'], ['skip/fill_data.bin', 'skip/fill_data2.bin'])

    def test_skip_file_with_fill(self):
        self.__test_with_reference_bin('skip/file_with_fill.xml', 'skip/file_with_fill.bin', 'NETX90_MPW', None, ['skip/fill_data.bin'])

    def test_skip_relative(self):
        self.__test_with_reference_bin('skip/relative.xml', 'skip/relative.bin', 'NETX90_MPW', None, None)

    def test_skip_relative_file(self):
        self.__test_with_reference_bin('skip/relative_file.xml', 'skip/relative_file.bin', 'NETX90_MPW', None, ['skip/fill_data.bin'])

    def test_skip_incomplete_absolute(self):
        self.__test_with_reference_bin('skip_incomplete/absolute.xml', 'skip_incomplete/absolute.bin', 'NETX90_MPW', None, None)

    def test_skip_incomplete_absolute_file(self):
        self.__test_with_reference_bin('skip_incomplete/absolute_file.xml', 'skip_incomplete/absolute_file.bin', 'NETX90_MPW', None, ['skip_incomplete/fill_data.bin'])

    def test_skip_incomplete_absolute_with_offset(self):
        self.__test_with_reference_bin('skip_incomplete/absolute_with_offset.xml', 'skip_incomplete/absolute_with_offset.bin', 'NETX90_MPW', None, None)

    def test_skip_incomplete_file(self):
        self.__test_with_reference_bin('skip_incomplete/file.xml', 'skip_incomplete/file.bin', 'NETX90_MPW', None, ['skip_incomplete/file.bin'])

    def test_skip_incomplete_file_with_fill(self):
        self.__test_with_reference_bin('skip_incomplete/file_with_fill.xml', 'skip_incomplete/file_with_fill.bin', 'NETX90_MPW', None, ['skip_incomplete/fill_data.bin'])

    def test_skip_incomplete_relative(self):
        self.__test_with_reference_bin('skip_incomplete/relative.xml', 'skip_incomplete/relative.bin', 'NETX90_MPW', None, None)

    def test_skip_incomplete_relative_file(self):
        self.__test_with_reference_bin('skip_incomplete/relative_file.xml', 'skip_incomplete/relative_file.bin', 'NETX90_MPW', None, ['skip_incomplete/fill_data.bin'])

    def test_snippets_cdata(self):
        self.__test_with_reference_bin('snippets/cdata.xml', 'snippets/cdata.bin', 'NETX90_MPW', None, ['snippets/sniplib/cdata-1.0.0.xml'])

    def test_snippets_custom_location(self):
        self.__test_with_reference_bin('snippets/custom_location.xml', 'snippets/custom_location.bin', 'NETX90_MPW', ['--sniplib', 'custom_sniplib'], ['snippets/custom_sniplib/custom-1.0.0.xml'])

    def test_snippets_default_location(self):
        self.__test_with_reference_bin('snippets/default_location.xml', 'snippets/default_location.bin', 'NETX90_MPW', None, ['snippets/sniplib/default-1.0.0.xml'])

    def test_snippets_precedence(self):
        self.__test_with_reference_bin('snippets/precedence.xml', 'snippets/precedence.bin', 'NETX90_MPW', ['--sniplib', 'custom_sniplib', '--sniplib', 'sniplib'], ['snippets/sniplib/precedence-1.0.0.xml', 'snippets/custom_sniplib/precedence-1.0.0.xml'])

    def test_text_NETX90_INTFLASH(self):
        self.__test_with_reference_bin('text/text_NETX90_INTFLASH.xml', 'text/text.bin', 'NETX90', None, None)
    def test_text_NETX4000_INTFLASH(self):
        self.__test_with_reference_bin('text/text_NETX4000_4100_SQIROM0.xml', 'text/text.bin', 'NETX4000', None, None)
    def test_text_NETX4100_INTFLASH(self):
        self.__test_with_reference_bin('text/text_NETX4000_4100_SQIROM0.xml', 'text/text.bin', 'NETX4100', None, None)
        
    def test_xip_concat_NETX90_INTFLASH(self):
        self.__test_with_reference_bin('xip/xip_concat_NETX90_INTFLASH.xml',       'xip/xip_concat.bin', 'NETX90', None, None)
    def test_xip_concat_NETX4000_SQIROM0(self):
        self.__test_with_reference_bin('xip/xip_concat_NETX4000_4100_SQIROM0.xml', 'xip/xip_concat.bin', 'NETX4000', None, None)
    def test_xip_concat_NETX4100_SQIROM0(self):
        self.__test_with_reference_bin('xip/xip_concat_NETX4000_4100_SQIROM0.xml', 'xip/xip_concat.bin', 'NETX4100', None, None)
        
    def test_xip_file_alias_NETX4000_SQIROM0(self):
        self.__test_with_reference_bin('xip/xip_file_alias_NETX4000_SQIROM0.xml', 'xip/xip_file_alias_NETX4000_SQIROM0.bin', 'NETX4000', ['--alias', 'FillData=fill_data.bin'], ['xip/fill_data.bin'])

    def test_xip_hex_NETX4000_RELAXED_SQIROM0(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX4000_RELAXED_SQIROM0.xml', 'xip/xip_hex_NETX4000_RELAXED_SQIROM0.bin', 'NETX4000_RELAXED', None, None)

    def test_xip_hex_NETX4000_RELAXED_SQIROM1(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX4000_RELAXED_SQIROM1.xml', 'xip/xip_hex_NETX4000_RELAXED_SQIROM1.bin', 'NETX4000_RELAXED', None, None)

    def test_xip_hex_NETX4000_SQIROM0(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX4000_SQIROM0.xml', 'xip/xip_hex_NETX4000_SQIROM0.bin', 'NETX4000', None, None)

    def test_xip_hex_NETX4000_SQIROM1(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX4000_SQIROM1.xml', 'xip/xip_hex_NETX4000_SQIROM1.bin', 'NETX4000', None, None)

    def test_xip_hex_NETX4100_SQIROM0(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX4100_SQIROM0.xml', 'xip/xip_hex_NETX4100_SQIROM0.bin', 'NETX4100', None, None)

    def test_xip_hex_NETX4100_SQIROM1(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX4100_SQIROM1.xml', 'xip/xip_hex_NETX4100_SQIROM1.bin', 'NETX4100', None, None)

    def test_xip_hex_NETX90_MPW_INTFLASH(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX90_MPW_INTFLASH.xml', 'xip/xip_hex_NETX90_MPW_INTFLASH.bin', 'NETX90_MPW', None, None)

    def test_xip_hex_NETX90_MPW_SQIROM(self):
        self.__test_with_reference_bin('xip/xip_hex_NETX90_MPW_SQIROM.xml', 'xip/xip_hex_NETX90_MPW_SQIROM.bin', 'NETX90_MPW', None, None)

#    def test_hash_table_fwk_NETX90_B(self):
#        self.__test_with_reference_bin(
#            'secure_boot/NXHX90-JTAG_COM/hash_table_fwk.xml',
#            'secure_boot/NXHX90-JTAG_COM/hash_table_fwk.bin',
#            'NETX90B',
#            ['--keyrom', 'keyrom.xml',
#             '--openssl-exe', <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/NXHX90-JTAG_COM/keyrom.xml'])
#
#    def test_hash_table_rk_NETX90_B(self):
#        self.__test_with_reference_bin(
#            'secure_boot/NXHX90-JTAG_COM/hash_table_rk.xml',
#            'secure_boot/NXHX90-JTAG_COM/hash_table_rk.bin',
#            'NETX90B',
#            ['--keyrom', 'keyrom.xml',
#             '--openssl-exe', <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/NXHX90-JTAG_COM/keyrom.xml'])
#
#    def test_asig_NETX90_B(self):
#        self.__test_netx90_appimg_with_reference_bin(
#            'secure_boot/NXHX90-JTAG_APP/asig.xml',
#            ['secure_boot/NXHX90-JTAG_APP/asig.nai',
#             'secure_boot/NXHX90-JTAG_APP/asig.nae'],
#            ['-n', 'netx90_rev1' ,
#             '--keyrom' , 'keyrom.xml',
#             '-c', '%%NETX90_OBJCOPY%%', '-d', '%%NETX90_OBJDUMP%%', '-r', '%%NETX90_READELF%%',
#             '-A', 'tElf=%%ELF_NETX90_APP_BLINKI_IFLASH_SDRAM%%',
#             '--openssl-exe' , <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/NXHX90-JTAG_APP/keyrom.xml'])
#
#    def test_usip_app_set_pk_NETX90_B(self):
#        self.__test_with_reference_bin(
#            'secure_boot/UpdateSecureInfoPage/usip_app_set_pk.xml',
#            'secure_boot/UpdateSecureInfoPage/usip_app_set_pk.bin',
#            'NETX90B',
#            ['--keyrom' , 'keyrom.xml',
#             '--openssl-exe', <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/UpdateSecureInfoPage/keyrom.xml'])
#
#    def test_usip_com_set_sbo_NETX90_B(self):
#        self.__test_with_reference_bin(
#            'secure_boot/UpdateSecureInfoPage/usip_com_set_sbo.xml',
#            'secure_boot/UpdateSecureInfoPage/usip_com_set_sbo.bin',
#            'NETX90B',
#            ['--keyrom' , 'keyrom.xml',
#             '--openssl-exe', <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/UpdateSecureInfoPage/keyrom.xml'])

    def test_data_hex_public(self):
        self.__test_with_reference_bin_public('data/data_hex.xml', 'data/data_hex.bin', 'netx90_mpw', None, None)

    def test_regi_chunk_public(self):
        self.__test_with_reference_bin_public('regi/regi.xml', 'regi/regi.bin', 'netx90_rev0', None, None)

    def test_firewall_chunk_public(self):
        self.__test_with_reference_bin_public(
            'firewall/firewall.xml',
            'firewall/firewall.bin',
            'netx90',
            ['--netx-type', 'NETX90'],
            None,
            strExpectedError = "hboot_image_compiler: error: argument -n/--netx-type: not allowed with argument --netx-type-public"
        )

    def test_skip_absolute_parameter_public(self):
        self.__test_with_reference_bin_public(
            'skip/absolute_parameter.xml',
            'skip/absolute_parameter.bin',
            None,
            ['--define', 'skipUntil=0x1000'],
            None,
            strExpectedError = "hboot_image_compiler: error: one of the arguments -n/--netx-type --netx-type-public is required"
        )
		
    def test_text_NETX4000_INTFLASH_public(self):
        self.__test_with_reference_bin_public('text/text_NETX4000_4100_SQIROM0.xml', 'text/text.bin', 'NETX4000', None, None)

    def test_text_NETX4100_INTFLASH_public(self):
        self.__test_with_reference_bin_public('text/text_NETX4000_4100_SQIROM0.xml', 'text/text.bin', 'NETX4100', None, None)
		
    def test_xip_hex_NETX4000_RELAXED_SQIROM0_public(self):
        self.__test_with_reference_bin_public('xip/xip_hex_NETX4000_RELAXED_SQIROM0.xml', 'xip/xip_hex_NETX4000_RELAXED_SQIROM0.bin', 'NETX4000_RELAXED', None, None)
		
    def test_option_chunks_netx90B_options(self):
        self.__test_with_reference_bin('option_chunks/netx90b_options.xml', 'option_chunks/netx90b_options.bin', 'NETX90B', None, None)

    def test_option_chunks_netx90_rev1_options_public(self):
        self.__test_with_reference_bin_public('option_chunks/netx90b_options.xml', 'option_chunks/netx90b_options.bin', 'netx90_rev1', None, None)
		
    def test_option_chunks_netx90_options_public(self):
        self.__test_with_reference_bin_public('option_chunks/netx90b_options.xml', 'option_chunks/netx90b_options.bin', 'netx90', None, None)

#    def test_secure_netx4000_root_cert(self):
#        self.__test_with_reference_bin(
#            'secure_boot/NXHX4000-JTAG/ValidRootCertNewRegTemplate.xml',
#            'secure_boot/NXHX4000-JTAG/ValidRootCertNewRegTemplate.bin',
#            'NETX4000',
#            ['--keyrom' , 'Keys/keyrom.xml',
#             '-A', 'licensePublicKey=Keys/licensePublicKey.der', '-A', 'cr7PublicKey=Keys/cr7PublicKey.der', '-A', 'a9PublicKey=Keys/a9PublicKey.der',
#             '--openssl-exe', <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/NXHX4000-JTAG/Keys/keyrom.xml',
#             'secure_boot/NXHX4000-JTAG/Keys/a9PublicKey.der',
#             'secure_boot/NXHX4000-JTAG/Keys/cr7PublicKey.der',
#             'secure_boot/NXHX4000-JTAG/Keys/licensePublicKey.der'
#			])
#
#    def test_secure_netx4000_lic_cert(self):
#        self.__test_with_reference_bin(
#            'secure_boot/NXHX4000-JTAG/ValidLicenseCertNewRegTemplate.xml',
#            'secure_boot/NXHX4000-JTAG/ValidLicenseCertNewRegTemplate.bin',
#            'NETX4000',
#            ['-A', 'licensePrivatKey=Keys/licensePrivatKey.der',
#             '--openssl-exe', <your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/NXHX4000-JTAG/Keys/licensePrivatKey.der'])
#
#    def test_secure_netx4000_sw_cert(self):
#        self.__test_with_reference_bin(
#            'secure_boot/NXHX4000-JTAG/ValidSecureSwCr7A9Template.xml',
#            'secure_boot/NXHX4000-JTAG/ValidSecureSwCr7A9Template.bin',
#            'NETX4000',
#            ['-A', 'a9PrivatKey=Keys/a9PrivatKey.der', '-A', 'cr7PrivatKey=Keys/cr7PrivatKey.der',
#             '--openssl-exe', '<your openssl path>,
#             '--openssl-rand-off'],
#            ['secure_boot/NXHX4000-JTAG/Keys/a9PrivatKey.der',
#             'secure_boot/NXHX4000-JTAG/Keys/cr7PrivatKey.der'
#            ])

    # Check that each file with suffix .py contains the license header
    def test_License_Header(self):
        astrLicenseHeader =[
            '# ***************************************************************************',
            '# *   Copyright (C) 2019 by Hilscher GmbH                                   *',
            '# *   netXsupport@hilscher.com                                              *',
            '# *                                                                         *',
            '# *   This program is free software; you can redistribute it and/or modify  *',
            '# *   it under the terms of the GNU General Public License as published by  *',
            '# *   the Free Software Foundation; either version 2 of the License, or     *',
            '# *   (at your option) any later version.                                   *',
            '# *                                                                         *',
            '# *   This program is distributed in the hope that it will be useful,       *',
            '# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *',
            '# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *',
            '# *   GNU General Public License for more details.                          *',
            '# *                                                                         *',
            '# *   You should have received a copy of the GNU General Public License     *',
            '# *   along with this program; if not, write to the                         *',
            '# *   Free Software Foundation, Inc.,                                       *',
            '# *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *',
            '# ***************************************************************************',
            ]
            
        strLicenseHeader = ''.join(astrLicenseHeader)
        strLicenseLine = ''.join(strLicenseHeader.split())
        strRootDir = os.environ["HBOOT_DEPACK_FOLDER"]
        
        print("Checking files for GPL header: .py in" + strRootDir)
        
        fResult = True
        
        for strDir, astrSubdirs, astrFiles in os.walk(strRootDir):
            for strFile in astrFiles:
                strFilePath = os.path.join(strDir, strFile)
                strBasename, strExt = os.path.splitext(strFilePath)
                if strExt == ".py":
                    fd = open(strFilePath, "r")
                    strContents = fd.read()
                    fd.close()
                    
                    strContentsLine = ''.join(strContents.split())
                    if strContentsLine.find(strLicenseLine) > 0:
                        print("Has license header: " + strFilePath)
                    else:
                        print("No license header:  " + strFilePath)
                        fResult = False
    
        self.assertEqual(fResult, True)


if __name__ == '__main__':
    unittest.main()

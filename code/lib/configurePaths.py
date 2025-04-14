# configurePaths.py: Sets the paths to project folders.

# Preamble
import os

# Functions
def getProjectRoot():
    return os.getcwd().split(os.sep + 'code', 1)[0]

def getSubfolderPaths(cRoot):
    cCodePath = os.path.join(cRoot, 'code')
    cDataPath = os.path.join(cRoot, 'data')
    cRawDataPath = os.path.join(cDataPath, 'raw')
    cCleanDataPath = os.path.join(cDataPath, 'clean')
    cTempDataPath = os.path.join(cDataPath, 'temp')
    cOutputPath = os.path.join(cRoot, 'output')
    cTablesOutputPath = os.path.join(cOutputPath, 'tables')
    cFiguresOutputPath = os.path.join(cOutputPath, 'figures')
    return cCodePath, cRawDataPath, cCleanDataPath, cTempDataPath, cOutputPath, cTablesOutputPath, cFiguresOutputPath

def getFilePath(cFolder, fileName):
    return os.path.join(cFolder, fileName)
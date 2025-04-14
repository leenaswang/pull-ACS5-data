#Import libraries
import os
import lib.configurePaths as configurePaths
import glob
import pandas as pd
import multiprocessing

#cProjectRoot = configurePaths.getProjectRoot()
_, cRawDataPath, cCleanDataPath, _, _, _, _ = configurePaths.getSubfolderPaths(configurePaths.getProjectRoot())

#Dictionary
acs5Variables = {
    "B01002_001E": "fMedAge",
    "B19013_001E": "nMedHHIncome",
    "B25064_001E": "nMedGrossRent",
    "B08303_001E": "nCommutePop",
    "B23025_001E": "nPopEmployed16Plus"
}

#Extracts information (column names) from file and saves as a feather file (with relevant naming)
def readCSVsToFeather(rawCSVFolder, cleanCSVFolder, featherFileName, renamedVars):
    csv_files = glob.glob(os.path.join(rawCSVFolder, "*.csv"))  # Find all CSVs
    dataFrameList = []
    for file in csv_files:
        # Ensures state, county, tract, block_group codes remain strings
        #df = pd.read_csv(file, dtype={"STATE": str, "COUNTY": str, "TRACT": str, "BLOCK_GROUP": str})
        df = pd.read_csv(file)
        df = df.rename(columns=renamedVars)
        #Adding GEOID (11 and 12 digit) columns
        df['GEOID12'] = (
                df['STATE'].astype(str).str.zfill(2) +
                df['COUNTY'].astype(str).str.zfill(3) +
                df['TRACT'].astype(str).str.zfill(6) +
                df['BLOCK_GROUP'].astype(str).str.zfill(1)
        )
        df['GEOID11'] = (
                df['STATE'].astype(str).str.zfill(2) +
                df['COUNTY'].astype(str).str.zfill(3) +
                df['TRACT'].astype(str).str.zfill(6)
        )
        dataFrameList.append(df)
    panel_df = pd.concat(dataFrameList, ignore_index=True)
    panel_df.to_feather(configurePaths.getFilePath(cleanCSVFolder, featherFileName))

# Making sure the created feather file looks correct
def testing(cleanCSVFolder, featherFileName):
    # Read the Feather file
    featherPath = configurePaths.getFilePath(cleanCSVFolder, featherFileName)
    df = pd.read_feather(featherPath)
    testCSVPath = configurePaths.getFilePath(cleanCSVFolder, "test.csv")
    df.to_csv(testCSVPath, index=False)

def main():
    readCSVsToFeather(cRawDataPath, cCleanDataPath, "ACS5_panel.feather", acs5Variables)
    testing(cCleanDataPath, "ACS5_panel.feather")

#Execute
main()
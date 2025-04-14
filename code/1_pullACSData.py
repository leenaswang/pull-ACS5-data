#Import libraries
import multiprocessing
import censusdis.data as ced
import lib.configurePaths as configurePaths

#cProjectRoot = configurePaths.getProjectRoot()
_, cRawDataPath, _, _, _, _, _ = configurePaths.getSubfolderPaths(configurePaths.getProjectRoot())

#Constants
DATASET = "acs/acs5"
EMPLOYED_POP_16_PLUS = "B23025_001E"
MED_HOUSING_VALUE = "B25077_001E"
MED_AGE = "B01002_001E"
MED_HOUSEHOLD_INCOME = "B19013_001E"
MED_GROSS_RENT = "B25064_001E"
MEAN_COMMUTE = "B08303_001E"
VARIABLES = ["NAME", EMPLOYED_POP_16_PLUS, MED_AGE, MED_HOUSEHOLD_INCOME, MED_GROSS_RENT, MEAN_COMMUTE]

"""
Pulls ACS data for a given year, state, and county FIPS code and
saves the result as a CSV file in the raw data folder
"""

# Pulls data frame with year, variables, state, and county from input, up to year 2019
def pullACSDataframe(year, stateFIPS, countyFIPS):
    try:
        print(f"Ready to download")
        df_block_group = ced.download(DATASET,
                                      year,
                                      VARIABLES,
                                      state = stateFIPS,
                                      county = countyFIPS,
                                      block_group = "*",
                                      )
        df_block_group["YEAR"] = year
        # Converts to CSV and saves with success message
        print(f"Ready to save to CSV")
        df_block_group.to_csv(configurePaths.getFilePath(cRawDataPath, f"{year}state{stateFIPS}county{countyFIPS}ACS5.csv"))
        print(f"{year} ACS data successfully saved to raw folder")
    except ced.CensusApiException as e:
        print(e)

# Saves inputs for state/county FIPS codes
def getUserInputs():
    # Takes year, state & county FIPS codes as inputs
    cYear = input("Enter the starting year you would like to pull: ")
    try:
        year = int(cYear)
        if year < 2013 or year > 2019:
            year = 2013
            print("Invalid year: input should stay within 2013 to 2019. Year set to 2013")
    except:
        print("Invalid year string: input should stay within 2013 to 2019. Year set to 2013")
        year = 2013  #The first year with valid data
    stateFIPS = input("Enter state FIPS code (e.g. 42 for PA): ")
    countyFIPS = input("Enter county FIPS code (e.g. 101 for Philadelphia County): ")
    return year, stateFIPS, countyFIPS

def loopPullACSData(year, stateFIPS, countyFIPS):
    processes = []
    while year <= 2019:
        process = multiprocessing.Process(target=pullACSDataframe, args=(year, stateFIPS, countyFIPS,))  # Create a process
        # process = multiprocessing.Process(target=worker, args=(i,))  # Create a process
        year = year + 1
        processes.append(process)
        process.start()
    for process in processes:
       process.join()  # Wait for all processes to finish

def main():
    userYear, userStateFIPS, userCountyFIPS = getUserInputs()
    loopPullACSData(userYear, userStateFIPS, userCountyFIPS)

#Execute
if __name__ == "__main__":
    main()

## pull-ACS5-data

[Work in progress].

pull-ACS5-data is a project that pulls American Census Survey 5-year block group data from a specified state, county, and time frame.

## code

### 1_pullACSData.py

Pulls ACS data for a given year, state, and county FIPS code and saves the result as a .csv file in the raw data folder.

Uses censusdis package to pull a dataframe from the ACS website, up to 2019. Utilizes multiprocessing to speed up the process and collate all years. 

### 2_appendCSVToFeather.py

Extracts each .csv file in the raw data folder and appends each .csv to create a large panel, which is then saved as a .feather file in the clean data folder.

Additionally creates a "test" .csv file of the panel to check for errors.

### 3_dataAnalysis.py



##API

Request a U.S. Census Data API key [here] (https://api.census.gov/data/key_signup.html). 

Find the key (a string of numbers and letters in your email) and create a directory named ".censusdis" in your home directory. Then create a .txt file "api_key.txt". Paste your API key into this file. From now on, all censusdis calls will use this API Key.

Check out the [censusdis documentation] (https://censusdis.readthedocs.io/en/latest/intro.html#census-api-key-optional-initially) for more information.

## Known Issues

1. Desired variables are hardcoded.
2. Only data from 10 year periods (2010-2019, for example) should be aggregated.
3. Maps have aggressive borders/background imagery that get in the way of visualization, especially when data from census block groups.

## License

[MIT](https://choosealicense.com/licenses/mit/)

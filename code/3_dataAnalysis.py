#Import libraries
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import lib.configurePaths as configurePaths
import matplotlib.pyplot as plt
import seaborn as sns

#cProjectRoot = configurePaths.getProjectRoot()
_, _, cCleanDataPath, _, _, cTablesOutputPath, cFiguresOutputPath = configurePaths.getSubfolderPaths(configurePaths.getProjectRoot())

#Variables
VARIABLES =["fMedAge", "nMedHHIncome", "nMedGrossRent", "nCommutePop", "nPopEmployed16Plus"]

def mergeFilesViaGEOID(cleanCSVFolder, ACS5Panel, TLShapeFile):
    # Load the shapefile and Feather file from the clean data folder
    ACS5FeatherPath = configurePaths.getFilePath(cleanCSVFolder, ACS5Panel)
    SHPPath = configurePaths.getFilePath(cleanCSVFolder, TLShapeFile)
    ACS5df = pd.read_feather(ACS5FeatherPath)
    SHPgdf = gpd.read_file(SHPPath)

    # Adding GEOID (11 and 12 digit) columns
    SHPgdf['GEOID12'] = (
        SHPgdf['STATEFP10'].astype(str).str.zfill(2) +
        SHPgdf['COUNTYFP10'].astype(str).str.zfill(3) +
        SHPgdf['TRACTCE10'].astype(str).str.zfill(6) +
        SHPgdf['BLKGRPCE10'].astype(str).str.zfill(1)
    )
    SHPgdf['GEOID11'] = (
        SHPgdf['STATEFP10'].astype(str).str.zfill(2) +
        SHPgdf['COUNTYFP10'].astype(str).str.zfill(3) +
        SHPgdf['TRACTCE10'].astype(str).str.zfill(6)
    )
    mergedGDF = SHPgdf.merge(ACS5df,
                           on="GEOID11",
                           how="inner")
    mergedGDF['fMonthlyIncome'] = mergedGDF["nMedHHIncome"] / 12
    mergedGDF['fRentToIncomeRatio'] = mergedGDF["nMedGrossRent"] / mergedGDF['fMonthlyIncome']
    mergedGDF["fPercentCommute"] = mergedGDF["nCommutePop"] / mergedGDF["nPopEmployed16Plus"]
    return mergedGDF

def correlationTable(dataframe, variables, tableOutputFolder, outputFileName, colNames=None):
    # Select a subset of the df with desired variables
    dataSubset = dataframe[variables]
    #Create correlation matrix and keep lower triangle
    corrMatrix = dataSubset.corr()
    maskedCorrMatrix = corrMatrix.where(np.tril(np.ones(corrMatrix.shape), k=-1).astype(bool))
    # Replace NaN values with "-"
    maskedCorrMatrix = maskedCorrMatrix.fillna("-")
    if colNames and len(colNames) == len(variables):
        maskedCorrMatrix.columns = colNames
        maskedCorrMatrix.index = colNames
    latexCode = maskedCorrMatrix.to_latex(float_format="%.2f")
    outputPath = configurePaths.getFilePath(tableOutputFolder, outputFileName)
    with open(outputPath, 'w') as f:
        f.write(latexCode)

def monthlyRentToIncomeRatio(dataframe, rentVar, incomeVar, year, tableOutputFolder, outputFileName):
    dataframe['Rent to Income (Monthly) Ratio'] = dataframe[rentVar] / dataframe['nMonthlyIncome']
    # Calculate average rent to income ratio and standard deviation per year
    avgRentToIncomeRatioYear = dataframe.groupby('YEAR')['Rent to Income (Monthly) Ratio'].mean()
    stdRentToIncomeRatioYear = dataframe.groupby('YEAR')['Rent to Income (Monthly) Ratio'].std()
    # Build the LaTeX table
    avgRatioTable = '\\begin{table}[ht]\n\\centering\n'
    avgRatioTable += '\\begin{tabular}{|c|c|c|}\n\\hline\n'
    avgRatioTable += 'Year & Average Rent/Income Ratio & Standard Deviation \\\\ \\hline\n'
    # Loop through the years 2013 to 2019 to get the average and standard deviation for each
    for year in range(2013, 2020):
        # Format the year and the avg ratio in the table row
        avg_ratio = avgRentToIncomeRatioYear.get(year, 'N/A')  # In case there's no data for a year
        std_dev = stdRentToIncomeRatioYear.get(year, 'N/A')  # Handle missing data
        avgRatioTable += f'{year} & {avg_ratio:.3f} & {std_dev:.3f} \\\\ \\hline\n'
    avgRatioTable += '\\end{tabular}\n\\caption{Average Rent to Income Ratio in Philadelphia County from 2013 to 2019}\n\\end{table}'
    outputPath = configurePaths.getFilePath(tableOutputFolder, outputFileName)
    with open(outputPath, 'w') as f:
        f.write(avgRatioTable)

def annualAvgHHIncomeTable(dataframe, incomeVar, year, tableOutputFolder, outputFileName):
    # Calculate average and standard deviation of income
    avgAnnualHHIncome = dataframe.groupby('YEAR')[incomeVar].mean()
    stdAnnualHHIncome = dataframe.groupby('YEAR')[incomeVar].std()
    # Build the LaTeX table
    avgIncomeTable = '\\begin{table}[ht]\n\\centering\n'
    avgIncomeTable += '\\begin{tabular}{|c|c|c|}\n\\hline\n'
    avgIncomeTable += 'Year & Average Annual Household Income & Standard Deviation \\\\ \\hline\n'
    # Loop through the years 2013 to 2019 to get the average and standard deviation for each
    for year in range(2013, 2020):
        # Format the year and the avg ratio in the table row
        avg_income = avgAnnualHHIncome.get(year, 'N/A')  # Handle missing data
        std_dev = stdAnnualHHIncome.get(year, 'N/A')  # Handle missing data
        avgIncomeTable += f'{year} & {avg_income:.3f} & {std_dev:.3f} \\\\ \\hline\n'
    avgIncomeTable += '\\end{tabular}\n\\caption{Average Household Income in Philadelphia County from 2013 to 2019}\n\\end{table}'
    outputPath = configurePaths.getFilePath(tableOutputFolder, outputFileName)
    with open(outputPath, 'w') as f:
        f.write(avgIncomeTable)

def mappingVarTracts(dataframe, variable, title, legend, figuresOutputFolder, outputFileName):
    # Aggregate data by tract and year
    tractAvg = dataframe.groupby(['GEOID11', 'YEAR']).agg({variable: 'mean'}).reset_index()
    # Set up animated map
    fig, ax = plt.subplots(figsize=(10, 10))
    dataframe.plot(column=variable, cmap='viridis', legend=True, ax=ax,
                    legend_kwds={'label': legend})
    # Set the title
    ax.set_title(title)
    outputPath = configurePaths.getFilePath(figuresOutputFolder, outputFileName)
    plt.savefig(outputPath, dpi=300, bbox_inches='tight', format='png')
    print(f"Map saved in {outputPath}")

def mappingVarTractsByYear(dataframe, variable, title, legend, figuresOutputFolder):
    sortedUniqueYears = sorted(dataframe['YEAR'].unique())
    minVarValue = 0
    maxVarValue = dataframe[variable].max()
    print(sortedUniqueYears)
    for eachYear in sortedUniqueYears:
        filteredDFPerYear = dataframe[dataframe['YEAR'] == eachYear]
        fig, ax = plt.subplots(figsize=(10, 10))
        filteredDFPerYear.plot(column = variable, cmap='viridis', legend=True, ax=ax,
                               vmin = minVarValue, vmax = maxVarValue, legend_kwds={'label': legend})
        ax.set_title(str(eachYear) + " " + title)
        outputPath = configurePaths.getFilePath(figuresOutputFolder, f"{eachYear}for{variable}CensusTract.png")
        plt.savefig(outputPath, dpi=300, bbox_inches='tight', format='png')
        print(f"Map saved in {outputPath}")

def plottingVarBlockGroupsByYear(dataframe, xVar, yVar, title, xlabel, ylabel, figuresOutputFolder, xMax, yMax, prefix):
    sortedUniqueYears = sorted(dataframe['YEAR'].unique())
    print(sortedUniqueYears)
    for eachYear in sortedUniqueYears:
        filteredDFPerYear = dataframe[dataframe['YEAR'] == eachYear]
        plt.figure(figsize=(10, 6))
        # limiting x and y axes to keep consistent when animating
        if xMax is not None:
            plt.xlim(0, xMax)
        if yMax is not None:
            plt.ylim(0, yMax)
        sns.scatterplot(
            data=  filteredDFPerYear,
            x = xVar,
            y = yVar,
            alpha = 0.4,  # transparency
            s = 10        # point size
        )
        plt.title(f"{eachYear} - {title}")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        outputPath = configurePaths.getFilePath(figuresOutputFolder, f"{prefix}{xVar}{yVar}Scatter{eachYear}.png")
        plt.savefig(outputPath, dpi=300, bbox_inches='tight', format='png')
        plt.close()
        print(f"Scatter plot saved in {outputPath}")

def plotMap(numeratorVar, denominatorVar, dataframe, year, figuresOutputFolder):
    # Filter GeoDataFrame for the selected year
    dataframe_year = dataframe[dataframe['YEAR'] == year].copy()

    # Calculate the ratio column
    ratioCol = f"{numeratorVar}_to_{denominatorVar}_Ratio"
    dataframe_year[ratioCol] = dataframe_year[numeratorVar] / dataframe_year[denominatorVar]

    # Group by GEOID11 to get the mean ratio per tract
    dataframe_GEOID11avg = dataframe_year.groupby('GEOID11')[[ratioCol]].mean().reset_index()

    # Merge the average ratios back with the original GeoDataFrame geometry
    merged_gdf = dataframe[['GEOID11', 'geometry']].drop_duplicates().merge(dataframe_GEOID11avg, on='GEOID11')

    # Plot the map
    ax = merged_gdf.plot(column=ratioCol,
                         figsize=(10, 10),
                         legend=True,
                         legend_kwds={"label": f"Ratio of {numeratorVar}/{denominatorVar} in {year}",
                                      "orientation": "horizontal"},
                         cmap='viridis',
                         linewidth=0.5,
                         vmin = 0,
                         vmax = 0.3)  # Lock the scale from 0 to 1

    ax.set_axis_off()

    # Save the figure
    outputFilePath = configurePaths.getFilePath(figuresOutputFolder,
                                                f"ratio_{numeratorVar}to{denominatorVar}_{year}.png")
    plt.savefig(outputFilePath)
    plt.close()
    print(f"Figure saved to {outputFilePath}")

def main():
    mergedGDF = mergeFilesViaGEOID(cCleanDataPath, "ACS5_panel.feather",
                                   "tl_2019_42101_faces.zip")
    # mappingVarTractsByYear(mergedGDF, "nMedHHIncome", "Average Household Income in Census Tracts",
    #                  "Dollars", cFiguresOutputPath)
    # mappingVarTractsByYear(mergedGDF, "fMedAge", "Average Age in Census Tracts",
    #                        "Years", cFiguresOutputPath)
    # mappingVarTractsByYear(mergedGDF, "nMedGrossRent", "Average Gross Rent in Census Tracts",
    #                        "Dollars", cFiguresOutputPath)
    # correlationTable(mergedGDF,
    #                   variables,
    #                   cTablesOutputPath,
    #                   "corrTable.tex",
    #                   ['Median Age', 'Median Household Income', 'Median Gross Rent'])
    # monthlyRentToIncomeRatio(mergedGDF, 'nMedGrossRent','nMedHHIncome',
    #                          'YEAR', cTablesOutputPath, "RentIncomeRatio.tex")
    # annualAvgHHIncomeTable(mergedGDF, "nMedHHIncome", "YEAR", cTablesOutputPath, "avgHHIncome.tex")
    # weird = mergedGDF[mergedGDF['nRentToIncomeRatio'] > 1]
    # print(weird.sort_values(by='nRentToIncomeRatio', ascending=False))
    # output_csv_path = configurePaths.getFilePath(cTablesOutputPath, "weird_rent_income_ratios.csv")
    # weird.to_csv(output_csv_path, index=False)
    plottingVarBlockGroupsByYear(mergedGDF, 'nMedHHIncome', 'fRentToIncomeRatio',
                                 'Monthly Rent/Income Ratio and Median Household Income in Philadelphia County',
                                 "Monthly Rent/Income Ratio", "Median Annual Household Income",
                                 cFiguresOutputPath, None, None,"messy")
    plottingVarBlockGroupsByYear(mergedGDF, 'nMedHHIncome', 'fRentToIncomeRatio',
                                 'Monthly Rent/Income Ratio and Median Household Income in Philadelphia County',
                                 "Median Annual Household Income", "Monthly Rent/Income Ratio",
                                 cFiguresOutputPath, 180000, 1,"clean")
    plottingVarBlockGroupsByYear(mergedGDF, 'nMedHHIncome', 'fPercentCommute',
                                 "Percent of Workers Who Commute and Median Household Income",
                                 "Median Annual Household Income", "Percent of Workers Who Commute",
                                 cFiguresOutputPath, 180000, 1,"clean")

#Execute
main()


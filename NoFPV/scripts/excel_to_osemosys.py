#!/usr/bin/env python
# coding: utf-8
"""
Extract data from Excel spreadsheets (.xls and .xlsx)
Import the csv file that I want as an output, need to convert the xls format to csv format
To create the csv outputs (per sheet) in a folder called CSV files
"""
import xlrd
import csv
import os
import sys
import pandas as pd


def main(input_workbook, output_file):
    """Read the xlsx file
    """
    scenario = input_workbook[11:-5]
    csv_from_excel(input_workbook, scenario, output_file)


def csv_from_excel(input_workbook, scenario, output_file):
    """Read the workbook and
    """
    xl = pd.ExcelFile(input_workbook)
    sheetNames = xl.sheet_names
    
    # workBook = xlrd.open_workbook(os.path.join(input_workbook))
    # sheetNames = workBook.sheet_names()  # I read all the sheets in the xlsx file
    # I modify the names of the sheets since some do not match with the actual ones
    modifiedSheetNames = modifyNames(sheetNames)
    
    os.makedirs(f"CSVFiles_{scenario}", exist_ok=True)  # creates the csv folder
    
    # Create all the csv files in a new folder called CSVFiles
    for i in range(len(sheetNames)):
        df = pd.read_excel(input_workbook, sheet_name = sheetNames[i], header=None)

        # Open the sheet name in the xlsx file and write it in csv format
        with open(f'CSVFiles_{scenario}/' + modifiedSheetNames[i] + '.csv', 'w', newline='') as your_csv_file:
            wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

            # for rownum in range(sh.nrows):  # reads each row in the csv file
            #     if (all(isinstance(n, float) for n in sh.row_values(rownum))):
            #         # function to convert all float numbers to integers....need to check it!!
            #         wr.writerow(list(map(int, sh.row_values(rownum))))
            #     else:
            #         wr.writerow(sh.row_values(rownum))
            
            for rownum in range(len(df)):  # reads each row in the csv file
                if (all(isinstance(n, float) for n in df.loc[rownum,:].values)):
                    # function to convert all float numbers to integers....need to check it!!
                    wr.writerow(list(map(int, df.loc[rownum,:].values)))
                else:
                    wr.writerow(df.loc[rownum,:].values)

    # I create a txt file - string that contains the csv files
    fileOutput = parseCSVFilesAndConvert(scenario, modifiedSheetNames)
    with open(output_file, "w") as text_file:
        text_file.write(fileOutput)
        text_file.write("end;\n")

    # workBook.release_resources()  # release the workbook-resources
    # del workBook


# for loop pou trexei ola ta sheet name kai paragei to format se csv
def parseCSVFilesAndConvert(scenario, sheetNames):
    result = ''
    for i in range(len(sheetNames)):
        # 8 #all the     parameters thad do not have variables
        if (sheetNames[i] in ['STORAGE', 'EMISSION', 'MODE_OF_OPERATION',
                              'REGION', 'FUEL', 'TIMESLICE', 'TECHNOLOGY', 'TECHS_HYD',
                              'TECHS_FPV', 'YEAR']):
            result += 'set ' + sheetNames[i] + ' := '
            with open(f'CSVFiles_{scenario}/' + sheetNames[i] + '.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    result += " ".join(row) + " "
                result += ";\n"
        # 24 #all the parameters     that have one variable
        elif (sheetNames[i] in ['AccumulatedAnnualDemand', 'CapacityOfOneTechnologyUnit','CapitalCost',
                                'EmissionsPenalty','FixedCost', 'ResidualCapacity',
                                'SpecifiedAnnualDemand',
                                'TotalAnnualMinCapacity',
                                'TotalAnnualMinCapacityInvestment',
                                'TotalTechnologyAnnualActivityLowerLimit']):
            result += 'param ' + sheetNames[i] + ' default 0 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(scenario, sheetNames[i])
        # 24 #all the parameters that have one variable
        elif (sheetNames[i] in ['TotalAnnualMaxCapacityInvestment']):
            result += 'param ' + sheetNames[i] + ' default 99999 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(scenario, sheetNames[i])
        elif (sheetNames[i] in ['AvailabilityFactor']):
            result += 'param ' + sheetNames[i] + ' default 1 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(scenario, sheetNames[i])
        elif (sheetNames[i] in ['TotalAnnualMaxCapacity',
                                'TotalTechnologyAnnualActivityUpperLimit']):
            result += 'param ' + sheetNames[i] + ' default 9999999 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(scenario, sheetNames[i])
        elif (sheetNames[i] in ['AnnualEmissionLimit']):
            result += 'param ' + sheetNames[i] + ' default 99999 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(scenario, sheetNames[i])
        elif (sheetNames[i] in ['YearSplit']):
            result += 'param ' + sheetNames[i] + ' default 0 :\n'
            result += insert_table(scenario, sheetNames[i])
        elif (sheetNames[i] in ['REMinProductionTarget',
                                'RETagFuel', 'RETagTechnology',
                                'ReserveMargin', 'ReserveMarginTagFuel',
                                'ReserveMarginTagTechnology', 'TradeRoute']):
            result += 'param ' + sheetNames[i] + ' default 0 := ;\n'
        # 3 #all the parameters that have 2 variables
        elif (sheetNames[i] in ['SpecifiedDemandProfile']):
            result += 'param ' + sheetNames[i] + ' default 0 := \n'
            result += insert_two_variables(scenario, sheetNames, i)
        # 3 #all the parameters that have 2 variables
        elif (sheetNames[i] in ['VariableCost']):
            result += 'param ' + sheetNames[i] + ' default 9999999 := \n'
            result += insert_two_variables(scenario, sheetNames, i)
        # 3 #all the parameters that have 2 variables
        elif (sheetNames[i] in ['CapacityFactor']):
            result += 'param ' + sheetNames[i] + ' default 1 := \n'
            result += insert_two_variables(scenario, sheetNames, i)
        # 4 #all the parameters that have 3     variables
        elif (sheetNames[i] in ['EmissionActivityRatio', 'InputActivityRatio',
                                'OutputActivityRatio']):
            result += 'param ' + sheetNames[i] + ' default 0 := \n'
            with open(f'CSVFiles_{scenario}/' + sheetNames[i] + '.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                newRow = next(reader)
                newRow.pop(0)
                newRow.pop(0)
                newRow.pop(0)
                year = newRow.copy()
                for row in reader:
                    result += '[REGION, ' + \
                        row.pop(0) + ', ' + row.pop(0) + ', *, *]:'
                    result += '\n'
                    result += " ".join(year) + " "
                    result += ':=\n'
                    result += " ".join(row) + " "
                    result += '\n'
                result += ';\n'
        # 8 #all the parameters that do not have variables
        elif (sheetNames[i] in ['TotalTechnologyModelPeriodActivityUpperLimit']):
            result += 'param ' + sheetNames[i] + ' default 9999999 : \n'
            result += insert_no_variables(scenario, sheetNames, i)
        elif (sheetNames[i] in ['CapacityToActivityUnit']):
            result += 'param ' + sheetNames[i] + ' default 1 : \n'
            result += insert_no_variables(scenario, sheetNames, i)
        # 8 #all the parameters that do not have variables
        elif (sheetNames[i] in ['TotalTechnologyAnnualActivityLowerLimit']):
            result += 'param ' + sheetNames[i] + ' default 0 := \n'
            result += insert_no_variables(scenario, sheetNames, i)
        # 8 #all the parameters that do not have variables
        elif (sheetNames[i] in ['ModelPeriodEmissionLimit']):
            result += 'param ' + sheetNames[i] + ' default 999999 := ;\n'
        # 8 #all the   parameters   that do not have variables
        elif (sheetNames[i] in ['ModelPeriodExogenousEmission', 'AnnualExogenousEmission', 'OperationalLifeStorage']):
            result += 'param ' + sheetNames[i] + ' default 0 := ;\n'
        elif (sheetNames[i] in []):  # 8 #all the parameters that do not have variables
            result += 'param ' + sheetNames[i] + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheetNames[i] in ['TotalTechnologyModelPeriodActivityLowerLimit']):
            result += 'param ' + sheetNames[i] + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheetNames[i] in ['DepreciationMethod']):
            result += 'param ' + sheetNames[i] + ' default 1 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheetNames[i] in ['OperationalLife']):
            result += 'param ' + sheetNames[i] + ' default 1 : \n'
            result += insert_no_variables(scenario, sheetNames, i)
        elif (sheetNames[i] in ['DiscountRate']):  # default value
            with open(f'CSVFiles_{scenario}/' + sheetNames[i] + '.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    result += 'param ' + sheetNames[i] + ' default 0.1 := ;\n'
    return result


def insert_no_variables(scenario, sheetNames, i):
    result = ""
    with open(f'CSVFiles_{scenario}/' + sheetNames[i] + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        firstColumn = []
        secondColumn = []
        secondColumn.append('REGION')
        for row in reader:
            firstColumn.append(row[0])
            secondColumn.append(row[1])
        result += " ".join(firstColumn) + ' '
        result += ':=\n'
        result += " ".join(secondColumn) + ' '
        result += ';\n'
    return result


def insert_two_variables(scenario, sheetNames, i):
    result = ""
    with open(f'CSVFiles_{scenario}/' + sheetNames[i] + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        newRow = next(reader)
        newRow.pop(0)
        newRow.pop(0)
        year = newRow.copy()
        for row in reader:
            result += '[REGION, ' + row.pop(0) + ', *, *]:'
            result += '\n'
            result += " ".join(year) + " "
            result += ':=\n'
            result += " ".join(row) + " "
            result += '\n'
        result += ';\n'
    return result


def insert_table(scenario, name):
    result = ""
    with open(f'CSVFiles_{scenario}/' + name + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        newRow = next(reader)
        newRow.pop(0)  # removes the first element of the row
        result += " ".join(newRow) + " "
        result += ':=\n'
        for row in reader:
            result += " ".join(row) + " "
            result += '\n'
        result += ';\n'
    return result


def modifyNames(sheetNames):
    """I change the name of the sheets in the xlsx file to match with the csv
    actual ones
    """
    modifiedNames = sheetNames.copy()
    for i in range(len(modifiedNames)):
        if (modifiedNames[i] == "TotalAnnualMaxCapacityInvestmen"):
            modifiedNames[i] = "TotalAnnualMaxCapacityInvestment"
        elif (modifiedNames[i] == "TotalAnnualMinCapacityInvestmen"):
            modifiedNames[i] = "TotalAnnualMinCapacityInvestment"
        elif (modifiedNames[i] == "TotalTechnologyAnnualActivityLo"):
            modifiedNames[i] = "TotalTechnologyAnnualActivityLowerLimit"
        elif (modifiedNames[i] == "TotalTechnologyAnnualActivityUp"):
            modifiedNames[i] = "TotalTechnologyAnnualActivityUpperLimit"
        elif (modifiedNames[i] == "TotalTechnologyModelPeriodActLo"):
            modifiedNames[i] = "TotalTechnologyModelPeriodActivityLowerLimit"
        elif (modifiedNames[i] == "TotalTechnologyModelPeriodActUp"):
            modifiedNames[i] = "TotalTechnologyModelPeriodActivityUpperLimit"
    return modifiedNames


if __name__ == '__main__':
    if len(sys.argv) != 3:
        msg = "Usage: python {} <workbook_filename> <model_run> <output_filepath>"
        print(msg.format(sys.argv[0]))
        print(len(sys.argv))
        sys.exit(1)
    else:
        try:
            main(sys.argv[1], sys.argv[2])
        except Exception as ex:
            print(ex)
            sys.exit(1)
            


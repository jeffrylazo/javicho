# Fetching required modules
import numpy
import pandas
import logging
from os import path
from random import choices, random

# Definition of class Data for simple actions on DataFrames
class Data():
    '''
    Summary: This class generates a data frame with user-defined parameters, or an existing file.

    Examples: ds = Data([name,numRecords,columns,caseSet,dependance,probability])
              ds = Data([name,numRecords,columns,caseSet])
              ds = Data([name,r'inputPath'])
    
    Required elements for generating the data frame within the parameter list:
    1. name (List or Tuple) -> Used for default file deneration
    2. numRecords (List or Tuple) -> Number of records
    3. columns (List or Tuple) -> Names of the columns
    4. caseSet (List or Tuple) -> Options available per column

    Optional elements for generating the data frame within the parameter list:
    1. dependance (List or Tuple) -> Dependance of a column controlled thru the index of the independent column
    2. probability (List or Tuple) -> Weights for the randomized selection of caseSet value selection
    
    Required attributes for loading a dataset:
    1. inputPath (String) -> Path of the .cvs, .html, or .xlsx file 
    '''
    
    def __init__(self, parameter = [None], *args):
        '''Constructor'''
        
        # Attribute initialization
        self.__parameter = parameter
        self.__df = pandas.DataFrame(numpy.zeros(1))
        self.__dfTrain = None
        self.__dfTest = None

        try:
            # Check if self.__parameter is a list with 2, 4, or 6 elements and initialize accordingly
            if (isinstance(self.__parameter, list)):
                if (len(self.__parameter) == 2):
                    self.__name = str(self.__parameter[0])
                    self.__inputPath = self.__parameter[1]
                if ((len(self.__parameter) == 4) or (len(self.__parameter) == 6)):
                    self.__name = str(self.__parameter[0])
                    self.__numRecords = self.__parameter[1]
                    self.__columns = self.__parameter[2]
                    self.__caseSet = self.__parameter[3]
                    # The "None" keyword avoids errors on attributes if the user do not initialize them
                    self.__dependance = None
                    self.__probability = None
                    if (len(self.__parameter) == 6):
                        self.__dependance = self.__parameter[4]
                        self.__probability = self.__parameter[5]
                # Generate main dataset
                self.__generate_main()   

            # If it fails, log the error
            else:
                logging.error(" The constructor needs to be initialized as a list containing either 2, 3, or 6 parameters")
        
        # If the initialization generates the following exceptions, log the error
        except (TypeError, SyntaxError):
            logging.error(" The constructor needs to be initialized as a list containing either 2, 3, or 6 parameters")
        
    def __generate_main(self):
        '''
        Private method: Generates main data frame based on the parameters obtained from the constructor.
        '''
            
        # If there is no predefined data frame, create it from scratch using the parameters on the overloaded constructor
        if ((len(self.__parameter) == 4) or (len(self.__parameter) == 6)):
            self.__df = pandas.DataFrame(index=range(self.__numRecords),columns=self.__columns)
            for header in range(len(self.__columns)):
                if(isinstance(self.__caseSet[header],int)):
                    self.__df[self.__columns[header]] = pandas.Series(round(random()*self.__caseSet[header],0) for record in range(self.__numRecords))
                elif(isinstance(self.__caseSet[header],float)):
                    self.__df[self.__columns[header]] = pandas.Series(round(random()*self.__caseSet[header],2) for record in range(self.__numRecords))
                else:
                    if(self.__dependance[header] == -1):
                        if(isinstance(self.__caseSet[header],(tuple,list))):
                            self.__df[self.__columns[header]] = pandas.Series(str(choices(self.__caseSet[header])[0]) for record in range(self.__numRecords))
                    else:
                        for record in range(self.__numRecords):
                            self.__df.iloc[record][self.__columns[header]] = str(choices(self.__caseSet[header],weights=self.__probability[header],k=1)[0])
            self.__save_index()

        # If there is a predefined data frame, do not do anything
        elif (isinstance(self.__parameter[1], pandas.core.frame.DataFrame)):
            self.__df = self.__parameter[1]

        # Otherwise, load it from the desired location
        else:
            # Check if the path exists
            if (path.isfile(self.__inputPath)):
                # Check for the following file formats
                if (self.__parameter != self.__inputPath):
                    root, ext = path.splitext(self.__inputPath)
                    if (ext == '.csv'):
                        self.__df = pandas.read_csv(self.__inputPath)
                    if (ext == 'html'):
                        self.__df = pandas.read_html(self.__inputPath)
                    if (ext == '.xlsx'):
                        self.__df = pandas.read_excel(self.__inputPath,sheet_name='Sheet1')
                    self.__save_index()
                # Display the following log if the path exists, but the object was initialized incorrectly
                else:
                    logging.info(" Valid Path. Incorrect object initialization. Try df = Data([name,numRecords,columns,caseSet,dependance,probability]) or df = Data([name,r'inputPath'])")
            # Log the error id the path does not exist
            else:
                logging.error(" Invalid path. " + root + ext + " does not exists")

    def __save_index(self):
        '''
        Private method: Generates a specialized column for index.
        '''
        
        # Create a new Series on the data frame and store it temporary on another location
        temp = self.__df['Record'] = self.__df.index
        # Eliminate the Series on the data frame, permanently
        self.__df.drop(columns='Record', inplace = True)
        # Set the temporary Series as first column on the data frame
        self.__df.insert(0,'Record',temp)    
        
    def gen_train_test(self,percentage = 0.2):
        '''
        Abstract: Generate random traning and test subsets from main data frame.
        Example: ds1.train_test(0.3)
        '''
        
        # Check if percentage is a decimal
        if (percentage > 0):
            if (percentage > 1 and percentage < 100):
                percentage = percentage / 100

        # Generate sampling data frame and sort index in ascending order
        self.__dfTrain = self.__df.sample(frac = percentage, replace=False,random_state=1)
        self.__dfTrain = self.__dfTrain.sort_index()
        
        # Generate testing data frame
        self.__dfTest = self.__df[~self.__df.isin(self.__dfTrain)]
        self.__dfTest = self.__dfTest.dropna()
        self.__dfTest['returned'] = ' '
        temp = self.__dfTest['Record'] = self.__dfTest.index
        self.__dfTest.drop(columns='Record', inplace = True)
        self.__dfTest.insert(0,'Record',temp)

    def __file_name(self, desired_path = None, key = False):
        '''
        Private method: Generates names for csv files.
        '''
        
        new_name = desired_path
        if ((key == True) or (desired_path == None)):
            new_name = [None for i in range(3)]
            if (desired_path == None):
                old_name = self.__name
            if (key == True):
                old_name = path.splitext(desired_path)
            new_name[0] = str(old_name[0]) + '_main_data.csv'
            new_name[1] = str(old_name[0]) + '_train_data.csv'
            new_name[2] = str(old_name[0]) + '_test_data.csv'

        return new_name

    def save_main(self, desired_path = None, key = False):
        '''
        Abstract: Store main data frame on a .csv file. If path = None, default path is used.
        Example: ds1.save_main(r'TrainSet.csv')
        '''

        self.__df.to_csv(self.__file_name(desired_path, key)[0],index = False, header = True)
        
    def save_train(self, desired_path = None, key = False):
        '''
        Abstract: Store training data frame on a .csv file. If path = None, default path is used.
        Example: ds1.save_train(r'TrainSet.csv')
        '''
        
        self.__dfTrain.to_csv(self.__file_name(desired_path, key)[1],index = False, header = True)
                      
    def save_test(self, desired_path = None, key = False):
        '''
        Abstract: Store test data frame on a .csv file. If path = None, default path is used.
        Example: ds1.save_test(r'TestSet.csv')
        '''
        
        self.__dfTest.to_csv(self.__file_name(desired_path, key)[2],index = False, header = True)
                          
    def save_all(self, desired_path = None):
        '''
        Abstract: Store data frame on three separate .csv files using default paths.
        Example:x,y,z = ds1.save_all()
        '''
        
        self.save_main(desired_path, True)
        self.save_train(desired_path, True)
        self.save_test(desired_path, True)
    
    def get_data(self):
        '''
        Abstract: Returns data frames as three separate objects.
        Example: x,y,z = ds1.get_data()
        '''
        
        return self.__df, self.__dfTrain, self.__dfTest

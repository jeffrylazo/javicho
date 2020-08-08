import numpy as np
import pandas as pd
from javoxl import Data

# First dataset
ds1 =Data(['workshop',50,['computer','display','keyboard','mouse','sound','budget','membership','returned'],
                 [('PC','Laptop'),('Yes','No'),('Yes','No'),('Yes','No'),40,('$700','$1400','$2100'),('No', 'Bronze', 'Silver', 'Gold'),
                  ('Yes','No')],[-1,0,0,0,0,-1,-1,-1],[None,(90,10),(85,15),(70,30),None,None,None,None]])
ds1.gen_train_test(0.2)
ds1.save_all('abc.csv')

# Second dataset
ds2 = Data(['workshop','workshop_main_data.csv'])
ds1.gen_train_test(10)
ds2.save_all()

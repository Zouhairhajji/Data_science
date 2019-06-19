#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, DoubleType
import operator
import re


# In[2]:


os.environ["SPARK_HOME"] = "/Users/zouhairhajji/Documents/dev/spark-2.4.0-bin-hadoop2.7" 

spark = SparkSession.builder \
        .master('local[*]') \
        .appName('Matrix multiplication') \
        .config("spark.driver.memory", "2g") \
        .enableHiveSupport() \
        .getOrCreate()


# In[3]:





# # Spark algorithm

# In[4]:

file_regex = 'inputs/*.demo'
flat_data = spark.sparkContext.wholeTextFiles(file_regex)

files = flat_data.map(lambda x: x[0].split('/')[-1]).collect()


def filter_appropriate_words(x):
    splitet_str = re.split('\n| |\'', x)
    
    splitet_str = list(filter(None, splitet_str))
    splitet_str = list(filter(lambda x: False if len(x) < 3 else True, splitet_str))
    
    return splitet_str

formated_input = flat_data    \
    .map(lambda x: (x[0].split('/')[-1],  filter_appropriate_words(x[1])    ))    \
    .flatMap(lambda x: [ (x[0], word) for word in x[1]]  )


result = formated_input     \
    .cartesian(formated_input)   \
    .filter(lambda x: x[0][0] == x[1][0])  \
    .filter(lambda x: x[0][1] != x[1][1])  \
    .map(lambda x:  ( (x[0][0], x[0][1], x[1][1]), 1)    ) \
    .reduceByKey(lambda x, y: x+y)   \
    .map(lambda x: (x[0][0], (x[0][1], x[0][2]), x[1]-1))  

result.saveAsTextFile('output_spark')
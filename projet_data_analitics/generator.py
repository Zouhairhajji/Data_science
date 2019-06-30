#!/usr/bin/env python

import sys
import random
import numpy as np

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.mllib.random import RandomRDDs

 
# create connector with spark
spark = SparkSession.builder \
        .master('local[*]')  \
        .enableHiveSupport() \
        .getOrCreate()

sc = spark.sparkContext



# methods 
def calculate_rdn_with_std(centroids, points, std, cluster, dimension):
    values = []
    for d in range(dimension):
        value = centroids[d] + points[d] * std
        value = round(value, 2)
        values.append( value )
    return (values, cluster )
 
    
def format_as_csv(x):
    line = ""
    for i in x[0]:
        line += '{},'.format(i)
    line += '{}'.format(x[1])
    return line

 


if __name__ == "__main__":
    file_name = sys.argv[1]  # file name to be generated
    points = int(sys.argv[2]) # number of points to be generated
    count_cluster = int(sys.argv[3]) # number of clusters
    dimension = int(sys.argv[4]) # dimension of the data
    std = int(sys.argv[5]) # standard deviation
    



    clusters = range(0, count_cluster)
    clusters_rdd = sc.parallelize(clusters)


    # create random centroids 
    centroids_rdd = clusters_rdd   \
        .map(lambda x : (x, random.sample(list(np.arange(0, 100, 0.1)), k=dimension)) )


    # generate random point and assign them to random centroids
    random_values_vector = RandomRDDs   \
        .normalVectorRDD(sc, numRows=points, numCols=dimension, numPartitions=count_cluster, seed=1)   \
        .map(lambda x : (random.randint(0, count_cluster - 1), list(x)))

    result = random_values_vector   \
        .join(centroids_rdd)     \
        .map(lambda x: calculate_rdn_with_std(x[1][1], x[1][0], std, x[0], dimension)) \
        .map(format_as_csv) 
 

    result.coalesce(1).saveAsTextFile(file_name)
    
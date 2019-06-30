#!/usr/bin/env python


import os
import sys 
import numpy as np
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, DoubleType
import operator
import re

 

spark = SparkSession.builder \
        .master('local[*]') \
        .enableHiveSupport() \
        .getOrCreate()

sc = spark.sparkContext



def loadData(namefile) :
    textfile = sc.textFile(namefile)    \
            .zipWithIndex()   \
            .map(lambda x: (x[1], x[0].split(',')  ))  \
            .map(lambda x: (x[0], [float(i) for i in x[1]]  ))
            
    return textfile

def dimension(rdd_load_data) :
    return rdd_load_data.map(lambda x: len(x[1])).reduce(lambda x, y: max(x, y)) 


#calculate the distance between each point and centroids
def calculate_distance(x, y):
    x = np.array(x)
    y = np.array(y)
    return np.sqrt(np.sum(np.square( x-y )))  
    
    
#assign a centroid to each point
def assignToCluster(rdd, centroids):
    cartes = rdd.cartesian(centroids) 
    
    cartes = cartes.map(lambda x: (x[0][0], (x[1][0], calculate_distance(x[1][1], x[0][1]))  ) )
    cartes = cartes.groupByKey().mapValues(closestcentroide)
    return cartes

#choose the closest centroid to each node
def closestcentroide(y):
    y = list(y)
    closest = y[0]
    
    for couple in y:
        if(closest[1] > couple[1]): 
            closest = couple
            
    return  closest

#formula to calculate the new coordinate (mean)
def calculate_new_coordinate(x): 
    mean = lambda x: sum(x) / len(x)
    return [ round(mean(x), 2) for x in zip(*x)]  


# calculate the new coordinate of each centroid
def computeCentroids(rdd, assigned_centroids): 
     return assigned_centroids   \
                .join(rdd)       \
                .map(lambda x: (x[1][0][0], x[1][1]) )       \
                .groupByKey()       \
                .mapValues(calculate_new_coordinate)



# calculate the distance intra clusters
def computeIntraClusterDistance(rdd, centroids):
    initdistance = assignToCluster(rdd, centroids) 
    totaldistance = initdistance.map(lambda x: (1, x[1][1]) ).reduceByKey(lambda x,y: x+y)
    return totaldistance   

def initCentroids(rdd_flat_data, k):
    seed = random.randint(0, 100)
    
    centroids = rdd_flat_data.takeSample(False, k, seed=seed)
    return  sc.parallelize(centroids)   \
                .zipWithIndex()         \
                .map(lambda x: (x[1], x[0][1])) 


def kmeans(filename, k, max_attempt = 20, debug=True):
    flat_data = loadData(filename)
    #dim = dimension(flat_data)
    
    centroids = initCentroids(flat_data, k)
     
    #assign every point to a centroids
    assigned_points = assignToCluster(flat_data, centroids)
    
    #compute centroids
    old_centroids = computeCentroids(flat_data, assigned_points)
    
    converged = False
    step_count = 0
    step_max = max_attempt
    
    while not converged  and step_count < step_max:
        step_count += 1
        if(debug):
            print('running step ', step_count)
        
        
        assigned_points = assignToCluster(flat_data, old_centroids) 
        
        new_centroids   = computeCentroids(flat_data, assigned_points)
        distance_intracluster = computeIntraClusterDistance(flat_data, new_centroids)
        
        
        centroid_changed = old_centroids.join(new_centroids).map(lambda x: np.sqrt(np.sum(np.square(np.array(x[1][0]) - np.array(x[1][1])))) ).reduce(lambda x, y: x+y) 
        if(debug):
            print('    ->  ' ,  round(centroid_changed, 2))
        
        
         
        if centroid_changed == 0:
            converged = True 
        old_centroids = sc.parallelize(new_centroids.collect()) 
            
        
    return (step_count, distance_intracluster.take(1)[0][1], assigned_points, old_centroids  ) 

if __name__ == "__main__":
    file_name = sys.argv[1]
    k = int(sys.argv[2])
    max_attempt = int(sys.argv[3])
    

    step_count, distance, points, centroids= kmeans(file_name, k, max_attempt)
    
    print("\n")
    print("distance : " , distance)
    print("nbr iteration : " , step_count)
    print("\n")
    print("points [echantillon]: " , points.take(2))
    print("centroids [echantillon]: ", centroids.take(2))
    print("\n")



    
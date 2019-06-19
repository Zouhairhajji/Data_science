


# hadoop streaming 
start_time="$(date -u +%s)"

rm -rf output_hadoop && hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar  \
    -input inputs/*.demo -output output_hadoop \
    -file hadoop_streaming/mapper.py -mapper hadoop_streaming/mapper.py   \
    -file hadoop_streaming/reducer.py -reducer hadoop_streaming/reducer.py   \

command_code=$(echo $?)

end_time="$(date -u +%s)"
elapsed_hadoop="$(($end_time-$start_time))"

test $command_code -eq 0 && echo rm -rf *.py

rm -rf mapper.py && rm -rf reducer.py



#spark
start_time="$(date -u +%s)"

rm -rf output_spark && python3.7 spark/spark_job_co_occurance.py

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"


echo "Total of $elapsed seconds elapsed for spark process"
echo "Total of $elapsed_hadoop seconds elapsed for hadoop process"

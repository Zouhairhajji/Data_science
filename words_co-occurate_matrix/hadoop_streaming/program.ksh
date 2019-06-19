


# hadoop streaming
rm -rf output  \
    && \
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar  \
    -input inputs/*.demo -output output \
    -file mapper.py -mapper mapper.py   \
    -file reducer.py -reducer reducer.py   \
    && \
cat output/part-00000 
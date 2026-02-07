#!/bin/bash
set -e

# Start the Spark Thrift Server in the background using spark-submit directly.
# Using the HiveThriftServer2 class avoids daemon-mode issues with start-thriftserver.sh
# inside Docker containers.
/opt/spark/bin/spark-submit \
  --class org.apache.spark.sql.hive.thriftserver.HiveThriftServer2 \
  --name "Spark Thrift Server" \
  --master "local[*]" \
  --conf spark.sql.warehouse.dir=/opt/spark-data/spark-warehouse \
  --conf javax.jdo.option.ConnectionURL="jdbc:derby:;databaseName=metastore_db;create=true" \
  --conf spark.hadoop.hive.server2.authentication=NONE \
  --conf spark.hadoop.hive.server2.thrift.bind.host=0.0.0.0 \
  --conf spark.driver.extraJavaOptions="-Dderby.system.home=/opt/spark-data" \
  spark-internal &

PID=$!

# Wait for the Thrift Server to accept connections.
# The apache/spark image doesn't include netcat, so use bash /dev/tcp instead.
echo "Waiting for Spark Thrift Server to start..."
for i in $(seq 1 120); do
  if (echo > /dev/tcp/localhost/10000) 2>/dev/null; then
    echo "Spark Thrift Server is ready."
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "Spark Thrift Server process exited unexpectedly."
    exit 1
  fi
  sleep 2
done

if ! (echo > /dev/tcp/localhost/10000) 2>/dev/null; then
  echo "Timed out waiting for Spark Thrift Server."
  exit 1
fi

# Load sample data
echo "Loading sample data..."
/opt/spark/bin/beeline -u "jdbc:hive2://localhost:10000" -f /opt/init-data.sql --silent=true
echo "Sample data loaded."

# Keep the container alive by waiting on the Spark process
wait $PID

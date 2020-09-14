# This FOR is necessary because for some reason the environment variables
# loaded from the docker-compose do not work in CRON
# for more details consider reading
# https://stackoverflow.com/questions/27771781/how-can-i-access-docker-set-environment-variables-from-a-cron-job
for variable_value in $(cat /proc/1/environ | sed 's/\x00/\n/g'); do
    export $variable_value
  done

# Update the database with the latest properties
/usr/local/bin/python3.7 /property_anomaly_detector/property_anomaly_detector/scraper/zoopla/zoopla.py

# Detect the anomalies over the latest properties
/usr/local/bin/python3.7 /property_anomaly_detector/property_anomaly_detector/scraper/anomaly/detect_anomalies.py
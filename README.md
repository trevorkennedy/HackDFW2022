# HackDFW 2022
This repo is a project submission for [HackDFW](https://hackdfw.com/) 2022. The backend architecture is comprised of a single AWS Lambda function written in Python that calls Amazon Rekognition service to label an image, then calls Amazon Polly to convert the detected labels to speach (saved as an MP3 file on S3), logs the event to InfluxDB Cloud (for easy visualizations) and returns the resulting MP3 file to the caller. 

## Requirements
AWS Lambda

- Set Timeout to 6+ seconds
- Python v3.8
- Add IAM permission policies
	- AmazonS3FullAccess
	- AmazonPollyFullAccess
	- AmazonRekognitionFullAccess
- Environment variables
	- INFLUXDB_BUCKET - InfluxDB database bucket name
	- INFLUXDB_ORG - InfluxDB organization
	- INFLUXDB_TOKEN	- InfluxDB auth token
	- INFLUXDB_URL - InfluxDB endpoint 
	- S3_BUCKET - location to save files
- Custom layer for the InfluxDB client library
	- mkdir python
	- pip install influxdb-client -t python
	- zip -r influx.zip python
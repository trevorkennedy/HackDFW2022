import os
import json
import boto3
import uuid
import base64
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS


s3_bucket = os.environ['S3_BUCKET']
influx_token = os.environ['INFLUXDB_TOKEN']
influx_org = os.environ['INFLUXDB_ORG']
influx_url = os.environ['INFLUXDB_URL']
influx_bucket = os.environ['INFLUXDB_BUCKET']

def save_influxdb(image, label, value):
    client = influxdb_client.InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
    point = (
        Point("hack_dfw").tag("image", image).tag("label", label).field("confidence", value)
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

def get_image_labels(bucket, photo):
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=10)
    return response
    
def process_image(bucket, image):
    label_response = get_image_labels(bucket, image)
    first_label = label_response['Labels'][0]
    return first_label

def save_file(data, file_name, ext):
    file_name = f"{file_name}.{ext}"
    s3 = boto3.client('s3')
    s3.put_object(Body=data, Bucket=s3_bucket, Key=file_name)
    return file_name

def gen_audio(text, file_name):
    polly = boto3.client("polly")
    response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")
    stream = response["AudioStream"]
    return save_file(stream.read(), file_name, 'mp3')

def lambda_handler(event, context):
    status = 204
    body = None
    
    if 'body' in event:
        status = 200
        file_name = str(uuid.uuid4())[:12]
        data = base64.b64decode(event['body'])
        file = save_file(data, file_name, 'bin')
        label = process_image(s3_bucket, file)
        label_name = label['Name']
        confidence_level = label['Confidence']
        mp3 = gen_audio(label_name, file_name)
        save_influxdb(file, label_name, confidence_level)
        response = {
            "label": label_name,
            "confidence": confidence_level,
            "image_file": f'https://{s3_bucket}.s3.amazonaws.com/{file}',
            "audio_file": f'https://{s3_bucket}.s3.amazonaws.com/{mp3}'
        }
        body = json.dumps(response)

    return {
        'statusCode': status,
        'body': body
    }
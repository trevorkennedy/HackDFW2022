 import os
import json
import boto3
import uuid
import base64
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS


s3_bucket = os.environ['S3_BUCKET']
aws_region = os.environ['S3_REGION']
model = os.environ['MODEL_ARN']
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
    client = boto3.client('rekognition', region_name=aws_region)
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=10)
    return response
    
def get_custom_labels(photo):
    client = boto3.client('rekognition', region_name=aws_region)
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': s3_bucket, 'Name': photo}},
                                           ProjectVersionArn=model)
    labels = response['CustomLabels']
    if len(labels) > 0:
        return labels[0]['Name'], labels[0]['Confidence']
    else:
        generic_label = process_image(photo)
        return generic_label['Name'], generic_label['Confidence']

def process_image(image):
    label_response = get_image_labels(s3_bucket, image)
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
        file_name = str(uuid.uuid4())[:14]
        data = base64.b64decode(event['body'])
        file = save_file(data, file_name, 'jpeg')
        label, confidence = get_custom_labels(file)
        mp3 = gen_audio(label, file_name)
        save_influxdb(file, label, confidence)
        response = {
            "label": label,
            "confidence": confidence,
            "image_file": f'https://{s3_bucket}.s3.amazonaws.com/{file}',
            "audio_file": f'https://{s3_bucket}.s3.amazonaws.com/{mp3}'
        }
        body = json.dumps(response)

    return {
        'statusCode': status,
        'body': body
    }
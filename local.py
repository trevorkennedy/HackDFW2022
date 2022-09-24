import boto3
import pathlib
import base64


def get_image_labels(s3_bucket, photo):
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': s3_bucket, 'Name': photo}},
        MaxLabels=10)
    return response


def process_image(bucket, image):
    ext = pathlib.Path(image).suffix
    if ext in ['.jpg', '.png']:
        label_response = get_image_labels(bucket, image)
        first_label = label_response['Labels'][0]
        for label in label_response['Labels']:
            print(label['Name'], label['Confidence'])
        return first_label


def encode_image(file):
    with open(file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        print(encoded_string)


def main():
    img = 'doritos_cool_ranch.jpg'
    s3_bucket = 'hackdfw123'
    process_image(s3_bucket, img)
    # encode_image(r'/Users/tkennedy/Desktop/doritos_cool_ranch.jpg')


if __name__ == "__main__":
    main()

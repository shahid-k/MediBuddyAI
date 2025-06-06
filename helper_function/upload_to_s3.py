import boto3
import os

def upload_pdf_to_s3(pdf_file_path, s3_key):
    s3 = boto3.client('s3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    s3.upload_file(pdf_file_path, "medibuddyai", s3_key)
    s3_url = f"https://medibuddyai.s3.amazonaws.com/{s3_key}"
    return s3_url

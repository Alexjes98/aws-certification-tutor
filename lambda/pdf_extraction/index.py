import json
import os
import boto3
import pymupdf
import tempfile
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Get the S3 bucket and key from the Step Functions input
    message_body = json.loads(event['messageBody'])
    s3_record = message_body['Records'][0]['s3']
    bucket = s3_record['bucket']['name']
    key = unquote_plus(s3_record['object']['key'])
    
    print(f"Processing PDF from bucket: {bucket}, key: {key}")
    
    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        # Download the PDF file from S3
        s3_client.download_file(bucket, key, tmp_file.name)
        
        # Process the PDF
        text_content = ""
        doc = pymupdf.open(tmp_file.name)
        
        for page in doc:
            text_content += page.get_text()
        
        doc.close()
        
        # Clean up the temporary file
        os.unlink(tmp_file.name)
        
        return {
            'statusCode': 200,
            'body': {
                'bucket': bucket,
                'key': key,
                'text_content': text_content
            }
        }
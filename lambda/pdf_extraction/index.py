import json
import os
import boto3
import pymupdf
import tempfile

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda function to extract text from a PDF file stored in an S3 bucket and returns the text as pages in a list.
    
    Args:
        event (dict): The event data passed to the Lambda function.
        event['document_id'] (str): The ID of the document to extract text from.
        event['bucket'] (str): The name of the S3 bucket containing the document.
        context (dict): The context object passed to the Lambda function.
    Returns:
        dict: A dictionary containing the bucket, document_id, and pages.
    """
    
    if not event or not event.get('document_id') or not event.get('bucket'):
        return {
            'statusCode': 400,
            'body': 'Missing document_id or bucket'
        }
    
    # Get the S3 bucket and key from the Step Functions input
    document_id = event.get('document_id')
    bucket = event.get('bucket')
    
    print(f"Processing PDF from bucket: {bucket}, document_id: {document_id}")
    
    try:
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        # Download the PDF file from S3
            s3_client.download_file(bucket, document_id, tmp_file.name)
        
        # Process the PDF
        pages = []
        doc = pymupdf.open(tmp_file.name)
        
        for page in doc:
            pages.append(page.get_text())
        
        doc.close()
        
        # Clean up the temporary file
        os.unlink(tmp_file.name)
        
        return {
            'statusCode': 200,
            'body': {
                'bucket': bucket,
                'document_id': document_id,
                'pages': pages
            }
        }
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return {
            'statusCode': 500,
            'body': str(e)
        }
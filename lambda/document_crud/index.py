import json
import os
import boto3
import uuid
import base64
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
bucket_name = os.environ.get('SOURCE_BUCKET_NAME')

def lambda_handler(event, context):
    """
    Lambda function to handle CRUD operations for documents in S3 bucket
    """
    try:
        http_method = event.get('httpMethod')
        path_parameters = event.get('pathParameters', {})
        
        if http_method == 'GET':
            if path_parameters and path_parameters.get('document_id'):
                # Get a specific document
                document_id = path_parameters.get('document_id')
                return get_document(document_id)
            else:
                # List all documents
                return list_documents()
                
        elif http_method == 'POST':
            # Create a new document
            return create_document(event)
            
        elif http_method == 'DELETE' and path_parameters:
            # Delete a document
            document_id = path_parameters.get('document_id')
            return delete_document(document_id)
            
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid request method or parameters'})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def list_documents():
    """List all documents in the bucket"""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        documents = []
        if 'Contents' in response:
            for item in response['Contents']:
                # Get metadata for each document
                obj_metadata = s3.head_object(Bucket=bucket_name, Key=item['Key'])
                document = {
                    'document_id': item['Key'],
                    'size': item['Size'],
                    'last_modified': item['LastModified'].isoformat(),
                    'metadata': obj_metadata.get('Metadata', {})
                }
                documents.append(document)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(documents)
        }
    except Exception as e:
        print(f"Error listing documents: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_document(document_id):
    """Get a specific document by ID"""
    try:
        # Generate a pre-signed URL for the document
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': document_id},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        # Get document metadata
        metadata = s3.head_object(Bucket=bucket_name, Key=document_id)
        
        document = {
            'document_id': document_id,
            'url': url,
            'metadata': metadata.get('Metadata', {}),
            'content_type': metadata.get('ContentType', 'application/octet-stream'),
            'size': metadata.get('ContentLength', 0),
            'last_modified': metadata.get('LastModified').isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(document)
        }
    except s3.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Document not found'})
        }
    except Exception as e:
        print(f"Error getting document: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def create_document(event):
    """Create a new document in the S3 bucket"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Generate a unique document ID if not provided
        document_id = body.get('document_id', f"{uuid.uuid4()}")
        
        # Check if the document contains base64 encoded file data
        if 'file_content' in body:
            # Decode base64 file data
            file_content = base64.b64decode(body['file_content'])
            content_type = body.get('content_type', 'application/octet-stream')
            
            # Upload to S3
            metadata = body.get('metadata', {})
            s3.put_object(
                Bucket=bucket_name,
                Key=document_id,
                Body=file_content,
                ContentType=content_type,
                Metadata=metadata
            )
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'document_id': document_id,
                    'message': 'Document created successfully'
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No file content provided'})
            }
    except Exception as e:
        print(f"Error creating document: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def delete_document(document_id):
    """Delete a document from the S3 bucket"""
    try:
        # Check if the document exists
        s3.head_object(Bucket=bucket_name, Key=document_id)
        
        # Delete the document
        s3.delete_object(Bucket=bucket_name, Key=document_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'document_id': document_id,
                'message': 'Document deleted successfully'
            })
        }
    except s3.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Document not found'})
        }
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        } 
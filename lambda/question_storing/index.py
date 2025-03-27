import json
import boto3
import uuid
from datetime import datetime, UTC

import os

QUESTIONS_TABLE_NAME = os.environ.get("QUESTIONS_TABLE_NAME")

def lambda_handler(event, context):
    """
    This lambda function stores the question in the DynamoDB table.
    @param event: The event object from the API Gateway
    @param context: The context object from the API Gateway
    @return: A dictionary containing the status code and the body of the response
    """
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(QUESTIONS_TABLE_NAME)
        
        # Get the question object from the event
        question_data = event.get('question')
        
        if not question_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No question data provided'})
            }
        
        # Create a unique ID for the question
        question_id = str(uuid.uuid4())
        
        # Get current UTC time
        current_time = datetime.now(UTC).isoformat()
        
        # Prepare the item for DynamoDB
        item = {
            'questionId': question_id,
            'questionText': question_data['questionText'],
            'options': question_data['options'],
            'correctOptions': question_data['correctOptions'],
            'optionsExplanation': question_data['optionsExplanation'],
            'tags': question_data['tags'],
            'difficulty': question_data['difficulty'],
            'createdAt': current_time,
            'updatedAt': current_time
        }
        
        # Store the item in DynamoDB
        table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Question stored successfully',
                'questionId': question_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

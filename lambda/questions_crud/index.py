import json
import os
import boto3
import uuid
from decimal import Decimal
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('QUESTIONS_TABLE_NAME')
table = dynamodb.Table(table_name)

# Helper class to handle Decimal types in DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """
    Lambda function to handle CRUD operations for questions in DynamoDB
    """
    try:
        http_method = event.get('httpMethod')
        path_parameters = event.get('pathParameters', {})
        
        if http_method == 'GET':
            if path_parameters and path_parameters.get('question_id'):
                # Get a specific question
                question_id = path_parameters.get('question_id')
                return get_question(question_id)
            else:
                # List all questions
                return list_questions(event)
                
        elif http_method == 'POST':
            # Create a new question
            return create_question(event)
            
        elif http_method == 'PUT' and path_parameters:
            # Update a question
            question_id = path_parameters.get('question_id')
            return update_question(question_id, event)
            
        elif http_method == 'DELETE' and path_parameters:
            # Delete a question
            question_id = path_parameters.get('question_id')
            return delete_question(question_id)
            
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

def list_questions(event):
    """List all questions from DynamoDB with optional filtering"""
    try:
        # Get query parameters for filtering and pagination
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Query parameters
        limit = int(query_params.get('limit', 50))
        category = query_params.get('category')
        difficulty = query_params.get('difficulty')
        
        # Basic scan operation
        scan_params = {
            'Limit': limit
        }
        
        # Add filter expression if filters provided
        filter_expressions = []
        expression_attribute_values = {}
        
        if category:
            filter_expressions.append('category = :category')
            expression_attribute_values[':category'] = category
            
        if difficulty:
            filter_expressions.append('difficulty = :difficulty')
            expression_attribute_values[':difficulty'] = difficulty
        
        if filter_expressions:
            scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
            scan_params['ExpressionAttributeValues'] = expression_attribute_values
        
        # Execute the scan
        response = table.scan(**scan_params)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response.get('Items', []), cls=DecimalEncoder)
        }
    except Exception as e:
        print(f"Error listing questions: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_question(question_id):
    """Get a specific question by ID"""
    try:
        response = table.get_item(
            Key={'question_id': question_id}
        )
        
        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Question not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(item, cls=DecimalEncoder)
        }
    except Exception as e:
        print(f"Error getting question: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def create_question(event):
    """Create a new question in DynamoDB"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Generate a unique ID if not provided
        question_id = body.get('question_id', str(uuid.uuid4()))
        
        # Basic validation
        if 'question_text' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Question text is required'})
            }
        
        # Prepare item for DynamoDB
        timestamp = datetime.now().isoformat()
        item = {
            'question_id': question_id,
            'question_text': body['question_text'],
            'answers': body.get('answers', []),
            'correct_answer': body.get('correct_answer'),
            'explanation': body.get('explanation', ''),
            'category': body.get('category', 'general'),
            'difficulty': body.get('difficulty', 'medium'),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Add to DynamoDB
        table.put_item(Item=item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'question_id': question_id,
                'message': 'Question created successfully'
            })
        }
    except Exception as e:
        print(f"Error creating question: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def update_question(question_id, event):
    """Update an existing question in DynamoDB"""
    try:
        # Check if the question exists
        response = table.get_item(
            Key={'question_id': question_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Question not found'})
            }
        
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        
        # Prepare update expression and values
        update_expression = "SET updated_at = :updated_at"
        expression_attribute_values = {
            ':updated_at': datetime.now().isoformat()
        }
        
        # Add all updated fields
        update_fields = {
            'question_text': 'question_text',
            'answers': 'answers',
            'correct_answer': 'correct_answer',
            'explanation': 'explanation',
            'category': 'category',
            'difficulty': 'difficulty'
        }
        
        for key, attr_name in update_fields.items():
            if key in body:
                update_expression += f", {attr_name} = :{key}"
                expression_attribute_values[f':{key}'] = body[key]
        
        # Update the item in DynamoDB
        table.update_item(
            Key={'question_id': question_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'question_id': question_id,
                'message': 'Question updated successfully'
            })
        }
    except Exception as e:
        print(f"Error updating question: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def delete_question(question_id):
    """Delete a question from DynamoDB"""
    try:
        # Check if the question exists
        response = table.get_item(
            Key={'question_id': question_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Question not found'})
            }
        
        # Delete the question
        table.delete_item(
            Key={'question_id': question_id}
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'question_id': question_id,
                'message': 'Question deleted successfully'
            })
        }
    except Exception as e:
        print(f"Error deleting question: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        } 
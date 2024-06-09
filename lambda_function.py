import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = 'zacks-trade-data'
table = dynamodb.Table(table_name)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    logger.info('Event structure: %s', json.dumps(event, indent=2))
    
    # Extract date from the event (assuming the date is passed in the query string parameters)
    query_params = event.get('queryStringParameters', {})
    trade_date = query_params.get('date', None)
    
    try:
        if trade_date:
            # Query the DynamoDB table for the specified trade date
            response = table.query(
                IndexName='CustomTradeDay-index',  # Use the GSI if available
                KeyConditionExpression=Key('CustomTradeDay').eq(trade_date)
            )
        else:
            # Scan the entire table if no date is provided
            response = table.scan()
        
        trades = response.get('Items', [])

        # Return the trades as JSON
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(trades, default=decimal_default)
        }
    
    except Exception as e:
        logger.error('Error querying trades: %s', str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

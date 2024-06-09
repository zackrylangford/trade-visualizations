import json
import boto3
from decimal import Decimal
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = 'zacks-trade-data'  # Replace with your table name
table = dynamodb.Table(table_name)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    logger.info('Event structure: %s', json.dumps(event, indent=2))
    
    try:
        # Scan the entire table
        logger.info('Scanning entire table')
        response = table.scan()
        
        trades = response.get('Items', [])
        logger.info('Trades fetched: %d', len(trades))

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

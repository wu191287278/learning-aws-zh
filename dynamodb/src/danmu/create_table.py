import boto3
import json
import time

def create_table(client):
    client.create_table(
        TableName='danmu',
        KeySchema=[
            { 
                'AttributeName': 'objectId', 
                'KeyType': 'HASH'
            },
            { 
                'AttributeName': 'id', 
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            { 
                'AttributeName': 'objectId', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'id', 
                'AttributeType': 'N' 
            }
        ],
        ProvisionedThroughput={       
            'ReadCapacityUnits': 5, 
            'WriteCapacityUnits': 5
        }
    )


# 用于查询我评论的作品
def created_user_id_id_index(client):
    client.update_table(
        TableName='danmu',
        AttributeDefinitions=[
            { 
                'AttributeName': 'userId', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'id', 
                'AttributeType': 'N' 
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'userId_id',
                    'KeySchema': [
                        {'AttributeName': 'userId', 'KeyType': 'HASH'},  
                        {'AttributeName': 'id', 'KeyType': 'RANGE'},
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
                }
            }
        ]
    )

 
endpoint_url = "http://localhost:8000"
access_key = ""  # 本地Dynamodb不需要填写
secret_key = ""
region_name = "us-west-2"
client = boto3.client('dynamodb',
                          endpoint_url=endpoint_url,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region_name,)

# 删除表
try:
    client.delete_table(TableName = 'danmu')
except :
    pass

create_table(client)
created_user_id_id_index(client)

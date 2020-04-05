import boto3
import json
import time

def create_table(client):
    
    client.create_table(
        TableName='liking',
        KeySchema=[
            { 
                'AttributeName': 'id', 
                'KeyType': 'HASH'
            },
            { 
                'AttributeName': 'userId', 
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            { 
                'AttributeName': 'id', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'userId', 
                'AttributeType': 'S' 
            }
        ],
        ProvisionedThroughput={       
            'ReadCapacityUnits': 5, 
            'WriteCapacityUnits': 5
        }
    )


# 用于查询谁点赞了该作品
def created_id_created_at_index(client):
    client.update_table(
        TableName='liking',
        AttributeDefinitions=[
            { 
                'AttributeName': 'id', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'createdAt', 
                'AttributeType': 'N' 
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'id_createdAt',
                    'KeySchema': [
                        {'AttributeName': 'id', 'KeyType': 'HASH'},  
                        {'AttributeName': 'createdAt', 'KeyType': 'RANGE'},
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

# 用于查询我点赞的作品
def created_user_id_created_at_index(client):
    client.update_table(
        TableName='liking',
        AttributeDefinitions=[
            { 
                'AttributeName': 'userId', 
                'AttributeType': 'S'
            },
            { 
                'AttributeName': 'createdAt', 
                'AttributeType': 'N'
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'userId_createdAt',
                    'KeySchema': [
                        {'AttributeName': 'userId', 'KeyType': 'HASH'},  
                        {'AttributeName': 'createdAt', 'KeyType': 'RANGE'},
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

# 用于查询我被点赞的作品
def created_owner_id_created_at_index(client):
    client.update_table(
        TableName='liking',
        AttributeDefinitions=[
            { 
                'AttributeName': 'ownerId', 
                'AttributeType': 'S'
            },
            { 
                'AttributeName': 'createdAt', 
                'AttributeType': 'N' 
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'ownerId_createdAt',
                    'KeySchema': [
                        {'AttributeName': 'ownerId', 'KeyType': 'HASH'},  
                        {'AttributeName': 'createdAt', 'KeyType': 'RANGE'},
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



"""
点赞
user_id: 点赞用户
owner_id: 作品所属用户
id:作品
"""
def liking(client,user_id, owner_id, id):
    created_at = int(round(time.time() * 1000))

    item = {'userId':{'S':user_id},'id':{'S':id},'ownerId':{'S':owner_id},'createdAt':{'N':str(created_at)}}
    client.put_item(TableName='liking',Item=item)


def importData(client):
    for id in range(1,10):
        for user_id in range(1,100):
            if user_id==id:
                continue
            liking(client,str(user_id),str(id),str(id))


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
    client.delete_table(TableName = 'liking')
except :
    pass

create_table(client)
created_id_created_at_index(client)
# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)
created_user_id_created_at_index(client)

# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)
created_owner_id_created_at_index(client)

# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)

# 导入测试数据
importData(client)

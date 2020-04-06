import boto3
import json
import time

def create_table(client):
    client.create_table(
        TableName='comment',
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
        TableName='comment',
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

# 查询我被评论的作品
def created_owner_id_id_index(client):
    client.update_table(
        TableName='comment',
        AttributeDefinitions=[
            { 
                'AttributeName': 'ownerId', 
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
                    'IndexName': 'ownerId_id',
                    'KeySchema': [
                        {'AttributeName': 'ownerId', 'KeyType': 'HASH'},  
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


"""
评论
object_id 作品ID
user_id: 评论用户
owner_id: 作品拥有者
"""
def comment(client,object_id,user_id,owner_id,content):
    # 使用纳秒作为id,线上请使用snowflake算法进行生成有序id
    id = int(round(time.time() * 1000000))
    created_at = int(round(time.time() * 1000))
    item = {
        'id':{'N':str(id)},
        'objectId':{'S':object_id},
        'userId':{'S':user_id},
        'ownerId':{'S':owner_id},
        'content':{'S':content},
        'createdAt':{'N':str(created_at)}
        }
    client.put_item(TableName='comment',Item=item)


def importData(client):
    for user_id in range(2,30):
        comment(client,'1',str(user_id),'1',str(user_id)+"_hello")

 
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
    client.delete_table(TableName = 'comment')
except :
    pass

create_table(client)
created_user_id_id_index(client)
# Dynamodb 有建时间限制 休眠3秒

time.sleep(3)
created_owner_id_id_index(client)
# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)

# 导入测试数据
importData(client)
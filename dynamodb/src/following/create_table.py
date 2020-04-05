import boto3
import json
import time

def create_table(client):
    client.create_table(
        TableName='following',
        KeySchema=[
            { 
                'AttributeName': 'userId', 
                'KeyType': 'HASH'
            },
            { 
                'AttributeName': 'followingId', 
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            { 
                'AttributeName': 'userId', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'followingId', 
                'AttributeType': 'S' 
            }
        ],
        ProvisionedThroughput={       
            'ReadCapacityUnits': 5, 
            'WriteCapacityUnits': 5
        }
    )


# 查询关注我的用户,按照时间倒序
def created_user_id_created_at_index(client):
    client.update_table(
        TableName='following',
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

# 查询我关注的用户,按照时间倒序
def created_following_id_created_at_index(client):
    client.update_table(
        TableName='following',
        AttributeDefinitions=[
            { 
                'AttributeName': 'followingId', 
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
                    'IndexName': 'followingId_createdAt',
                    'KeySchema': [
                        {'AttributeName': 'followingId', 'KeyType': 'HASH'},  
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
关注
user_id: 被关注的用户
following_id: 发起关注的用户
"""
def following(client,user_id,following_id):
    created_at = int(round(time.time() * 1000))
    item = {'userId':{'S':user_id},'followingId':{'S':following_id},'createdAt':{'N':str(created_at)}}
    client.put_item(TableName='following',Item=item)


def importData(client):
    for following_id in range(1,30):
        for user_id in range(1,30):
            if following_id==user_id:
                continue
            following(client,str(following_id),str(user_id))

 
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
    client.delete_table(TableName = 'following')
except :
    pass

create_table(client)
created_user_id_created_at_index(client)
# Dynamodb 有建时间限制 休眠3秒

time.sleep(3)
created_following_id_created_at_index(client)
# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)

# 导入测试数据
importData(client)
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
def created_id_rank_index(client):
    client.update_table(
        TableName='liking',
        AttributeDefinitions=[
            { 
                'AttributeName': 'id', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'rank', 
                'AttributeType': 'N' 
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'id_rank',
                    'KeySchema': [
                        {'AttributeName': 'id', 'KeyType': 'HASH'},  
                        {'AttributeName': 'rank', 'KeyType': 'RANGE'},
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
def created_user_id_rank_index(client):
    client.update_table(
        TableName='liking',
        AttributeDefinitions=[
            { 
                'AttributeName': 'userId', 
                'AttributeType': 'S'
            },
            { 
                'AttributeName': 'rank', 
                'AttributeType': 'N'
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'userId_rank',
                    'KeySchema': [
                        {'AttributeName': 'userId', 'KeyType': 'HASH'},  
                        {'AttributeName': 'rank', 'KeyType': 'RANGE'},
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
def created_owner_id_rank_index(client):
    client.update_table(
        TableName='liking',
        AttributeDefinitions=[
            { 
                'AttributeName': 'ownerId', 
                'AttributeType': 'S'
            },
            { 
                'AttributeName': 'rank', 
                'AttributeType': 'N' 
            }
        ],
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': 'ownerId_rank',
                    'KeySchema': [
                        {'AttributeName': 'ownerId', 'KeyType': 'HASH'},  
                        {'AttributeName': 'rank', 'KeyType': 'RANGE'},
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

def importData(client):
    for id in range(1,10):
        for user_id in range(1,100):
            liking(client,str(user_id),str(id),str(id))

    

"""
点赞
user_id: 点赞用户
owner_id: 作品所属用户
id:作品
"""
def liking(client,user_id, owner_id, id):
    # 使用时间戳代替rank,正式环境请使用snowflake算法生成有序rank
    rank = int(round(time.time() * 1000000))
    created_at = int(round(time.time() * 1000))

    item = {'userId':{'S':user_id},'rank':{'N':str(rank)},'id':{'S':id},'ownerId':{'S':owner_id},'createdAt':{'N':str(created_at)}}
    client.put_item(TableName='liking',Item=item)


"""
取消点赞
user_id: 点赞用户
id:作品
"""
def unliking(client,user_id , id):
    client.delete_item(
        Key={
            'userId': {
                'S': user_id,
            },
            'id': {
                'S': id,
            },
        },
        TableName='liking',
    )


# 查询点赞该作品的用户 按时间倒序
def query_by_id(client,id,size,lastEvaluatedKey):
    conditions = {
        'id':{
            'AttributeValueList':[
                {
                    'S': id
                }
            ],
            'ComparisonOperator': 'EQ'
        }
    }

    if lastEvaluatedKey!= None:
        return client.query(
                TableName='liking',
                IndexName='id_rank', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='liking',
        IndexName='id_rank',  #使用索引
        Limit=size,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False)
 

# 查询我点赞的作品 按时间倒序
def query_by_user_id(client,user_id,size,lastEvaluatedKey):
    conditions = {
        'userId':{
            'AttributeValueList':[
                {
                    'S': user_id
                }
            ],
            'ComparisonOperator': 'EQ'
        }
    }

    if lastEvaluatedKey!= None:
        return client.query(
                TableName='liking',
                IndexName='userId_rank', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='liking',
        IndexName='userId_rank',  #使用索引
        Limit=size,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False)

 
# 查询我被点赞的作品 按时间倒序
def query_by_owner_id(client,owner_id,size,lastEvaluatedKey):
    conditions = {
        'ownerId':{
            'AttributeValueList':[
                {
                    'S': owner_id
                }
            ],
            'ComparisonOperator': 'EQ'
        }
    }

    if lastEvaluatedKey!= None:
        return client.query(
                TableName='liking',
                IndexName='ownerId_rank', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='liking',
        IndexName='ownerId_rank',  #使用索引
        Limit=size,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False)
         

endpoint_url = "http://localhost:8000"
access_key = ""  # 本地Dynamodb不需要填写
secret_key = ""
region_name = "us-west-2"
client = boto3.client('dynamodb',
                          endpoint_url=endpoint_url,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region_name,)

# table = client.delete_table(TableName = 'liking')

create_table(client)
created_id_rank_index(client)
# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)
created_user_id_rank_index(client)

# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)
created_owner_id_rank_index(client)

# Dynamodb 有建时间限制 休眠3秒
time.sleep(3)

# 导入测试数据
importData(client)

# 拉取点赞作品的用户
response = query_by_id(client,'1',20,None)

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

# 拉取我点赞的作品
response = query_by_user_id(client,'1',20,None)

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_user_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))


#拉取 我被点赞的作品
response = query_by_owner_id(client,'1',20,None)
#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_owner_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

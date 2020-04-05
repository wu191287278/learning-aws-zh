import boto3
import json
import time



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
                IndexName='id_createdAt', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='liking',
        IndexName='id_createdAt',  #使用索引
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
        IndexName='userId_createdAt',  #使用索引
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
                IndexName='ownerId_createdAt', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='liking',
        IndexName='ownerId_createdAt',  #使用索引
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


# 拉取点赞作品的用户
response = query_by_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

# 拉取我点赞的作品
response = query_by_user_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_user_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))


#拉取 我被点赞的作品
response = query_by_owner_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))
#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_owner_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

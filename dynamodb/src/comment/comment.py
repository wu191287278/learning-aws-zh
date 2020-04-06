import boto3
import json
import time



"""
评论
object_id 作品ID
user_id: 评论用户
owner_id: 作品拥有者
"""
def comment(client,object_id,user_id,owner_id,content):
    # 使用纳秒作为id,线上请使用snowflack算法进行生成有序id
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


"""
删除评论
id: 评论ID
object_id: 作品ID
"""
def delete(client,id, object_id):
    client.delete_item(
        Key={
            'userId': {
                'N': id,
            },
            'id': {
                'S': object_id,
            },
        },
        TableName='comment',
    )

"""
查询评论作品的用户 按id倒序
object_id: 作品ID
size: 数量
lastEvaluatedKey: 游标
"""
def query_by_object_id(client,object_id,size,lastEvaluatedKey):
    conditions = {
        'objectId':{
            'AttributeValueList':[
                {
                    'S': object_id
                }
            ],
            'ComparisonOperator': 'EQ'
        }
    }

    if lastEvaluatedKey!= None:
        return client.query(
                TableName='comment',
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='comment',
        Limit=size,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False)
 

"""
查询我评论的作品 按id倒序
user_id: 用户ID
size: 数量
lastEvaluatedKey: 游标
"""
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
                TableName='comment',
                IndexName='userId_id', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='comment',
        IndexName='userId_id',  #使用索引
        Limit=size,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False)
 

"""
查询我被评论的作品 按时间倒序
owner_id: 作品拥有者
size: 数量
lastEvaluatedKey: 游标
"""
def query_by_owner_id_id(client,owner_id,size,lastEvaluatedKey):
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
                TableName='comment',
                IndexName='ownerId_id', #使用索引
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='comment',
        IndexName='ownerId_id',  #使用索引
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


# 查询评论作品的用户
response = query_by_object_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_object_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))


# 查询我评论的作品
response = query_by_user_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_user_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

# 查询评论我的作品用户
response = query_by_owner_id_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_owner_id_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

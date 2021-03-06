## Dynamodb实现点赞系统

### 介绍

点赞在社交类平台中，作为一个最常见的操作，每天会有成千上万的操作。如果每次都将操作写入数据库，那么对于数据库会形成很大的操作负担。本文介绍如何通过Dynamodb构建一个点赞系统。

### 为什么选择Dynamodb

1. 吞吐量和存储空间几乎无限
2. 可自动纵向扩展和缩减表
3. 价格低廉
4. 天然支持排序
5. 支持游标分页,适合下拉内容
6. 每天可处理超过 10 万亿个请求，并可支持每秒超过 2000 万个请求的峰值

### 架构图
![image](./images/Dynamodb实现点赞系统/1.jpg)

#### 表结构设计

|名称|类型|说明|
|---|---|---|
|userId|String|点赞用户ID HashKey|
|id|String|作品ID RangeKey|
|ownerId|String|作品拥有者|
|createdAt|Number|点赞时间戳|

#### 点赞的用户索引(id_createdAt)

> 查询点赞作品的用户,按照时间倒序

|名称|说明|
|---|---|
|id|HashKey 分区键|
|createdAt|RangeKey 排序键|

![image](./images/Dynamodb实现点赞系统/4.jpg)


#### 我点赞的作品索引(userId_createdAt)

> 查询我点赞的作品,按照时间倒序

|名称|说明|
|---|---|
|userId|HashKey 分区键|
|createdAt|RangeKey 排序键|

![image](./images/Dynamodb实现点赞系统/2.jpg)



#### 我的被点赞作品索引(ownerId_createdAt)

> 查询我的被点赞作品列表,按照时间倒序

|名称|说明|
|---|---|
|ownerId|HashKey 分区键|
|createdAt|RangeKey 排序键|


![image](./images/Dynamodb实现点赞系统/3.jpg)


#### 启动一个本地的Dynamodb

```
docker run -d -p 8000:8000 ryanratcliff/dynamodb
```

#### 安装依赖包

```
pip install boto3
```

#### 创建表
```
def create_table(client):
    client.create_table(
        TableName='liking',
        KeySchema=[
            { 
                'AttributeName': 'userId', 
                'KeyType': 'HASH'
            },
            { 
                'AttributeName': 'id', 
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            { 
                'AttributeName': 'userId', 
                'AttributeType': 'S' 
            },
            { 
                'AttributeName': 'id', 
                'AttributeType': 'S' 
            }
        ],
        ProvisionedThroughput={       
            'ReadCapacityUnits': 5, 
            'WriteCapacityUnits': 5
        }
    )
```


#### 创建索引(id_createdAt) 用于查询谁点赞了该作品
```
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

```


#### 创建索引(userId_createdAt) 用于查询我点赞的作品
```
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
```


#### 创建索引(ownerId_createdAt) 用于查询我被点赞的作品
```
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

```

#### 点赞
```
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

```

#### 取消点赞
```

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

```

#### 写入测试数据

```

def importData(client):
    for id in range(1,10):
        for user_id in range(1,100):
            if user_id==id:
                continue
            liking(client,str(user_id),str(id),str(id))
```


#### 查询点赞该作品的用户 按时间倒序

```
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

```


#### 查询我点赞的作品 按时间倒序

```
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
                IndexName='userId_createdAt', #使用索引
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

```


#### 查询我被点赞的作品 按时间倒序

```
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
```

#### 主函数
```
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

# 模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

# 拉取我点赞的作品
response = query_by_user_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

# 模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_user_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))


# 拉取 我被点赞的作品
response = query_by_owner_id(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#模拟用户不断下拉数据,使用LastEvaluatedKey游标
while 'LastEvaluatedKey' in response:
    response = query_by_owner_id(client,'1',20,response['LastEvaluatedKey'])
    print(json.dumps(response["Items"],indent=4))

```

#### 完整代码

* [创建表](./src/liking/create_table.py)
* [Liking](./src/liking/liking.py)
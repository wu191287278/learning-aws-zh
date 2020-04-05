## Dynamodb实现Feed流系统

### 介绍

评论在社交类平台中，作为一个最常见的操作，每天会有成千上万的操作。如果每次都将操作写入数据库，那么对于数据库会形成很大的操作负担。本文介绍如何通过Dynamodb构建一个评论系统。


### 为什么选择Dynamodb

1. 存储扩展,无需考虑扩容问题
2. 读取扩展,无需考虑扩容问题
3. 价格低廉
4. 天然支持排序
5. 支持游标分页,适合下拉内容

### 常见的评论系统

#### 楼中楼模式

每条评论占一楼，针对该评论的所有回复都在该楼里展现，比如百度贴吧、简书的评论系统

![image](./images/Dynamodb实现评论系统/1.jpg)

优势：回复评论的内容集中展现，易于了解评论引发的对话。
劣势：内容过多时需要做分页处理，较为复杂。


#### 流模式(本文将采用的模式)

展现形式类似于信息流，不管是评论还是回复，每条信息都占一层，比如laravel-china社区的评论系统。

![image](./images/Dynamodb实现评论系统/2.jpg)

优势： 逻辑简单，实现较为容易
劣势： 对话内容不能集中呈现，不便于了解对话内容。


#### 引用模式

引用模式与流模式相似，只是回复的内容发布时会带上引用的内容。

![image](./images/Dynamodb实现评论系统/3.jpg)

优势：可以理解回复针对的是哪条评论，有助于了解对话内容。实现相对容易。
劣势：与流模式相似，不能完整呈现整个对话内容。
通过分析优劣势可以发现，引用模式是介于楼中楼以及流模式之间的一个折中方案。



#### 表结构设计

|名称|类型|说明|
|---|---|---|
|id|String|userId+"_"+followingId 组成唯一键|
|userId|String|用户ID|
|followingId|String|关注我的用户ID|
|createdAt|Number|关注时间|

#### 关注我的用户索引 userId_createdAt

> 查询关注我的用户,按照时间倒序

|名称|说明|
|---|---|
|userId|HashKey 分区键|
|createdAt|RangeKey 排序键|


#### 我关注的用户索引 following_createdAt

> 查询我关注的用户,按照时间倒序

|名称|说明|
|---|---|
|following|HashKey 分区键|
|createdAt|RangeKey 排序键|


### 启动一个本地的Dynamodb

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
                'AttributeName': "id", 
                'KeyType': "HASH"
            }
        ],
        AttributeDefinitions=[
            { 
                'AttributeName': "userId", 
                'AttributeType': "S" 
            }
        ],
        ProvisionedThroughput={       
            'ReadCapacityUnits': 5, 
            'WriteCapacityUnits': 5
        }
    )
```


#### 创建索引
```
def created_index(client):
    client.update_table(
        TableName='liking',
        GlobalSecondaryIndexUpdates=[
            {
                'Create': {
                    'IndexName': "objectId_createdAt",
                    'KeySchema': [
                        {'AttributeName': "objectId", 'KeyType': "HASH"},  
                        {'AttributeName': "createdAt", 'KeyType': "RANGE"},
                    ],
                    'Projection': {
                        "ProjectionType": "ALL"
                    },
                    'ProvisionedThroughput': {
                        "ReadCapacityUnits": 10,
                        "WriteCapacityUnits": 10
                    }
                }
            },
            {
                'Create': {
                    'IndexName': "userId_createdAt",
                    'KeySchema': [
                        {'AttributeName': "userId", 'KeyType': "HASH"},  
                        {'AttributeName': "createdAt", 'KeyType': "RANGE"},
                    ],
                    'Projection': {
                        "ProjectionType": "ALL"
                    },
                    'ProvisionedThroughput': {
                        "ReadCapacityUnits": 10,
                        "WriteCapacityUnits": 10
                    }
                }
            }
        ]
    )
)
```

#### 写入测试数据

```
def importData(client):
    # 使用时间戳代替rank,正式环境请使用snowflake算法生成有序rank
    for i in range(100):
        created_at = int(round(time.time() * 1000))
        rank = int(round(time.time() * 1000000))
        item = {'userId':{'S':'1'},'rank':{'N':str(rank)},'id':{'N':str(i)},'kind':{'S':'photo'},'createdAt':{'N':str(created_at)}}
        client.put_item(TableName='home_feed',Item=item)
```

#### 拉取用户瀑布流数据

```
def query(client,user_id,size,lastEvaluatedKey):
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
                TableName='home_feed',
                Limit=size,
                KeyConditions=conditions,
                ConsistentRead=False,
                ScanIndexForward=False,
                ExclusiveStartKey=lastEvaluatedKey)

    return client.query(
        TableName='home_feed',
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
create_table(client)
importData(client)

response = query(client,'1',20,None)
print(json.dumps(response["Items"],indent=4))

#下一页数据,不断的把LastEvaluatedKey进行传递模拟用户下拉数据
response = query(client,'1',20,response['LastEvaluatedKey'])
print(json.dumps(response["Items"],indent=4))
```

#### 完整代码

* [HomeFeed](./src/home_feed.py)
* [Gorilla-Websocket](https://github.com/gorilla/websocket)
* [Vert.x](https://vertx.io/docs/)
## Dynamodb实现Feed流系统

### 什么是Feed流

在互联网领域，尤其现在的移动互联网时代，Feed流产品非常常见。例如我们每天都会用到的朋友圈、微博就是一种非常典型的Feed流产品，图片分享网站Pinterest、花瓣网等又是另一种形式的Feed流产品。除此之外，很多应用的都会有一个模块，有些叫动态、有些叫消息广场，这些也是Feed流产品。Feed流产品已经被广泛应用在各种主流应用中。

### 基础概念

|概念|描述|
|---|---|
|Feed|Feed流中的每一条状态或者消息都是Feed，例如朋友圈中的一个状态就是一个Feed、微博中的一条微博就是一个Feed。|
|Feed流|持续更新并呈现给用户内容的信息流。每个人的朋友圈、微博关注页等都是一个Feed流。|
|Timeline|Timeline是一种Feed流的类型，微博、朋友圈都是Timeline类型的Feed流。但是由于Timeline类型出现最早、使用最广泛、最为人熟知，有时也用||Timeline来表示Feed流。|
|关注页Timeline|展示其他人Feed消息的页面，例如朋友圈、微博的首页。|
|个人页Timeline|展示自己发送过的Feed消息的页面，例如微信中的相册、微博的个人页。|

### 为什么选择Dynamodb

1. 存储扩展,无需考虑扩容问题
2. 读取扩展,无需考虑扩容问题
3. 价格低廉
4. 天然支持排序
5. 支持游标分页,特别适合下拉内容


#### 表结构设计

|名称|类型|说明|
|---|---|---|
|userId|String|分区键 HashKey，用户的消息存放在相同的分区查询时|
|rank|Number|排序键 SortKey 可以使用Snowflake 算法生成,让数据保证有序,同时保证唯一性|
|id|String|业务ID|
|kind|String|业务类型|
|createdAt|Number|创建时间,用时间戳表示|

#### 安装依赖包

```
pip install boto3
```

#### 创建表
```
def create_table(client):
    client.create_table(
        TableName='home_feed',
        KeySchema=[
            { 
                'AttributeName': "userId", 
                'KeyType': "HASH"
            },
            { 
                'AttributeName': "rank", 
                'KeyType': "RANGE"
            }
        ],
        AttributeDefinitions=[
            { 
                'AttributeName': "userId", 
                'AttributeType': "S" 
            },
            { 
                'AttributeName': "rank", 
                'AttributeType': "N" 
            }
        ],
        ProvisionedThroughput={       
            'ReadCapacityUnits': 5, 
            'WriteCapacityUnits': 5
        }
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
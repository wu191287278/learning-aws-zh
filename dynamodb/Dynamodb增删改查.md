## Dynamodb 增删改查

#### 初始化客户端

```
import boto3
import json

endpoint_url = "http://localhost:8000"
access_key = ""  # 本地Dynamodb不需要填写
secret_key = ""
region_name = "us-west-2"
client = boto3.client('dynamodb',
                          endpoint_url=endpoint_url,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region_name,)
```

#### 创建测试表
```
 table = client.create_table(
    TableName='Music',
    KeySchema=[
        { 
            'AttributeName': "Artist", 
            'KeyType': "HASH"
        },
        { 
            'AttributeName': "SongTitle", 
            'KeyType': "RANGE"
        }
    ],
    AttributeDefinitions=[
        { 
            'AttributeName': "Artist", 
            'AttributeType': "S" 
        },
        { 
            'AttributeName': "SongTitle", 
            'AttributeType': "S" 
        }
    ],
    ProvisionedThroughput={       
        'ReadCapacityUnits': 5, 
        'WriteCapacityUnits': 5
    }
)

```


#### 单条插入

```
item = {'Artist':{'S':'Andrew Lloyd Webber'},'SongTitle':{'S':'The Phantom Of the Opera'}}

client.put_item(TableName='Music',Item=item)
```

#### 删除

```
client.delete_item(
    Key={
        'Artist': {
            'S': 'Andrew Lloyd Webber',
        },
        'SongTitle': {
            'S': 'The Phantom Of the Opera',
        },
    },
    TableName='Music',
)
```

#### 批量写入
> BatchWriteItem操作在一个或多个表中放入或删除多个项。对BatchWriteItem的单个调用可以写入高达16MB的数据，其中可以包含多达25个put或delete请求。要写入的单个项可能高达400kb。

```
response = client.batch_write_item(
    RequestItems={
        'Music': [
            {
                'PutRequest': {
                    'Item': {
                        'Artist': {
                            'S': 'No One You Know',
                        },
                        'SongTitle': {
                            'S': 'Call Me Today',
                        },
                    },
                },
            },
            {
                'PutRequest': {
                    'Item': {
                        'Artist': {
                            'S': 'Acme Band',
                        },
                        'SongTitle': {
                            'S': 'Happy Day',
                        },
                    },
                },
            },
            {
                'PutRequest': {
                    'Item': {
                        'Artist': {
                            'S': 'No One You Know',
                        },
                        'SongTitle': {
                            'S': 'Scared of My Shadow',
                        },
                    },
                },
            },
        ],
    },
)

print(response)

```

### 扫描表数据(全表扫描)

```
# 每次取1000条
limit = 1000
response = client.scan( TableName='Music', Limit=limit)
print(response)
```

### 分页查询
```
conditions = {
    'Artist':{
        'AttributeValueList':[
            {
                'S': 'No One You Know'
            }
        ],
        'ComparisonOperator': 'EQ'
    }
}


response = client.query(
        TableName='Music',
        Limit=1,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False)
print(response)        
response = client.query(
        TableName='Music',
        Limit=1,
        KeyConditions=conditions,
        ConsistentRead=False,
        ScanIndexForward=False,
        ExclusiveStartKey=response['LastEvaluatedKey'])     
print(response)        

```


### 特定于 API 的限制

#### CreateTable/UpdateTable/DeleteTable

通常，您同时可以运行多达 10 个 CreateTable、UpdateTable 和 DeleteTable 请求（任一组合）。也就是说，处于 CREATING、UPDATING 或 DELETING 状态的表的总数不能超过 50 个。

唯一例外是在创建含有一个或多个二级索引的表时。您可以一次运行最多 25 个这种请求。不过，如果表或索引指定很复杂，则 DynamoDB 可能会暂时降低并发操作的数量。

#### BatchGetItem

一个 BatchGetItem 操作最多可以检索 100 个项目。检索到的所有项目总大小不能超过 16 MB。

#### BatchWriteItem

一个 BatchWriteItem 操作最多可包含 25 个 PutItem 或 DeleteItem 请求。写入的所有项目总大小不能超过 16 MB。

DescribeTableReplicaAutoScaling
DescribeTableReplicaAutoScaling 方法每秒仅支持 10 个请求。

#### DescribeLimits

DescribeLimits 只应定期调用。如果您在一分钟内多次调用它，则可能遇到限制错误。

#### DescribeContributorInsights/ListContributorInsights/UpdateContributorInsights

DescribeContributorInsights、ListContributorInsights 和 UpdateContributorInsights 只应定期调用。对于这些 API 中的每一个，DynamoDB 每秒最多支持五个请求。

#### Query

来自 Query 的结果集大小上限为每个调用 1 MB。您可以使用查询响应中的 LastEvaluatedKey 检索更多结果。

#### Scan

来自 Scan 的结果集大小上限为每个调用 1 MB。您可以使用扫描响应中的 LastEvaluatedKey 检索更多结果。

#### UpdateTableReplicaAutoScaling

UpdateTableReplicaAutoScaling 方法每秒仅支持 10 个请求。

## 参考文档

* [Dynamodb官方文档](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)

* [Dynamodb中的限制](https://docs.aws.amazon.com/zh_cn/amazondynamodb/latest/developerguide/Limits.html#default-limits-throughput-capacity-modes)
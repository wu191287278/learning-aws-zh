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
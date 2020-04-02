### 什么是 Amazon DynamoDB

Amazon DynamoDB 是一种完全托管的 NoSQL 数据库服务，提供快速而可预测的性能，能够实现无缝扩展。使用 DynamoDB，您可以免除操作和扩展分布式数据库的管理工作负担，因而无需担心硬件预置、设置和配置、复制、软件修补或集群扩展等问题。

使用 DynamoDB，您可以创建数据库表来存储和检索任意量级的数据，并提供任意级别的请求流量。您可以扩展或缩减您的表的吞吐容量，而不会导致停机或性能下降，还可以使用 AWS 管理控制台来监控资源使用情况和各种性能指标。

### Amazon DynamoDB 特点

DynamoDB 会自动将数据和流量分散到足够数量的服务器上，以满足吞吐量和存储需求，同时保持始终如一的高性能。所有数据均存储在固态硬盘 (SSD) 中，并会自动复制到 AWS 区域中的多个可用区中，从而提供内置的高可用性和数据持久性。

DynamoDB 是 NoSQL 数据库并且无架构，这意味着，与主键属性不同，无需在创建表时定义任何属性或数据类型。与此相对，关系数据库要求在创建表时定义每个列的名称和数据类型。


### 启动一个本地的Dynamodb

```
docker run -d -p 8000:8000 ryanratcliff/dynamodb
```


### Python 操作 DynamoDB

#### 安装依赖包

```
pip install boto3
```

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
                          region_name=region_name,),
```

#### 创建表
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

#### 修改表
```
table = client.update_table(
    TableName='Music',
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
        'ReadCapacityUnits': 10, 
        'WriteCapacityUnits': 10
    }
)

client.describe_table(TableName='Music')
```

#### 创建索引
```
table = client.update_table(
    TableName='Music',
    AttributeDefinitions=[
        { 
            'AttributeName': "Genre", 
            'AttributeType': "S" 
        },
        { 
            'AttributeName': "Price", 
            'AttributeType': "N" 
        }
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create': {
                'IndexName': "GenreAndPriceIndex",
                'KeySchema': [
                    {'AttributeName': "Genre", 'KeyType': "HASH"},  # Partition key
                    {'AttributeName': "Price", 'KeyType': "RANGE"}, # Sort key
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

client.describe_table(TableName='Music')
```



#### 获取表信息
```
client.describe_table(TableName='Music')
```

#### 列出所有表

```
tables = client.list_tables()
print(json.dumps(tables))
```

```
{"TableNames": ["Music"], "ResponseMetadata": {"RequestId": "c2473363-433d-4037-8a0e-d103a01a61b5", "HTTPStatusCode": 200, "HTTPHeaders": {"content-type": "application/x-amz-json-1.0", "x-amz-crc32": "2248451684", "x-amzn-requestid": "c2473363-433d-4037-8a0e-d103a01a61b5", "content-length": "100", "server": "Jetty(8.1.12.v20130726)"}, "RetryAttempts": 0}}
```

#### 删除表
```
table = client.Table('Music')
table.delete()
```


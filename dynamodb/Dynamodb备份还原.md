
## Dynamodb 备份还原

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

#### 写入测试数据
> BatchWriteItem操作在一个或多个表中放入或删除多个项。对BatchWriteItem的单个调用可以写入高达16MB的数据，其中可以包含多达25个put或delete请求。要写入的单个项可能高达400kb。

```
table = 'Music'
batch_size = 25
items = []
for i in range(1000):
    item = {
                'Artist': {
                    'S': 'No One You Know'+str(i),
                },
                'SongTitle': {
                    'S': 'Call Me Today'+str(i),
                }
            }
    putRequest = {'PutRequest' : {'Item':item} }
    items.append(putRequest)
    if i % batch_size == 0 and len(items) != 0:
        response = client.batch_write_item(RequestItems={table:items})
        items=[]

if len(items) != 0:
    response = client.batch_write_item(RequestItems={table:items})

```

### 导出数据

```
# 每次取100条,正式环境可以1000或更大
table = 'Music'
limit = 100
fp = open( './backup.json','w') 
counter = 0
response = client.scan(TableName=table, Limit=limit)

while 'LastEvaluatedKey' in response :
    for item in response["Items"]:
        counter = counter+1
        fp.writelines(json.dumps(item)+"\r\n")        
    # 携带游标再次扫描
    response = client.scan(TableName=table,Limit=limit,ExclusiveStartKey = response['LastEvaluatedKey'])

for item in response['Items']:
    counter = counter+1
    fp.writelines(json.dumps(item)+"\r\n")        

fp.close()
print("导出:"+str(counter)+"数据")
```


### 还原数据

#### 数据打散

> 参考文档 [高效的写入数据](https://docs.aws.amazon.com/zh_cn/amazondynamodb/latest/developerguide/bp-partition-key-data-upload.html)

> Dynamodb 是按照分区导出，导致写入时都是往一个分区写,容易造成分区热点。为了加快速度 把数据打散

```
cat ./backup.json|sort|uniq >uniq.json
```

> 或者切分文件,每个进程对应一个文件

```
split -l 100000 buckup.json -d -a 3 backup_
```


#### 导入数据
```
table = 'Music'
batch_size = 25
counter = 0
fp = open( './uniq.json','r') 
items = []
for line in fp:
    item = json.loads(line)
    putRequest = {'PutRequest' : {'Item':item} }
    items.append(putRequest)
    counter = counter+1
    if counter % batch_size == 0:
        response = client.batch_write_item(RequestItems={table:items})
        items=[]

if len(items) != 0:
    response = client.batch_write_item(RequestItems={table:items})
    counter = counter+len(items)

fp.close()
print("导入"+str(counter)+" 条数据")
```

### 完整代码
[Backup](./src/backup.py)
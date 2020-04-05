## Dynamodb触发器

### 开通Dynamodb Stream 流服务

![image](./images/Dynamodb触发器/1.jpg)
![image](./images/Dynamodb触发器/2.jpg)
![image](./images/Dynamodb触发器/3.jpg)
![image](./images/Dynamodb触发器/4.jpg)

### 快速开始

```
import json

def handler(event, context):
    for record in event["Records"]:
        dynamodb = record["dynamodb"]
        eventName = record["eventName"]
        tableName = record["eventSourceARN"].split("/")[1]
        print(record)
```


### 将变更的数据发送到消息队列

```
import json

# 消息队列名称
STREAM_NAME = "data-dist"
kinesis = boto3.client('kinesis')

def handler(event, context):
    for record in event["Records"]:
        dynamodb = record["dynamodb"]
        eventName = record["eventName"]
        tableName = record["eventSourceARN"].split("/")[1]
        kinesis.put_record(StreamName=STREAM_NAME, Data=json.dumps(dynamodb))

```


#### 流费用计算

每个变更的数据将消耗1个读单位,lambda费用另算

#### 启用了流的表的最大写入容量

每个表 – 40000 个写入容量单位


### 参考文档

* [官方文档](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html)
import boto3
import json
import time


def create_test_table(client,table):
  client.create_table(
    TableName=table,
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

def import_test_data(client,table):
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
            client.batch_write_item(RequestItems={table:items})
            items=[]

    if len(items) != 0:
        client.batch_write_item(RequestItems={table:items})

def write(response,fp,counter):
    itemCount = len(response["Items"])

    if itemCount==0:
        return counter
        
    for item in response["Items"]:
        fp.writelines(json.dumps(item)+"\r\n")    

    counter = counter+itemCount
    print("已经导出:"+str(counter)+"数据")
    return counter

def buckup(client,table,path):
    # 每次取100条,正式环境可以1000或更大
    limit = 100
    fp = open( path,'w') 
    counter = 0
    response = client.scan(TableName=table, Limit=limit)
    counter = write(response,fp,counter)

    while 'LastEvaluatedKey' in response :
        # 携带游标再次扫描
        try:
            response = client.scan(TableName=table,Limit=limit,ExclusiveStartKey = response['LastEvaluatedKey'])
        except Exception as e:
            print("重新尝试:%s",e)
            # 休眠1秒重新尝试
            time.sleep(1)
            continue
        
        counter=write(response,fp,counter)
        
    counter = write(response,fp,counter)
    fp.close()
    print("共导出:"+str(counter)+"数据")


def restore(client,table,path):
    batch_size = 25
    counter = 0
    fp = open( path,'r') 
    items = []
    for line in fp:
        item = json.loads(line)
        putRequest = {'PutRequest' : {'Item':item} }
        items.append(putRequest)
        counter = counter+1
        if counter % batch_size == 0:
            client.batch_write_item(RequestItems={table:items})
            items=[]
            print("导入"+str(counter)+" 条数据")

    if len(items) != 0:
        client.batch_write_item(RequestItems={table:items})
        counter = counter+len(items)

    fp.close()
    print("共导入"+str(counter)+" 条数据")


endpoint_url = "http://localhost:8000"
access_key = ""  # 本地Dynamodb不需要填写
secret_key = ""
region_name = "us-west-2"
client = boto3.client('dynamodb',
                          endpoint_url=endpoint_url,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region_name,)
table = "Music"
path ="./backup.json"
client.delete_table(TableName=table)
create_test_table(client,table)
import_test_data(client,table)
buckup(client,table,path)
restore(client,table,path)
                         
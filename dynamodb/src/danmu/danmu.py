from flask import Flask, render_template,request
from flask_socketio import SocketIO
import time
import random
import json
import boto3

app = Flask(__name__,static_folder='./static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

client = boto3.client('dynamodb',
                          endpoint_url="http://localhost:8000",
                          aws_access_key_id="",
                          aws_secret_access_key="",
                          region_name="us-west-2",)

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/1.mp4')
def play():
    return app.send_static_file('1.mp4')

"""
curl "http://localhost:5000/danmu/send" -H 'Content-Type:application/json' --data-binary '{"objectId":"1","userId":"1","ownerId":"1","content":{ "text":"haha" ,"color":"yellow","size":"40px","position":1,"time":14}}'
"""
@app.route('/danmu/send',methods=['POST'])
def send():
    body = request.get_json()

    body['id'] = generate_id(body['content']['time'])

    body['createdAt']=int(time.time()*1000)
    
    item = encode(body)
    client.put_item(TableName='danmu',Item=item)
    # 发送给正在观看这个视频的用户
    socketio.emit('message', body, namespace='/video/'+body["objectId"])
    return body


"""
根据当前播放时间查询弹幕,用于拖拽,暂停 按id正序 curl http://localhost:5000/danmu/queryByTime/1
object_id: 作品ID
size: 数量
cursor: 游标
"""
@app.route('/danmu/queryByTime/<object_id>',methods=['GET'])
def query_by_time(object_id):
    size = int(request.args.get('size','20'))
    playing_time = float(request.args.get('playingTime','1'))
    conditions = {
        'objectId':{
            'AttributeValueList':[
                {
                    'S': object_id
                }
            ],
            'ComparisonOperator': 'EQ'
        },
        "id":{
            'AttributeValueList':[
                {
                    'N': str(generate_id(playing_time)) # 大于或等于客户端播放时间的弹幕
                }
            ],
            'ComparisonOperator': 'GT'
        }
    }

    query_result = client.query(
            TableName='danmu',
            Limit=size,
            KeyConditions=conditions,
            ConsistentRead=False,
            ScanIndexForward=True) # 按照ID正序排列

    data= []
    items = query_result['Items']
    for item in items:
        data.append(decode(item))
        
    # 查看是否还有下一页,如果有下一页 把游标返回给客户端使用
    if 'LastEvaluatedKey' in query_result:
        cursor = query_result['LastEvaluatedKey']['id']['N']
    else :
        # 没有游标 直接返回-1
        cursor = '-1'    
    return {'data':data,'cursor':cursor}



"""
根据游标拉取弹幕 按id正序 curl http://localhost:5000/danmu/pull/1
object_id: 作品ID
size: 数量
cursor: 游标
"""
@app.route('/danmu/pull/<object_id>',methods=['GET'])
def pull(object_id):
    cursor = request.args.get('cursor')
    
    # 如果没有游标,直接按照时间查询
    if(cursor==None):
        return query_by_time(object_id)
    size = int(request.args.get('size','20'))
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

    query_result = client.query(
            TableName='danmu',
            Limit=size,
            KeyConditions=conditions,
            ConsistentRead=False,
            ScanIndexForward=True, # 按照ID正序排列
            ExclusiveStartKey={'objectId':{'S':object_id},'id':{"N":cursor}})
    data= []
    items = query_result['Items']
    for item in items:
        data.append(decode(item))
        
    # 查看是否还有下一页,如果有下一页 把游标返回给客户端使用
    if 'LastEvaluatedKey' in query_result:
        cursor = query_result['LastEvaluatedKey']['id']['N']
    else :
        # 没有游标 直接返回-1
        cursor = '-1'    
    return {'data':data,'cursor':cursor}


"""
生成唯一有序ID
int(当前播放时间字符串+当前时间戳字符串+一个随机数字符串)
"""
def generate_id(playing_time):
   return int(str(int(playing_time)) + str(int(time.time()*1000))+ str(random.randint(0,9)))

def encode(item):
    id = item['id']
    object_id = item['objectId']
    user_id = item['userId']
    owner_id = item['ownerId']
    content = item['content']
    created_at = item['createdAt']

    return {
            'id':{'N':str(id)},
            'objectId':{'S':object_id},
            'userId':{'S':user_id},
            'ownerId':{'S':owner_id},
            'content':{'S':json.dumps(content)},
            'createdAt':{'N':str(created_at)}
           }

def decode(item):
    m = {}
    m['id'] = int(item['id']['N'])
    m['objectId'] = item['objectId']['S']
    m['userId'] = item['userId']['S']
    m['ownerId'] = item['ownerId']['S']
    m['content'] = json.loads(item['content']['S'])
    m['createdAt'] = int(item['createdAt']['N'])
    return m


    
if __name__ == '__main__':
    socketio.run(app)
    
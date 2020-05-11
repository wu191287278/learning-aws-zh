## ElasticSearch 入门

### 概述

Elasticsearch 是一个分布式的开源搜索和分析引擎，适用于所有类型的数据，包括文本、数字、地理空间、结构化和非结构化数据。

### ElasticSearch 可以做什么

Elasticsearch 在速度和可扩展性方面都表现出色，而且还能够索引多种类型的内容，这意味着其可用于多种用例：

* 应用程序搜索
* 网站搜索
* 企业搜索
* 日志处理和分析
* 基础设施指标和容器监测
* 应用程序性能监测
* 地理空间数据分析和可视化
* 安全分析
* 业务分析

### 安装


Windows

```
curl -o elasticsearch-7.6.2.zip https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-windows-x86_64.zip
unzip elasticsearch-7.6.2.zip
```

Linux

```
curl -o elasticsearch-7.6.2.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-linux-x86_64.tar.gz

tar -zxvf elasticsearch-7.6.2.tar.gz
```

Mac

```
curl -o elasticsearch-7.6.2.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-darwin-x86_64.tar.gz

tar -zxvf elasticsearch-7.6.2.tar.gz
```

#### 启动ElasticSearch

```
cd elasticsearch-7.6.2
./bin/elasticsearch
```

#### 后台启动
```
./bin/elasticsearch -d
```

#### 查看ElasticSearch 信息
```
curl localhost:9200

{
  "name" : "local",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "QrmMWfoPRcmQH2wmSVeIqg",
  "version" : {
    "number" : "7.6.2",
    "build_flavor" : "default",
    "build_type" : "tar",
    "build_hash" : "ef48eb35cf30adf4db14086e8aabd07ef6fb113f",
    "build_date" : "2020-03-26T06:34:37.794943Z",
    "build_snapshot" : false,
    "lucene_version" : "8.4.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

### 基本概念

#### Node 与 Cluster

```
Elastic 本质上是一个分布式数据库，允许多台服务器协同工作，每台服务器可以运行多个 Elastic 实例。

单个 Elastic 实例称为一个节点（node）。一组节点构成一个集群（cluster）。
```

#### Index


Elastic 会索引所有字段，经过处理后写入一个反向索引（Inverted Index）。查找数据的时候，直接查找该索引。

所以，Elastic 数据管理的顶层单位就叫做 Index（索引）。它是单个数据库的同义词。每个 Index （即数据库）的名字必须是小写。

下面的命令可以查看当前节点的所有 Index。

```
curl -X GET 'http://localhost:9200/_cat/indices?v'
```

#### Document

Index 里面单条的记录称为 Document（文档）。许多条 Document 构成了一个 Index。

Document 使用 JSON 格式表示，下面是一个例子。

同一个 Index 里面的 Document，不要求有相同的结构（scheme），但是最好保持相同，这样有利于提高搜索效率。
```
{
  "country": "中国",
  "province": "北京",
  "city": "北京"
}
```

#### Type 

6.0以上版本已经废弃

#### 数据类型

字符串

* text:⽤于全⽂索引，该类型的字段将通过分词器进⾏分词
* keyword:不分词，只能搜索该字段的完整的值

数值型

* long, integer, short, byte, double, float, half_float, scaled_float

* 布尔 - boolean
* ⼆进制 - binary:该类型的字段把值当做经过 base64 编码的字符串，默认不存储，且不可搜索

范围类型 范围类型表示值是⼀个范围，⽽不是⼀个具体的值

* integer_range, float_range, long_range, double_range, date_range 譬如 age 的类型是 integer_range，那么值可以是 {“gte” : 20, “lte” : 40}；搜索 “term” :{“age”: 21} 可以搜索该值

⽇期 - date
* 由于Json没有date类型，所以es通过识别字符串是否符合format定义的格式来判断是否为date类型format默认为：strict_date_optional_time||epoch_millis
格式:“2022-01-01” “2022/01/01 12:10:30” 这种字符串格式,从开始纪元（1970年1⽉1⽇0点） 开始的毫秒数,从开始纪元开始的秒数
示例

地理位置类型

* geo_point

#### 新建Index

```
curl -X PUT -H 'Content-Type:application/json' 'localhost:9200/conv19' -d '
{
  "mappings": {
    "properties": {
      "country": {
        "type": "keyword"
      },
      "province": {
        "type": "keyword"
      },
      "location": {
        "type": "geo_point"
      },
      "count":{
        "type":"integer"
      },
      "createdAt": {
        "type": "date",
        "format": "yyyy-MM-dd'T'HH:mm:ss"
      }
    }
  },
  "settings": {
    "index": {
      "number_of_shards": "1",
      "number_of_replicas": "0"
    }
  }
}'
```

* number_of_shards 分片数量 一般建议是20-40g一个分片,分片决定了查询时并行线程数量.

* number_of_replicas 副本数量, 冗余的副本 可以提高查询速度，以及提高数据的安全性. 


#### 删除Index
```
curl -X DELETE 'localhost:9200/conv19'
```

### 数据操作

#### 新增记录

> _doc 为默认的Type [数据来源](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)

```
curl -XPOST -H 'Content-type:application/json' localhost:9200/conv19/_doc/1 -d '
{
  "country": "US",
  "province": "Alabama",
  "confirmedCount": 14,
  "location":[-85.39072749,32.91360079],
  "createdAt":"2020-04-25"
}'
```
{"_index":"conv19","_type":"_doc","_id":"1","_version":2,"result":"updated","_shards":{"total":1,"successful":1,"failed":0},"_seq_no":1,"_primary_term":1}

```

{
  "_index":"accounts",
  "_type":"person",
  "_id":"1",
  "_version":1,
  "result":"created",
  "_shards":{"total":2,"successful":1,"failed":0},
  "created":true
}
```

#### 查看记录

> pretty=true表示以格式化JSON进行返回。

```
curl 'localhost:9200/conv19/_doc/1?pretty=true'
```

返回数据 

```
{
  "_index" : "conv19",
  "_type" : "_doc",
  "_id" : "1",
  "_version" : 35,
  "_seq_no" : 34,
  "_primary_term" : 1,
  "found" : true,
  "_source" : {
    "country" : "US",
    "province" : "Alabama",
    "confirmedCount" : 14,
    "location" : [
      -85.39072749,
      32.91360079
    ],
    "createdAt" : "2020-04-25"
  }
}
```

如果 Id 不正确，就查不到数据，found字段就是false。
```

{
  "_index" : "accounts",
  "_type" : "person",
  "_id" : "1",
  "found" : false
}
```

#### 删除记录

```
curl -X DELETE 'localhost:9200/conv19/_doc/1'
```

#### 更新记录
```
curl -XPUT -H 'Content-type:application/json' localhost:9200/conv19/_doc/1 -d '
{
  "country": "US",
  "province": "Alabama",
  "confirmedCount": 14,
  "location":[-85.39072749,32.91360079],
  "createdAt":"2020-04-25"
}'


{"_index":"conv19","_type":"_doc","_id":"1","_version":35,"result":"updated","_shards":{"total":1,"successful":1,"failed":0},"_seq_no":34,"_primary_term":1}
```

#### 批量操作数据

```
PUT /conv19/_bulk
{"index":{"_index":"conv19"}}
{"country":"US","province":"Alabama","confirmedCount":14,"location":[-85.39072749,32.91360079],"createdAt":"2020-04-25"}
{"index":{"_index":"conv19"}}
{"country":"US","province":"Alabama","confirmedCount":14,"location":[-85.39072749,32.91360079],"createdAt":"2020-04-25"}
```

### 数据查询

#### 搜索
```
curl 'localhost:9200/conv19/_doc/_search'
```

#### 分页搜索

```
curl 'localhost:9200/conv19/_doc/_search' -d '
{
    "from":0,
    "size":20
}'

{
  "took":2,
  "timed_out":false,
  "_shards":{"total":5,"successful":5,"failed":0},
  "hits":{
    "total":2,
    "max_score":1.0,
    "hits":[
      {
        "_index":"accounts",
        "_type":"person",
        "_id":"AV3qGfrC6jMbsbXb6k1p",
        "_score":1.0,
        "_source": {
          "user": "李四",
          "title": "工程师",
          "desc": "系统管理"
        }
      },
      {
        "_index":"accounts",
        "_type":"person",
        "_id":"1",
        "_score":1.0,
        "_source": {
          "user" : "张三",
          "title" : "工程师",
          "desc" : "数据库管理，软件开发"
        }
      }
    ]
  }
}
```

* total：返回记录数，本例是2条。
* max_score：最高的匹配程度，本例是1.0。
* hits：返回的记录组成的数组。

#### 全文搜索
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "query" : { "term" : { "province" : "Alabama" }}
}'
```

### 聚合

#### Count 统计记录数
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "count": {
      "value_count": {
        "field": "confirmedCount"
      }
    }
  }
}'
```


#### Sum 统计总数
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "sum": {
      "sum": {
        "field": "confirmedCount"
      }
    }
  }
}'
```


#### 求最大
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "max": {
      "max": {
        "field": "confirmedCount"
      }
    }
  }
}'
```


#### 求最小
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "max": {
      "max": {
        "field": "confirmedCount"
      }
    }
  }
}'
```


#### 求平均
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "avg": {
      "avg": {
        "field": "confirmedCount"
      }
    }
  }
}'
```


#### 按时间聚合
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "sumConfirmedCount": {
      "date_histogram": {
        "field": "createdAt",
        "interval": "day"
      }
    }
  }
}'
```

#### 按时间分组聚合
```
curl 'localhost:9200/conv19/_doc/_search'  -d '
{
  "aggs": {
    "sumConfirmedCount": {
      "date_histogram": {
        "field": "createdAt",
        "interval": "day"
      }
      , "aggs": {
        "count": {
          "value_count": {
            "field": "confirmedCount"
          }
        }
      }
    }
  }
}'
```

### Kibana 

#### 安装

Mac

```
curl -o kibana-7.6.2.tar.gz https://artifacts.elastic.co/downloads/kibana/kibana-7.6.2-darwin-x86_64.tar.gz
tar -zxvf kibana-7.6.2.tar.gz 
cd kibana-7.6.2
./bin/kibana
```

Windows

```
https://artifacts.elastic.co/downloads/kibana/kibana-7.6.2-windows-x86_64.zip
```

Linux
```
https://artifacts.elastic.co/downloads/kibana/kibana-7.6.2-linux-x86_64.tar.gz
```


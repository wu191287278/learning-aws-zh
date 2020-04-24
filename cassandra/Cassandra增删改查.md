## Cassandra 增删改查

### Cassandra 数据类型

|数据类型|	常量|	描述|
|---|---|---|
|ascii	|strings	|表示ASCII字符串|
|bigint	|bigint	|表示64位有符号长|
|blob	|blobs	|表示任意字节|
|Boolean	|booleans	|表示true或false|
|counter	|integers	|表示计数器列|
|decimal	|integers, floats	|表示变量精度十进制|
|double	|integers	|表示64位IEEE-754浮点|
|float	|integers, floats|	表示32位IEEE-754浮点|
|inet	|strings	|表示一个IP地址，IPv4或IPv6|
|int	|integers	|表示32位有符号整数|
|text	|strings	|表示UTF8编码的字符串|
|timestamp	|integers, strings	|表示时间戳|
|timeuuid	|uuids	|表示类型1 UUID|
|uuid	|uuids	|表示类型1或类型4|
|varchar|	strings	|表示uTF8编码的字符串|
|varint	|integers	|表示任意精度整数|
|map	|	|字段类型|
|set	|	|去重集合类型|
|list	|	|集合类型|


### 安装 Cassandra

```
docker run --name cassandra -p 7000:7000 -p 9042:9042 -d cassandra
```

### 简单使用

#### 进入Cassandra 客户端
```
docker exec -it cassandra cqlsh
```

#### 创建表空间KeySpace 类似mysql database

```
CREATE KEYSPACE example
WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};
```

> 参数说明

* replication_factor 该空间副本数量
* SimpleStrategy 不考虑数据中心，将Token按照从小到大的顺序，从第一个Token位置处依次取N个节点作为副本。
* OldNetworkTopologyStrategy 考虑数据中心，首先，在primary Token所在的数据中心的不同rack上存储N-1份数据，然后在另外一个不同数据中心的节点存储一份数据。该策略特别适合多个数据中心的应用场景，这样可以牺牲部分性能（数据延迟）的前提下，提高系统可靠性。
* NetworkTopologyStrategy 这需要复制策略属性文件，在该文件中定义在每个数据中心的副本数量。在各数据中心副本数量的总和应等于Keyspace的副本数量。


#### 使用表空间
```
use example;
```

#### 创建表
```
CREATE TABLE users (
	id INT,
	username text,
	password text,
	created_at BIGINT,
	PRIMARY KEY (id)
);
```


#### 添加表字段
```
ALTER TABLE users ADD  updated_at bigint;
```

#### 删除表
```
DROP TABLE users;
```

#### 删除表空间
```
DROP KEYSPACE exampes;
```

### DML

#### 插入数据

```
INSERT INTO 
users (id, username, "password", created_at)
values(1, 'zhangsan', 'lisi', dateof (now()))
```

#### 更新数据
```
UPDATE
	users
SET
	username = 'wangwu'
WHERE
	id = 1
```

#### 删除数据
```
DELETE FROM users WHERE id = 1
```

### 排序

#### 创建带有排序的表

> Cassandra 支持4个主键,第一个键 为分区键，用于分区使用.其他3个主键可以作为排序键或其他用途. 下面演示创建一个**评论表**使用photo_id作为分区键,id作为排序键.

```
CREATE TABLE comments (
	id INT,
    photo_id BIGINT,
    owner_id BIGINT,
	user_id BIGINT,
	content TEXT,
    created_at BIGINT,
	PRIMARY KEY (photo_id,id ),
)
 WITH CLUSTERING ORDER BY (id desc);
```

#### 插入测试数据
```
INSERT INTO comments (id, photo_id, owner_id, user_id, content, created_at) VALUES(1, 1, 1, 1, 'Yellow', dateof(now()));
INSERT INTO comments (id, photo_id, owner_id, user_id, content, created_at) VALUES(2, 1, 1, 1, 'Blue', dateof (now()));
INSERT INTO comments (id, photo_id, owner_id, user_id, content, created_at) VALUES(3, 1, 1, 1, 'Red', dateof(now()));
```

#### 查询

```
select * from comments
```

结果: 可以看到按照评论id进行倒序排列
```
 photo_id | id | content | created_at    | owner_id | user_id
----------+----+---------+---------------+----------+---------
        1 |  3 |     Red | 1587718841259 |        1 |       1
        1 |  2 |    Blue | 1587718820618 |        1 |       1
        1 |  1 |  Yellow | 1587718888426 |        1 |       1

```

#### 分页
```
select * from comments where photo_id=1 limit 2;
```

结果:
```
 photo_id | id | content | created_at    | owner_id | user_id
----------+----+---------+---------------+----------+---------
        1 |  3 |     Red | 1587718841259 |        1 |       1
        1 |  2 |    Blue | 1587718820618 |        1 |       1
```

携带上一个ID 作为条件取 下一页数据

```
select * from comments where photo_id=1 and id < 2 limit 2
```

结果

```
 photo_id | id | content | created_at    | owner_id | user_id
----------+----+---------+---------------+----------+---------
        1 |  1 |  Yellow | 1587718888426 |        1 |       1
```

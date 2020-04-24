## Cassandra策略

### 背景介绍

Cassandra 使用分布式哈希表（DHT）来确定存储某一个数据对象的节点。在 DHT 里面，负责存储的节点以及数据对象都被分配一个 token。token 只能在一定的范围内取值，比如说如果用 MD5 作为 token 的话，那么取值范围就是 [0, 2^128-1]。存储节点以及对象根据 token 的大小排列成一个环，即最大的 token 后面紧跟着最小的 token，比如对 MD5 而言，token 2^128-1 的下一个 token 就是 0。Cassandra 使用以下算法来分布数据：

首先，每个存储节点被分配一个随机的 token（涉及数据分区策略），该 token 代表它在 DHT 环上的位置；

然后，用户为数据对象指定一个 key（即 row-key），Cassandra 根据这个 key 计算一个哈希值作为 token，再根据 token 确定对象在 DHT 环上的位置；

最后，该数据对象由环上拥有比该对象的 token 大的最小的 token 的节点来负责存储；

根据用户在配置时指定的备份策略（涉及网络拓扑策略），将该数据对象备份到另外的 N-1 个节点上。网络中总共存在该对象的 N 个副本。

因此，每个存储节点最起码需要负责存储在环上位于它与它的前一个存储节点之间的那些数据对象，而且这些对象都会被备份到相同的节点上。我们把 DHT 环上任何两点之间的区域称为一个 range，那么每个存储节点需要存储它与前一个存储节点之间的 range。

因为 Cassandra 以 range 为单位进行备份，所以每个节点需要定期检查与它保存了相同的 range 的节点，看是否有不一致的情况，这涉及到数据一致性策略。

另外，Cassandra的一个特点是写速度大于读速度，这都归功于它的存储策略。

本文总结了Cassandra中使用的各种策略，包括数据分局策略，数据备份策略，网络拓扑策略，数据一致性策略和存储策略等。

### Partitioner数据分区策略

将key/value按照key存放到不同的节点上。Partitioner会按照某种策略给每个cassandra节点分配一个token，每个key/value进行某种计算后，将被分配到器对应的节点上。

提供了以下几个分布策略：

org.apache.cassandra.dht.RandomPartitioner：

将key/value按照（key的）md5值均匀的存放到各个节点上。由于key是无序的，所有该策略无法支持针对Key的范围查询。

org.apache.cassandra.dht.ByteOrderedPartitioner（BOP）：

将key/value按照key（byte）排序后存放到各个节点上。该Partitioner允许用户按照key的顺序扫描数据。该方法可能导致负载不均衡。

org.apache.cassandra.dht.OrderPreservingPartitioner：

该策略是一种过时的BOP，仅支持key为UTF8编码的字符串。

org.apache.cassandra.dht.CollatingOrderPreservingPartitioner：

该策略支持在EN或者US环境下的key排序方式。

### 备份策略（副本放置策略）

为了保证可靠性，一般要将数据写N份，其中一份写在其对应的节点上（由数据分片策略决定），另外N-1份如何存放，需要有相应的备份策略。

SimpleStrategy (以前称为RackUnawareStrategy，对应org.apache.cassandra.locator.RackUnawareStrategy)：

不考虑数据中心，将Token按照从小到大的顺序，从第一个Token位置处依次取N个节点作为副本。

OldNetworkTopologyStrategy (以前称为RackAwareStrategy，对应org.apache.cassandra.locator.RackAwareStrategy)：

考虑数据中心，首先，在primary Token所在的数据中心的不同rack上存储N-1份数据，然后在另外一个不同数据中心的节点存储一份数据。该策略特别适合多个数据中心的应用场景，这样可以牺牲部分性能（数据延迟）的前提下，提高系统可靠性。

NetworkTopologyStrategy (以前称为DatacenterShardStrategy，对应org.apache.cassandra.locator.DataCenterShardStrategy)：

这需要复制策略属性文件，在该文件中定义在每个数据中心的副本数量。在各数据中心副本数量的总和应等于Keyspace的副本数量。

### 网络拓扑策略

该策略主要用于计算不同host的相对距离，进而告诉Cassandra你的网络拓扑结构，以便更高效地对用户请求进行路由。

org.apache.cassandra.locator.SimpleSnitch：

将不同host逻辑上的距离（cassandra ring）作为他们之间的相对距离。

org.apache.cassandra.locator.RackInferringSnitch:

相对距离是由rack和data center决定的，分别对应ip的第3和第2个八位组。即，如果两个节点的ip的前3个八位组相同，则认为它们在同一个rack（同一个rack中不同节点，距离相同）；如果两个节点的ip的前两个八位组相同，则认为它们在同一个数据中心（同一个data center中不同节点，距离相同）。

org.apache.cassandra.locator.PropertyFileSnitch:

相对距离是由rack和data center决定的，且它们是在配置文件cassandra-topology.properties中设置的。

### 调度策略

对用户请求采用某个策略调度到不同节点上。

org.apache.cassandra.scheduler.NoScheduler：不用调度器

org.apache.cassandra.scheduler.RoundRobinScheduler：不同request_scheduler_id的用户请求采用轮询的方法放到节点的不同队列中。

### 一致性策略

#### 一致性等级

Cassandra采用了最终一致性。最终一致性是指分布式系统中的一个数据对象的多个副本尽管在短时间内可能出现不一致，但是经过一段时间之后，这些副本最终会达到一致。

Cassandra 的一个特性是可以让用户指定每个读/插入/删除操作的一致性级别（consistency level）。Casssandra API 目前支持以下几种一致性级别：

ZERO：只对插入或者删除操作有意义。负责执行操作的节点把该修改发送给所有的备份节点，但是不会等待任何一个节点回复确认，因此不能保证任何的一致性。

ONE：对于插入或者删除操作，执行节点保证该修改已经写到一个存储节点的 commit log 和 Memtable 中；对于读操作，执行节点在获得一个存储节点上的数据之后立即返回结果。

QUORUM：假设该数据对象的备份节点数目为 n。对于插入或者删除操作，保证至少写到 n/2+1 个存储节点上；对于读操作，向 n/2+1 个存储节点查询，并返回时间戳最新的数据。

ALL：对于插入或者删除操作，执行节点保证n（n为replication factor）个节点插入或者删除成功后才向client返回成功确认消息，任何一个节点没有成功，该操作均失败；对于读操作，会向n个节点查询，返回时间戳最新的数据，同样，如果某个节点没有返回数据，则认为读失败。

注：Cassandra默认的读写模式W(QUORUM)/R(QUORUM)，事实上，只要保证W+R>N（N为副本数），即写的节点和读的节点重叠，则是强一致性. 如果W+R<=N ，则是弱一致性.（其中，W是写节点数目，R是读节点数目）。

如果用户在读和写操作的时候都选择 QUORUM 级别，那么就能保证每次读操作都能得到最新的更改。另外，Cassandra 0.6 以上的版本对插入和删除操作支持 ANY 级别，表示保证数据写到一个存储节点上。与 ONE 级别不同的地方是，ANY 把写到 hinted handoff 节点上也看作成功，而 ONE 要求必须写到最终的目的节点上。

#### 维护最终一致性

Cassandra 通过4个技术来维护数据的最终一致性，分别为逆熵（Anti-Entropy），读修复（Read Repair），提示移交（Hinted Handoff）和分布式删除。

(1) 逆熵

这是一种备份之间的同步机制。节点之间定期互相检查数据对象的一致性，这里采用的检查不一致的方法是 Merkle Tree；

(2) 读修复

客户端读取某个对象的时候，触发对该对象的一致性检查；

举例：

读取Key A的数据时，系统会读取Key A的所有数据副本，如果发现有不一致，则进行一致性修复。

如果读一致性要求为ONE，会立即返回离客户端最近的一份数据副本。然后会在后台执行Read Repair。这意味着第一次读取到的数据可能不是最新的数据；如果读一致性要求为QUORUM，则会在读取超过半数的一致性的副本后返回一份副本给客户端，剩余节点的一致性检查和修复则在后台执行；如果读一致性要求高(ALL)，则只有Read Repair完成后才能返回一致性的一份数据副本给客户端。可见，该机制有利于减少最终一致的时间窗口。

(3) 提示移交

对写操作，如果其中一个目标节点不在线，先将该对象中继到另一个节点上，中继节点等目标节点上线再把对象给它；

举例：

Key A按照规则首要写入节点为N1，然后复制到N2。假如N1宕机，如果写入N2能满足ConsistencyLevel要求，则Key A对应的RowMutation将封装一个带hint信息的头部（包含了目标为N1的信息），然后随机写入一个节点N3，此副本不可读。同时正常复制一份数据到N2，此副本可以提供读。如果写N2不满足写一致性要求，则写会失败。 等到N1恢复后，原本应该写入N1的带hint头的信息将重新写回N1。

(4) 分布式删除

单机删除非常简单，只需要把数据直接从磁盘上去掉即可，而对于分布式，则不同，分布式删除的难点在于：如果某对象的一个备份节点 A 当前不在线，而其他备份节点删除了该对象，那么等 A 再次上线时，它并不知道该数据已被删除，所以会尝试恢复其他备份节点上的这个对象，这使得删除操作无效。Cassandra 的解决方案是：本地并不立即删除一个数据对象，而是给该对象标记一个hint，定期对标记了hint的对象进行垃圾回收。在垃圾回收之前，hint一直存在，这使得其他节点可以有机会由其他几个一致性保证机制得到这个hint。Cassandra 通过将删除操作转化为一个插入操作，巧妙地解决了这个问题。

### 存储策略

Cassandra的存储机制借鉴了Bigtable的设计，采用Memtable和SSTable的方式。和关系数据库一样，Cassandra在写数据之前，也需要先记录日志，称之为commitlog（数据库中的commit log 分为 undo-log, redo-log 以及 undo-redo-log 三类，由于 cassandra采用时间戳识别新老数据而不会覆盖已有的数据，所以无须使用 undo 操作，因此它的 commit log 使用的是 redo log），然后数据才会写入到Column Family对应的Memtable中，且Memtable中的数据是按照key排序好的。Memtable是一种内存结构，满足一定条件后批量刷新（flush）到磁盘上，存储为SSTable。这种机制，相当于缓存写回机制(Write-back Cache)，优势在于将随机IO写变成顺序IO写，降低大量的写操作对于存储系统的压力。SSTable一旦完成写入，就不可变更，只能读取。下一次Memtable需要刷新到一个新的SSTable文件中。所以对于Cassandra来说，可以认为只有顺序写，没有随机写操作。

SSTable是不可修改的，且一般情况下，一个CF可能会对应多个SSTable，这样，当用户检索数据时，如果每个SSTable均扫描一遍，将大大增加工作量。Cassandra为了减少没有必要的SSTable扫描，使用了BloomFilter，即通过多个hash函数将key映射到一个位图中，来快速判断这个key属于哪个SSTable。

为了减少大量SSTable带来的开销，Cassandra会定期进行compaction，简单的说，compaction就是将同一个CF的多个SSTable合并成一个SSTable。在Cassandra中，compaction主要完成的任务是：

（1）垃圾回收： cassandra并不直接删除数据，因此磁盘空间会消耗得越来越多，compaction 会把标记为删除的数据真正删除；

（2）合并SSTable：compaction 将多个 SSTable 合并为一个（合并的文件包括索引文件，数据文件，bloom filter文件），以提高读操作的效率；

（3）生成 MerkleTree：在合并的过程中会生成关于这个 CF 中数据的 MerkleTree，用于与其他存储节点对比以及修复数据。
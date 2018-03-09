# Pistis

A server makes work trustful by using blockchain technology

> pistis [name origin](https://en.wikipedia.org/wiki/Pistis)

## todos

- help page: how to verify
- help page: how it works
- server log tool
- server cron task
- private token 权限认证机制

## 概念设计

### manifest

manifest是一个证明，我们将证明提交到Pistis，让Pistis为我们的证明作证

对于keepwork来说，证明需要有如下的内容

```
field:
为数据划分区域，便于后续为其它服务提供证明
这里取值为keepwork
域的定义也决定了后续字段的定义，比如域也可以定义为github，接收github项目的证明，
后续的字段可以自己定义，用于标识项目的唯一性

author:
作者名，在keepwork下，取值网站的用户名

work:
作品名，在keepwork下，取值用户作品的站点名

id:
唯一标识符，唯一标识作品内容。在keepwork下，取值作品git的某个commit hash
```

### fingerprint

fingerprint是一个指纹，Pistis对于manifest的每一次作证，都会生成 fingerprint
当做标识这一次作证的凭证

fingerprint的输入包括
- manifest的内容
- 进行作证的时间戳

fingerprint生成，使用hash算法，唯一标识了manifest的内容与作证的时间

### block

block是Pistis中的概念，表示众多作证的集合

会有不同的manifest申请认证，block的作用是将某一时刻存在的所有认证进行聚合，
是Pistis所有认证的snapshot

block内容包括
- 唯一的hash标识
- 描述
- 进行聚合的时间戳

Pistis记录了所有的block，根据block hash，可以定位任意一个block并获取所有block内容

### chain block

chain block是公共区块链的块，公共区块链得到大家的信任，我们将Pistis block提交至chain block，
于是Pistis block也得到了信任

## 程序设计

### api

- 失败的api

    所有失败的api都返回
    return
    {
      "error": "error message why"
    }

- 向Pistis提交证明，进行作证

    POST /api/v1/manifest
    
    param
    {
      "field": "keepwork",
      "author": "${keepwork_user_name}",
      "work": "${keepwork_user_site_name}",
      "id": "${keepwork_user_site_git_commit_id}"
    }
    
    return
    {
      "field": "keepwork",
      "author": "${keepwork_user_name}",
      "work": "${keepwork_user_site_name}",
      "id": "${keepwork_user_site_git_commit_id}",
      "timestamp": "${time_when_witness}",
      "fingerprint": "${fingerprint_that_gen}"
    }

- 查看证明

    GET /api/v1/manifest
    
    param
    {
      "fingerprint": "${fingerprint_that_gen}"
    }
    
    return
    返回的数据根据域的不同而不同，keepwork的格式如下
    {
      "field": "keepwork",
      "author": "${keepwork_user_name}",
      "work": "${keepwork_user_site_name}",
      "id": "${keepwork_user_site_git_commit_id}",
      "timestamp": "${time_when_witness}",
    }
    
### 页面

- Pistis提供作证证书页面

    GET /page/v1/cert/:fingerprint?block_hash=:block_hash
    
    对于keepwork来说，
    页面内容包括
    - 文本
      - keepwork标识
      - author信息
      - work作品信息
      - 由Pistis认证的时间（UTC+8 or UTC+0）
    - 链接
      - work 作品 id
      - fingerprint
      - Pistis block hash
      - chain block hash
    - 图片
      - 图形印章（使用私钥认证）
      
- Pistis block页面

    GET /page/v1/block/:block_hash
    
    页面内容包括
    - block hash值
    - block生成时间
    - block生成描述
    - block所聚合的所有manifest列表
    
- manifest页面

    GET /page/v1/manifest/:fingerprint
    
    内容包括
    - manifest的内容
    - 作证时间戳
    
- chain block页面

    使用公共服务，地址待定
    
## 数据设计

manifest
manifest的内容为key:value对，以json格式保存
Pistis在为每个manifest作证时，会加上timestamp:now的键值，再将整个json file进行SHA-256运算，
生成 fingerprint


block
所有的manifest组织为一个git仓库，仓库目录文件按fingerprint来组织，结构为

    /
      AE/
        1C/
          2EF......AD3

fingerprint为64字节代表16进制的字符组成，分成3段
- 1-2字节
- 3-4字节
- 5-64字节

前两部分组织为目录与子目录，最后部分为文件名，存储着manifest与timestamp组成的json文件

所以一个block是一个git commit，这样就理解了block的所有内容


chain block
blockchain使用公共服务，将block信息提交到blockchain，将会作为blockchain的一个区块
这个区块有一个唯一的hash标识
每当提交一个block，并成功写入区块，需要将对应关系记录下来
- 一个block可以没有chain block对应
- 一个block可能写入了多个chain block
- 多个block可能写入了同一个chain block

总结下来，block与chain block是多对多的关系


对应关系记录存储于db中，表结构
| id     | service                          | chain_block    | block            |
|--------|----------------------------------|----------------|------------------|
| 自增id | 区块链服务类型，目前只有ethereum | 区块的hash标识 | 提交的Pistis block hash |




## 用户规则

对于所有用户，拥有被动方式
- 每天一次进行作品认证

对于其中的VIP用户，提供主动方式
- 可以自己触发作品认证，每日多次


一经认证，便已存在于历史中，无法删除


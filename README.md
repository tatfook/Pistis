# Pistis

A server makes work trustful by using blockchain technology

> pistis [name origin](https://en.wikipedia.org/wiki/Pistis)

## 概念设计

### manifest

Pistis为数据提供凭证，证明 **某时刻某数据确实存在着**

manifest就是用户想要获取凭证的数据，通过Pistis，为manifest作证

### fingerprint

Pistis每一次对manifest作证，都会生成fingerprint，作为作证行为的凭证

Pistis通过
- manifest内容
- 作证行为发生的时间戳
生成fingerprint

一个fingerprint唯一标识一次作证行为，理论上，不可能有多个作证行为对应相同的fingerprint

### block

在Pistis中，**某一时刻**所有manifest与fingerprint的**集合**，聚合构成一个block

block由
1. manifest与fingerprint
2. 描述信息
3. 聚合行为发生的时间戳
生成唯一的block hash

三项输入共同决定了block hash的值，理论上，不可能有三项不同输入生成相同的block hash

Pistis保留了所有block，根据hash标识，可以唯一定位到一个block，并索引到**那一时刻**所有manifest与fingerprint的**内容**

### blockchain block

即使Pistis为manifest作证，但是Pistis本身并不可信，需要大家公认的信任源为Pistis提供信任

公共区块链得到大家的信任，将Pistis block提交至区块链区块，借助区块链为Pistis提供信任

## 数据设计

### manifest

不同的用户对manifest有不同的需要，这里我们希望用普适的key:value的形式来组织数据，以json来存储

对于keepwork来说，manifest需要有如下的内容

| key      | value                      | description                                                                                                                           |
|----------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| field    | keepwork                   | 为数据划分区域，便于后续为接入其它服务提供拓展性。对于keepwork，取值为keepwork。也可能为github或者其它值，field也决定了后续字段的内容 |
| author   | ${keepwork_user_name}      | 作者名，取值keepwork的用户名                                                                                                          |
| work     | ${keepwork_user_work_name} | 作品名，取值keepwork用户作品网站的名字                                                                                                |
| identity | ${work_unique_id}          | 唯一标识符，唯一标识作品内容，取值网站git存储的某个commit hash                                                                        |


Pistis在为manifest作证时，会附加新的timestamp:${now}键值，根据key进行增序排序，再将所有数据进行SHA-256运算，生成fingerprint

所有manifest组织为一个git仓库，仓库目录与文件按fingerprint来组织，结构为

    /
      AE/
        1C/
          2EF......AD3

fingerprint为64字节代表16进制的字符组成，分成3段
- 1-2字节
- 3-4字节
- 5-64字节

前两部分组织为目录与子目录，最后部分为文件名，存储着manifest与timestamp组成的json文件

示例：

1. 请求认证的manifest

    {
      "field": "keepwork",
      "author": "dukes",
      "work": "test-report",
      "identity": "87f90ee50c0e3e1808a7931b4ed743ecf8aa98f2"
    }

2. 附加时间戳

    {
      "field": "keepwork",
      "author": "dukes",
      "work": "test-report",
      "identity": "87f90ee50c0e3e1808a7931b4ed743ecf8aa98f2",
      "timestamp": "1520590199"
    }

3. 排序

    {
      "author": "dukes",
      "field": "keepwork",
      "identity": "87f90ee50c0e3e1808a7931b4ed743ecf8aa98f2",
      "timestamp": "1520590199",
      "work": "test-report"
    }

4. 去格式化

    {"author":"dukes","field":"keepwork","identity":"87f90ee50c0e3e1808a7931b4ed743ecf8aa98f2","timestamp":"1520590199","work":"test-report"}
 
5. 生成fingerprint

   $ echo '{"author":"dukes","field":"keepwork","identity":"87f90ee50c0e3e1808a7931b4ed743ecf8aa98f2","timestamp":"1520590199","work":"test-report"}' | sha256sum 
   9b84d679ad274c97b2d46e4bdf649350f9c7286c825aea6a4e0a3ba4cc27fe4d  -

6. 存储为文件
 
    /
      9b/
        84/
          d679ad274c97b2d46e4bdf649350f9c7286c825aea6a4e0a3ba4cc27fe4d

    $ mkdir -p 9b/84
    $ echo '{"author":"dukes","field":"keepwork","identity":"87f90ee50c0e3e1808a7931b4ed743ecf8aa98f2","timestamp":"1520590199","work":"test-report"}' > 9b/84/d679ad274c97b2d46e4bdf649350f9c7286c825aea6a4e0a3ba4cc27fe4d

### block

数据以git仓库管理，一个block是一个git commit，这样是block的本质

    $ git add .
    $ git commit -m "generate block"

### blockchain block

Pistis将block信息提交到blockchain，成为blockchain一个区块的一部分，借此来为Pistis提供信任

同样的，每个区块也有唯一的hash标识，
每当提交一个block，并成功写入区块，需要将block与blockchain block的对应关系记录下来

- 一个block可以没有写入blockchain block
- 一个block可能写入了多个blockchain block
- 多个block可能写入了同一个blockchain block

因此，block与chain block是多对多的关系


这种对应关系记录存储到db中，表结构如下
| id     | service                          | chain_block    | block            |
|--------|----------------------------------|----------------|------------------|
| 自增id | 区块链服务类型，目前只有ethereum | 区块的hash标识 | 提交的Pistis block hash |



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
    

## 用户规则

对于所有用户，拥有被动方式
- 每天一次进行作品认证

对于其中的VIP用户，提供主动方式
- 可以自己触发作品认证，每日多次


一经认证，便已存在于历史中，无法删除

## todos

- help page: how to verify
- help page: how it works
- server log tool
- server cron task
- private token 权限认证机制


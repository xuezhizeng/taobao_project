## 整体架构

分布式架构
- 队列系统 redis
- 抓取系统 requests
- 代理系统 redis/mongo
- web系统 flask + gunicorn
- 搜索系统 es

## 安装

```
virtualenv taobao.env
source taobao.env/bin/activate
pip install 'requests[security]'
pip install Flask
pip install gunicorn
```

## 运维部署

nginx
```
sudo ln -s `pwd`/etc/nginx.conf /etc/nginx/conf.d/taobao-charts.conf
sudo nginx -s reload  # 平滑重启
```

supervisor 维护单机的web进程
```
supervisord -c etc/supervisord.conf
supervisorctl -c etc/supervisord.conf reload
supervisorctl -c etc/supervisord.conf restart all
```

## 性能瓶颈

工作节点数（物理机器数量 × 机器核心数量）
高并发，可通过 Nginx 负载均衡分流
单台普通机器，最优支持16个并发才能控制响应时间在1s内

Gunicorn

并发      平均响应时间
10       608.187 [ms]
16       983.604 [ms]
20      1266.331 [ms]


## 性能测试

- flask 自带服务器测试

```
✗ python app/run.py
✗ ab -n 100 -c 10 http://127.0.0.1:5000/item_list/连衣裙/
```
平均响应时间 2307.839 [ms]
```
This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        Werkzeug/0.11.10
Server Hostname:        127.0.0.1
Server Port:            5000

Document Path:          /item_list/连衣裙/
Document Length:        168388 bytes

Concurrency Level:      10
Time taken for tests:   23.078 seconds
Complete requests:      100
Failed requests:        98
   (Connect: 0, Receive: 0, Length: 98, Exceptions: 0)
Total transferred:      16865184 bytes
HTML transferred:       16849284 bytes
Requests per second:    4.33 [#/sec] (mean)
Time per request:       2307.839 [ms] (mean)
Time per request:       230.784 [ms] (mean, across all concurrent requests)
Transfer rate:          713.65 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       0
Processing:   289 2204 389.3   2304    2512
Waiting:      288 2204 389.3   2303    2511
Total:        289 2204 389.2   2304    2512

Percentage of the requests served within a certain time (ms)
  50%   2304
  66%   2354
  75%   2372
  80%   2400
  90%   2432
  95%   2456
  98%   2484
  99%   2512
 100%   2512 (longest request)
```

- gunicorn 服务器测试(双核四线程cpu)开4个进程

```
✗ gunicorn -w4 -b0.0.0.0:5000 app:app
✗ ab -n 100 -c 10 http://127.0.0.1:5000/item_list/连衣裙/
```
平均响应时间 608.187 [ms]
```
This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn/19.6.0
Server Hostname:        127.0.0.1
Server Port:            5000

Document Path:          /item_list/连衣裙/
Document Length:        163430 bytes

Concurrency Level:      10
Time taken for tests:   6.082 seconds
Complete requests:      100
Failed requests:        98
   (Connect: 0, Receive: 0, Length: 98, Exceptions: 0)
Total transferred:      16357678 bytes
HTML transferred:       16341278 bytes
Requests per second:    16.44 [#/sec] (mean)
Time per request:       608.187 [ms] (mean)
Time per request:       60.819 [ms] (mean, across all concurrent requests)
Transfer rate:          2626.54 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.4      0       2
Processing:   302  581  84.8    575     908
Waiting:      302  580  84.8    574     907
Total:        303  581  85.0    575     909

Percentage of the requests served within a certain time (ms)
  50%    575
  66%    595
  75%    602
  80%    616
  90%    655
  95%    741
  98%    904
  99%    909
 100%    909 (longest request)
```

因为是动态网页测试，由于 Length 响应的内容长度不一致产生的 Failed requests 可以忽略

### 增加并发超过 1000
```
Benchmarking 127.0.0.1 (be patient)
socket: Too many open files (24)
```

查看系统限制
```
✗ ulimit -a
-t: cpu time (seconds)              unlimited
-f: file size (blocks)              unlimited
-d: data seg size (kbytes)          unlimited
-s: stack size (kbytes)             8192
-c: core file size (blocks)         0
-m: resident set size (kbytes)      unlimited
-u: processes                       63367
-n: file descriptors                1024
-l: locked-in-memory size (kbytes)  64
-v: address space (kbytes)          unlimited
-x: file locks                      unlimited
-i: pending signals                 63367
-q: bytes in POSIX msg queues       819200
-e: max nice                        0
-r: max rt priority                 0
-N 15:                              unlimited
```

修改参数
```
✗ ulimit -n 35768
```

linux 是通过文件来对设备进行管理，
ulimit -n 是设置同时打开文件的最大数值，
ab 中每一个连接打开一个设备文件，所以设置这个值就可以解决了。


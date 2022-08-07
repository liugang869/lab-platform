IP信息：

centos IP 10.202.1.33
website: 134.226.41.134 : (80/443)
         db.ict.ac.cn

nohup python3 manage.py runserver > zserver.log &
nohup python3 runscore.py > zscore.log &

配置工具：

使用nginx作为请求分发中间件
使用用gunicorn运行多线程响应请求
http://docs.gunicorn.org/en/stable/deploy.html

配置注意事项:

需要保证到网站的路径能被执行
需要SELinux需要设置为permissive

-----------------------------------------------------------------------------------------------------------

参考文档：

## 网站服务器部署
因为Django自带的HTTP server是单线程的，通常不用于生产环境，我们选择**Nginx + Gunicorn**的方案来部署Ｄjango。

### 修改网站配置
编辑`finance/setting.py`文件
- 修改`SECRET_KEY`，`DEBUG`，`ALLOWED_HOSTS`的值

### 安装Gunicorn替代Django自带的WSGI HTTP Server
```bash
$ sudo pip3 install gunicorn
```

### 启动Gunicorn
```bash
# 可以更改绑定的端口, -h参数可以显示Gunicorn可以配置的选项，如线程数
$ gunicorn finance.wsgi:application --bind 0.0.0.0:8080
```

这时候可以访问网站了，但是Gunicorn在处理Django的静态资源（css, javascript）时有点问题，我们需要在Gunicorn的前端使用代理服务器转发处理请求，这个代理转发服务器可以是`Apache server`或者`Nginx server`。

接下来以Nginx为例说明, 版本号为`nginx/1.12.2`。

### 部署nginx
#### 安装nginx
```bash
$ sudo apt-get install nginx
```

#### 增加finance站点的nginx配置文件
1. 删除`/etc/nginx/conf.d/`文件夹里的默认站点配置文件`default.conf`，可以参考他是如何写的
2. 在`/etc/nginx/conf.d/`新建文件`finance.conf`，文件名无所谓，文件内容如下(#为注释符)，
```
server {
    listen       80;  # nginx server监听80端口
    server_name  localhost;   # 服务器名称，通常与域名一致

    # nginx server根据以下规则匹配url，对请求流量进行处理，如有多个匹配，则选择最长匹配
    location / {
        # proxy_pass的值有几种形式，参考文档
        # http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass 
        proxy_pass http://localhost:8080;  # 匹配`/*`，将请求转发到8080端口，也就是之前gunicorn的运行端口 
    }
    location /static/ {
        # root 指向finance项目的路径
        root /(替换为相应的路径)/finance;  # 匹配'/static/*', 直接返回root下的对应文件
    }
    location /favicon.ico {
        # root 指向finance项目里的static文件夹的路径
        root /(替换为相应的路径)/finance/static;  # 匹配'/favicon.ico', 直接返回root下的对应文件
    }
}
```
3. 重启nginx server
```bash
sudo systemctl restart nginx
```

以上是以**nginx 1.12.2**为例说明配置方法，低版本的配置目录有所不同，这点最好参考官方文档。
如果不想开放80端口，可以将nginx的监听端口修改为其他值。

##### 参考文档
1. http://gunicorn.org/
2. https://nginx.org/en/

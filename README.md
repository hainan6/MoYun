# MoYun

> “墨韵”在线读书交流平台项目 V2.0，在前作基础上进行了较大程度的优化。

<details>
<summary>效果展示</summary>

<ul>
  <li>首页
    <img src="./docs/readme_img/首页.png" alt="首页">
  </li>
  <li>书评
    <img src="./docs/readme_img/书评.png" alt="书评">
  </li>
  <li>书籍
    <img src="./docs/readme_img/书籍.png" alt="书籍">
  </li>
  <li>圈子
    <img src="./docs/readme_img/圈子.png" alt="圈子">
  </li>
  <li>私信
    <img src="./docs/readme_img/私信.png" alt="私信">
  </li>
</ul>

</details>

## 1. 功能介绍

### 1.1 基本功能

* 账号管理：注册、登录、登出、找回密码(需要配置邮箱服务)、修改个人信息、查看他人信息
* 书评：写书评、书评点赞、书评回复、书评搜索
* 书籍：书籍搜索、书籍详情
* 圈子：创建圈子、查看圈子详情、修改圈子信息(仅限管理员)、发表新帖、回帖
* 消息：用户间私信
* 个性化选项：个人头像、签名，圈子头像，书评插图

### 1.2 特色功能

* 自定义部分Error页面(比如404页面的效果，可以通过访问[`/error_sample/404`](http://127.0.0.1:5000/error_sample/404)预览)
* 消息中心：整合书评回复、圈子新帖、帖子回复、私信等消息
* 首页引入地方天气和“今日诗词”API
* 使用Redis作为数据库缓存，提高性能
* 基于大语言模型([通义千问](https://help.aliyun.com/zh/dashscope/developer-reference/model-introduction))的AI辅助创作功能

## 2. 部署指南

> 部署指南分两部分，在开发环境中仅需执行第一部分基本配置即可，完成后可在本地运行项目，便于进行修改和调试；第二部分内容为服务部署，引导你将项目部署到服务器上，供他人访问。
>
> 在安装之前，需确保电脑满足以下条件：
>
> * 部署路径请保证全英文
> * 可以正常访问互联网，以便于安装依赖
> * 具有Python环境，且版本不低于3.10
> * 已安装并配置好MySQL，root用户使用密码登录
> * 已安装并配置好Redis或同类项目（如Memurai、Valkey）

### 2.1 基本配置

1. **获取项目源代码**：使用`git clone`指令或直接下载整个项目的压缩包以获取项目源代码(仅需当前分支)
2. **安装必要依赖**：在项目根目录下执行`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade`(Windows)或`pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade`(Linux)，安装必要依赖。
3. **修改配置文件**：按照自身情况修改[`config.yaml`](/config.yaml)(建议将其拷贝一份为`myConfig.yaml`，并在这个文件中修改配置)
    > 该项目使用的“一刻天气”和“通义千问”的API均需要申请key，需要分别将相关配置填入配置文件中，否则使用该API时会触发内部错误(500)。此外，若邮箱相关配置(`E-Mail`)并未填写，则找回密码功能不可用。
4. **初始化数据库**：在项目根目录下执行`python initDB.py`(Windows)或`python3 initDB.py`(Linux)，按照提示，初始化数据库，该脚本假设您的MySQL中已有一个带有密码的**root**用户，并利用该用户创建数据库和表。
    > 注：在根目录下还存在一个[`ddlDemo.sql`](./ddlDemo.sql)，这份SQL是一个带有部分初始信息的DDL文件，可以用来快速初始化数据库，以预览项目的效果。使用方法为创建对应的数据库后，直接使用`source`指令导入即可，无需执行`initDB.py`文件
5. **安装额外依赖**：（WSGI服务器、OpenCV）

    ```shell
    pip install tornado opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple # Windows
    pip3 install uWSGI opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple # Linux
    ```

6. 此时在项目根目录下执行`python -u app.py`(Windows)或`python3 -u app.py`(Linux)即可运行，默认通过`http://127.0.0.1:5000`访问。

### 2.2 服务部署

1. **配置反向代理**：本项目使用Nginx作为反向代理。
   * 在项目根目录下附带了一份Nginx配置示例[`nginx.cfg`](./nginx.cfg)，适用于使用`http`协议、监听5000端口的情况。
   * 确定符合你的项目后，可用其替换掉Nginx配置文件(通常为`/usr/local/nginx/conf/nginx.conf`或`/etc/nginx/sites-available/default`)，修改后需要重启Nginx。

     ```shell
     # 这是一份在Linux下的配置参考，假定Nginx的配置文件为/usr/local/nginx/conf/nginx.conf
     sudo mv /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.bak # 备份原配置文件
     sudo cp ./nginx.cfg /usr/local/nginx/conf/nginx.conf # 将项目中的配置文件复制到Nginx配置文件夹
     systemctl restart nginx.service # 重启Nginx
     ```

2. **启动服务**：由于Flask自身使用的WSGI性能较差，因此通常使用uWSGI(Linux)或Tornado(Windows)等其他服务器来部署。
   * **Linux**:
     * 项目中已经提供了uWSGI的配置文件[`uwsgi.ini`](./uwsgi.ini)，可直接使用，该配置文件适用于使用`http`协议、监听5000端口的情况。
     * 在项目根目录下执行以下命令即可启动uWSGI服务：

       ```shell
       uwsgi --ini uwsgi.ini # 中止服务使用 "uwsgi --stop ./uwsgi/uwsgi.pid
       ```

   * **Windows**
     * 若使用Tornado，可直接执行`python tornadoApp.py`即可启动服务。

### 2.3 运行环境

> 该项目在`Windows 11 Professional 23H2`和`Ubuntu Server 22.04`上测试通过，主要软件版本如下。

|  配置项   |                版本(Windows)                |                版本(Linux)                |
|:------:|:-----------------------------------------:|:---------------------------------------:|
|   系统   | Windows 11 Professional 23H2 (22631.3447) | Ubuntu 22.04.4 LTS (5.15.0-101-generic) |
| Python |             3.11.8 (Anaconda)             |                 3.10.12                 |
| Flask  |                   3.0.2                   |                  3.0.3                  |
| MySQL  |                  8.0.36                   |         8.0.36-0ubuntu0.22.04.1         |
| Redis  |               Memurai 4.1.1               |              Redis 6.0.16               |

## TODO

* [x] 添加书籍功能
* [x] 圈子成员管理
* [x] 站内私信功能
* [ ] 书籍推荐功能
* [x] 使用Redis缓存
* [ ] 使用Bangumi API为图书增添Tag信息
* [x] 基于大模型的AI助手

## 后记

> 我本有心向明月，奈何明月照沟渠。

* 临近毕业，这个项目以后应该也不会再维护了，把这最后一个版本开源出来，权当为学弟学妹们提供一个参考吧(毕竟这项目做的也不怎么样)，部分设计文档和绘图可参见[docs](./docs)文件夹。
* 同时也劝告大家，如果真的想学些真东西，就不要把多少时间浪费在课堂上，至少在我的大学生涯中，课堂上教的东西多是过时而无用的。多去探索新的技术，多跳出舒适区学习才是“正道”(除非是竞争保研名额的同学)。

## Reference

### 资源

* HTML模板
  * [Dimension | HTML5 UP](https://html5up.net/dimension)
  * [Future Imperfect | HTML5 UP](https://html5up.net/future-imperfect)
* Logo设计：[AIDesign](https://ailogo.qq.com/guide/brandname)
* 第三方API
  * [今日诗词](https://www.jinrishici.com/)
  * [一刻天气](https://tianqiapi.com/index/doc?version=v61)
  * [通义千问](https://help.aliyun.com/zh/dashscope/developer-reference/model-introduction)

### 参考资料

* [欢迎来到 Flask 的世界 — Flask中文文档(2.1.x)](https://dormousehole.readthedocs.io/en/latest/index.html)
* [Flask 教程_w3cschool](https://www.w3cschool.cn/flask/)
* [CSS：层叠样式表 | MDN](https://developer.mozilla.org/zh-CN/docs/Web/CSS)
* [HTTP 响应状态码 - HTTP | MDN](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status)
* [AJAX | 菜鸟教程](https://www.runoob.com/ajax/ajax-tutorial.html)
* [Windows平台：Nginx+Tornado部署Flask_ningx+flask 在windows上搭建-CSDN博客](https://blog.csdn.net/fm0517/article/details/114976122)
* [Flask 生产环境部署（Falsk + uWSGI + nginx） - 今天学了微积分 - 博客园](https://www.cnblogs.com/liurundong/p/18134229)

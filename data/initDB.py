"""部署MySQL的脚本"""
# -*- coding: utf-8 -*-
import os
import subprocess
import warnings

import pymysql
from werkzeug.security import generate_password_hash

from service.Utils import queryConfig

# 获取相关配置信息
db_info = queryConfig("Database")
admin_info = queryConfig("Admin")
ddl_path = os.path.join(os.getcwd(), "ddl.sql").replace("\\", "/")
root_passwd = input("请输入MySQL root用户密码：")

# 连接数据库
print(">>---------------------------------------初始化数据库---------------------------------------<<")
try:
    conn = pymysql.connect(
        host=db_info["Host"],
        port=db_info["Port"],
        user="root",
        password=root_passwd
    )
    cursor = conn.cursor()
except pymysql.err.OperationalError:
    warnings.warn("数据库连接失败，请检查MySQL服务是否正常，或root用户的密码是否正确")
    exit(-1)
print("数据库连接成功，正在使用root账户初始化数据库")

# 创建数据库
try:
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARSET utf8 COLLATE utf8_general_ci;" % db_info["Database"])
    print(f"数据库 {db_info['Database']} 创建成功")
except pymysql.err.OperationalError:
    warnings.warn("数据库创建失败，请检查数据库名称是否合法")
    exit(-1)

# 创建数据库管理员账户
try:
    cursor.execute("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFIED BY '%s';" % (
        db_info["Account"], db_info["Host"], db_info["Password"]))
    print(f"用户'%s'@'%s'创建成功，密码: %s" % (db_info["Account"], db_info["Host"], db_info["Password"]))
except pymysql.err.OperationalError:  # 密码太简单，尝试降低安全级别再创建用户
    cursor.execute("SET global validate_password.policy = 0;")
    conn.commit()
    cursor.execute("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFIED BY '%s';" % (
        db_info["Account"], db_info["Host"], db_info["Password"]))
    warnings.warn(f"密码级别过低，已降低密码安全级别")
    print(f"用户'%s'@'%s'创建成功，密码: %s" % (db_info["Account"], db_info["Host"], db_info["Password"]))

# 为数据库管理员账户授权
cursor.execute(
    "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s';" % (db_info["Database"], db_info["Account"], db_info["Host"]))
print(f"用户'%s'@'%s'授权成功" % (db_info["Account"], db_info["Host"]))
conn.commit()

# 导入DDL
if subprocess.call("mysql -u%s -p%s -h%s -P%s %s < %s" % (
        'root', root_passwd, db_info["Host"], db_info["Port"], db_info["Database"], ddl_path
), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
    print("数据库模板导入成功")
else:
    warnings.warn("数据库模板导入失败")
    exit(-1)

print(">>---------------------------------------创建平台管理员---------------------------------------<<")

# 创建平台管理员账户
try:
    cursor.execute("USE %s;" % db_info["Database"])
    cursor.execute(
        """INSERT INTO user(id,account,password,signature,email,telephone,role) VALUES (%s,%s,%s,%s,%s,%s,%s);""",
        (admin_info["ID"], admin_info["Account"], generate_password_hash(admin_info["Password"]),
         admin_info["Signature"],
         admin_info["E-Mail"], admin_info["Telephone"], "admin")
    )
    conn.commit()
    print(f"管理员账户 {admin_info['Account']} 创建成功，密码: {admin_info['Password']}")
except pymysql.err.IntegrityError:
    warnings.warn("管理员账户创建失败，请检查管理员账户ID是否重复")
    exit(-1)
print("数据库初始化完成")

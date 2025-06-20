from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
def execute_sql(sql,connection_info):
    """
    执行传入的 SQL 语句，并返回查询结果。

    参数:
        sql: 要执行的 SQL 语句（字符串）。
        connection_info: 一个字典，包含数据库连接所需的信息：
            - host: 数据库地址（如 "localhost"）
            - user: 数据库用户名
            - password: 数据库密码
            - database: 数据库名称
            - port: 数据库端口（可选，默认为 3306）
            - charset: 字符编码（可选，默认为 "utf8mb4"）

    返回:
        如果执行的是 SELECT 查询，则返回查询结果的列表；
        如果执行的是 INSERT/UPDATE/DELETE 等非查询语句，则提交事务并返回受影响的行数。
        如果执行过程中出错，则返回 None。
    """
    connection = None
    try:
        # 从 connection_info 中获取各项参数，设置默认值
        host = connection_info.get("host", "localhost")
        user =  connection_info.get("user")
        password = connection_info.get("password")
        database = connection_info.get("database")
        port = connection_info.get("port", 3320)
        charset = connection_info.get("charset", "utf8mb4")

        # 建立数据库连接
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset=charset,
            cursorclass=pymysql.cursors.Cursor  # 可改为 DictCursor 返回字典格式结果
        )

        with connection.cursor() as cursor:
            cursor.execute(sql)
            # 判断是否为 SELECT 查询语句
            if sql.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                connection.commit()  # 非查询语句需要提交事务
                result = cursor.rowcount  # 返回受影响的行数

        return result

    except Exception as e:
        print("执行 SQL 语句时出错：", e)
        return None

    finally:
        if connection:
            connection.close()


@app.route('/execute_sql', methods=['POST'])
def execute_sql_api():
    """
    接口示例：通过 POST 请求传入 SQL 语句和连接信息，返回执行结果。
    请求示例 (JSON):
    {
        "sql": "SELECT * FROM your_table;",
        "connection_info": {
            "host": "localhost",
            "user": "your_username",
            "password": "your_password",
            "database": "your_database"
        }
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400

    sql = data.get("sql")
    connection_info = data.get("connection_info")
    if not sql or not connection_info:
        return jsonify({"error": "缺少sql语句或数据库连接信息"}), 400

    result = execute_sql(sql, connection_info)
    return jsonify({"result": result})


if __name__ == '__main__':
    # 开发环境下可以设置 debug=True，默认在本地5000端口启动服务
    app.run(debug=True)

# # 示例使用
# if __name__ == "__main__":
#     # 示例 SQL 查询语句，请根据实际情况修改
#     sql_query = "select * from candidates where id = 1;"
#     # 数据库连接信息，请根据实际情况修改
#     conn_info = {
#         "host": "localhost",
#         "user": "root",
#         "password": "123456",
#         "database": "ibms",
#         "port": 3306
#     }
#
#     result = execute_sql(sql_query, conn_info)
#     print("执行结果：", result)

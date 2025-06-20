
import json
import requests

def main(sql: str):
    url = "http://127.0.0.1:5000/api/v1/database/execute"
    conn_info = {
        "host": "3.85.167.248",
        "user": "ai_mysql",
        "password": "Qazwsx123",
        "database": "ai_db",
        "port": 3068
    }
    # 构造请求体
    payload = {
        "sql": sql,
        "connection_info": conn_info
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            try:
                return {"result":str(response.json()["result"])}
            except Exception as e:
                return {"result": f"解析响应 JSON 失败: {str(e)}"}
        else:
            return {"result": f"请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"result": str(e)}


def health():
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url="http://127.0.0.0:5000/api/v1/health", headers=headers)
    print(response)

if __name__ == "__main__":
    print(health())
    # print(main("SELECT g.goods_id, g.goods_name, g.price, i.stock_quantity FROM goods g JOIN inventory i ON g.goods_id = i.goods_id"))

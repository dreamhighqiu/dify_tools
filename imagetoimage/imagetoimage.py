from flask import Flask, request, jsonify
import os
import httpx
from openai import OpenAI

app = Flask(__name__)
def get_img_info(url,prompt):
    # Create a custom HTTP client without proxy configuration to avoid conflicts
    http_client = httpx.Client(
        timeout=30.0,
        # Disable environment proxy detection to avoid conflicts
        trust_env=False
    )

    client = OpenAI(
        api_key="bce-v3/ALTAK-dhB3oCeRjka6F1kHHzRP4/5ef96968e3d3d32920869e1856c1b1778967ee59",  # 你的千帆api-key
        base_url="https://qianfan.baidubce.com/v2",  # 千帆modelbulider平台
        http_client=http_client
    )

    # 合并参考图参数到请求
    extra_data = {
        "refer_image": url,
    }
    try:
        response = client.images.generate(
            model="irag-1.0",
            prompt=prompt,
            extra_body=extra_data
        )
        return response.data[0].url
    except Exception as e:
        print(e)

@app.route('/get_img_info', methods=['POST'])
def images_info():
    data = request.get_json()
    if not data:
        return jsonify({"result": "无效的请求数据"}), 400

    url = data.get("url")
    prompt = data.get("prompt")

    if not url :
        return jsonify({"result": "需要输入图片链接"}), 400
    if not prompt :
        return jsonify({"result": "需要输入提示词"}), 400

    result = get_img_info(url, prompt)
    return jsonify({"result": result})



if __name__ == '__main__':
    # 开发环境下可以设置 debug=True，默认在本地5000端口启动服务
    app.run(debug=True, host='0.0.0.0', port=5000)

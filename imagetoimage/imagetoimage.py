from flask import Flask, request, jsonify

from openai import OpenAI

app = Flask(__name__)
def get_img_info(url,prompt):
    client = OpenAI(
        api_key="bce-v3/ALTAK-B39KBUm1GxWtwjcNWxxxxxxxx3490d01a03335",  # 你的千帆api-key
        base_url="https://qianfan.baidubce.com/v2",  # 千帆modelbulider平台
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
    app.run(debug=True)
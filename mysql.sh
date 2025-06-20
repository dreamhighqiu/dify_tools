docker run --name ai-mysql \
  -p 0.0.0.0:3068:3306 \  # 关键修改：绑定到所有网络接口
  -e MYSQL_ROOT_PASSWORD=Qazwsx123 \
  -e MYSQL_DATABASE=ai_db \
  -e MYSQL_USER=ai_mysql \
  -e MYSQL_PASSWORD=Qazwsx123 \
  -d mysql:latest
# Lambdaのレイヤー作成方法
## 公式イメージの取得
```
docker pull amazon/aws-sam-cli-build-image-python3.9
# https://hub.docker.com/r/amazon/aws-sam-cli-build-image-python3.9
```
## コンテナに入る
```
docker run -it -v $(pwd):/var/task amazon/aws-sam-cli-build-image-python3.9:latest
```
## 必要なライブラリをインストール
pip install pandas -t ./python
pip install sshtunnel -t ./python
pip install pymysql -t ./python
## zip化
```
zip -r lambda-layer.zip ./python
```
## マネコンで作業
1. s3アップロード
2. httpsのURL取得
3. zipファイルをアップロードしてレイヤー作成
4. 関数側でレイヤーを指定
## 参考
https://pomblue.hatenablog.com/entry/2021/06/08/230146

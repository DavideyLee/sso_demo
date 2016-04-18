# sso_demo
sso_demo

# 安装步骤

1、先把sso_demo克隆到本地
2、进入sso_demo目录执行pip install -r requirements.txt
3、配置好config.py，本地运行默认使用的配置是DevelopmentConfig，这里要配置passport的链接参数：

  class DevelopmentConfig(Config):
      DEBUG = True
      SECRET_KEY = "yiwerwerwfdwsdsf"
      SSO_URL = "http://127.0.0.1:8005" #passport访问地址
      SSO_APP_SECRET = "pwFdm28hNtmNstGx" #应用的key，通过passport后台获取
      SSO_APP_ID = 9 #应用id，通过passport后踢获取
      SSO_ENABLE = True
      
4、在程序根目录下通过执行python manage.py运行服务

5、访问web即可

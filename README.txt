1、首先你得有个VPS，可以使用免费一年的googld clud
2、把项目代码在local和vps两个地方都clone一份
3、修改user_config.json，两个地方保持一致。根据文件中的提示实际填写
4、在vps执行insatll_ss.sh local执行install_ss_client.sh分别安装ss_server和ss_client
5、修改firefox网路配置，指向local的7788端口(默认)即可。

PS:
    1、如果安装中出错，请自行排查
    2、目前ss_server只支持Ubuntu17.04，只在这个版本测试通过，Ubuntu其他版本也许可以
    3、vps中会安装3个server 分别是ss ss_no_change ss_hub
    4、如果user_config.json什么都不填写，那么就会使用默认的
    5、但是install_ss_client.sh时，必须要把vps公网IP填写进入user_config.json

ss:               原版ss，动态修改cipher和密码，端口
ss_no_change:     原版ss，cipher不变，兼容于目前的各种原版客户端
ss_hub:           原版ss master分之，cipher不变，增加了gcm和poly加密

使用方法：
    1、首先需要访问apache的https页面，先allow.sh允许本机访问vps
    2、查看ss_hub 或者 ss_no_change 相关密码，加密方式，端口
    3、配置客户端，填入相关信息即可。


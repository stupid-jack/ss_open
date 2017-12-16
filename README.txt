1、首先你得有个VPS，可以使用免费一年的googld clud
2、把项目代码在local和vps两个地方都clone一份
3、修改user_config.json，两个地方保持一致。根据文件中的提示实际填写
4、在vps执行insatll_ss.sh local执行install_ss_client.sh分别安装ss_server和ss_client
5、修改firefox网路配置，只想local的7788端口(默认)即可。


PS:
    1、如果安装中出错，请自行排查
    2、目前ss_server只支持Ubuntu17.04，只在这个版本测试通过，Ubuntu其他版本也许可以
    3、vps中会安装3个server 分别是ss ss_no_change ss_hub

ss:               原版ss，动态修改cipher和密码，端口
ss_no_change:     原版ss，cipher不变，兼容于目前的各种原版客户端
ss_hub:           原版ss master分之，cipher不变，增加了gcm和poly加密

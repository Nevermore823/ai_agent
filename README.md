# 基于wechaty的微信agent

这是一个基于 WeChaty 的微信 Agent，利用 AppleScript 和 Mac 版微信客户端制作的简易版微信 Agent。该项目可以实现以下功能：

- text2sql
- text2cypher
- 总结微信公众号文章
- 获取指定地点天气

目前利用个人微信 + WeChaty 实现 ChatBot 的方案，并且部署在本地 Mac 机器上。

## 安装
根据 `requirements.txt`安装所需依赖。
```
pip install -r requirements.txt
```

## 运行
```
python main.py [prompt]
```

## 注意
1. 最多支持10轮对话内容，超过10轮的对话会丧失前序记忆；
2. 使用text2sql, text2cypher中，需要先将数据库配置到`database/db_base.py`中，并且将结构型数据库的DDL或neo4j的schema description配置到`database/DDL.py`中；
3. `agent_base/tools,py`中定义了3个tool_uses。text2sql和text2cypher需要替换prompt中的DDL；
4. 项目中包含了agent数据库的建表语句，可根据需要自行配置；

## 局限
- 无法获取用户唯一 ID，openid 和 unionid 都不可以，只有昵称或备注；
- 无法获取消息的唯一 ID，只能处理一条删一条；
- 处理速度慢，如果群聊的速度大于 AppleScript 的运行速度，那就会出现消息永远无法被处理的情况；
- 必须用一台Mac来Host，当然也可以通过开虚拟机的方式让一台 Mac 运行多个机器人；

## todo
- [ ] 支持处理图片、语音、链接等消息；
- [ ] 支持发送图片、文件；


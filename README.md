<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-dancecube/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-dancecube/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-dancecube

_✨ 舞立方插件：提供舞立方战力分析等基础功能 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/1v7w/nonebot-plugin-dancecube.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-dancecube">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-dancecube.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

目前支持二维码登录、战力分析、战力分析(包含自制谱)、战绩最好的30首ap歌曲、获取指定歌曲id的个人成绩、自动更新官方曲目封面。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-dancecube

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-dancecube
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-dancecube
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-dancecube
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-dancecube
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_dancecube"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| COVER_UPDATE_CRON | 否 | 0 3 * * * | cron格式；默认每天凌晨3点更新官方曲目封面 |
|SUPERUSERS|否|-|超级用户/管理员|
|NICKNAME|否|nisky|机器人名字，生成图片最低下会展示|

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| /dc | 群员 | 否 | 私聊/群聊 | 获取指令帮助 |
| /dc login | 群员 | 否 | 私聊 | 二维码登录 |
| /dc myrt | 群员 | 否 | 群聊 | 获取战力分析 |
| /dc myrtall | 群员 | 否 | 群聊 | 获取战力分析(含自制谱) |
| /dc ap30 | 群员 | 否 | 群聊 | 获取ap战绩最好的30首 |
| /dc updatecover | 超级用户 | 否 | 私聊/群聊 | 更新官方曲目封面 |

### 效果图


**/dc myrt**
![myrt](https://private-user-images.githubusercontent.com/25610914/575376467-021edb83-5a6c-4629-99a5-e5e419761a55.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzU2NjM1NjIsIm5iZiI6MTc3NTY2MzI2MiwicGF0aCI6Ii8yNTYxMDkxNC81NzUzNzY0NjctMDIxZWRiODMtNWE2Yy00NjI5LTk5YTUtZTVlNDE5NzYxYTU1LmpwZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA0MDglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNDA4VDE1NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTY2NDc1NTg2Y2MxMzUxZTdkNDk2M2MzNmY3OGU4NjhlYmU4MGFlNWE4NjNlODhhZjRjYzViYWZiZGQ1ODFlYzEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.JpVV5dISyef-l5PMuJS5k0L_CvDdOuOLtP2vGLY2yvY)

**/dc ap30**
![ap30](https://private-user-images.githubusercontent.com/25610914/575376735-63abf0b3-4e46-4e3f-8e99-c8cb442daf70.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzU2NjM1NjIsIm5iZiI6MTc3NTY2MzI2MiwicGF0aCI6Ii8yNTYxMDkxNC81NzUzNzY3MzUtNjNhYmYwYjMtNGU0Ni00ZTNmLThlOTktYzhjYjQ0MmRhZjcwLmpwZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA0MDglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNDA4VDE1NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTUzZDczYjkxOTA1YjMzZjVjNjI4ODExMDE5NjhiZDA2ZWIyMTdjZDE1MTM4ZTVmODcxNzY0MTZkZmRlMzc2YWYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.m10nGaxpK1JYJ8Ax5zOFn6kbUalDJdb4HUD2tt5h-xc)

**/dc song 6354**
![song 6354](https://private-user-images.githubusercontent.com/25610914/575376771-ce0049f3-80eb-4c02-9079-f3a794f1762a.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzU2NjM1NjIsIm5iZiI6MTc3NTY2MzI2MiwicGF0aCI6Ii8yNTYxMDkxNC81NzUzNzY3NzEtY2UwMDQ5ZjMtODBlYi00YzAyLTkwNzktZjNhNzk0ZjE3NjJhLmpwZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA0MDglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNDA4VDE1NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU3ZGE3NGIxMDEzNTA2OGM1NWNiNDFkOGVmN2YxY2Y5ZTJkZjNiYzg5ZTM0NTYwNGE5MTg0ZTVjNWU4OGUyOGYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.WEUPNeNyOALOGqWIw5ZZvCXZmnF5Jla0_BqUw_RuPoY)

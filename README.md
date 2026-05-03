<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
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

目前支持二维码/手机号登录、战力分析、战力分析(包含自制谱)、战绩最好的30首ap歌曲(可选官铺、自制谱)、获取指定歌曲id的个人成绩、自动更新官方曲目封面。

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
| DANCECUBE_COVER_UPDATE_CRON | 否 | 0 3 * * * | cron格式；默认每天凌晨3点更新官方曲目封面 |
| DANCECUBE_BOTNAME | 否 | nisky | 机器人名字，生成图片底部会展示 |
| SUPERUSERS | 否 | - | Nonebot配置，超级用户/管理员，仅超级用户可主动触发更新官方曲目封面 |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| /dc | 群员 | 否 | 私聊/群聊 | 获取指令帮助 |
| /dc login | 群员 | 否 | 私聊 | 登录舞立方账号，交互式选择登录方式 |
| /dc myrt | 群员 | 否 | 群聊 | 获取战力分析 |
| /dc myrtall | 群员 | 否 | 群聊 | 获取战力分析(含自制谱) |
| /dc ap30 [o/c] | 群员 | 否 | 群聊 | 获取最好的30首AP战绩(默认混合, o官方, c自制) |
| /dc song [id] | 群员 | 否 | 群聊 | 获取歌曲id为[id]的个人成绩 |
| /dc random [level] | 群员 | 否 | 群聊 | 随机一首官铺(可指定等级) |
| /dc updatecover | 超级用户/管理员 | 否 | 私聊/群聊 | 更新官方曲目封面 |

### 效果图


**/dc myrt**

![myrt](https://raw.githubusercontent.com/1v7w/1v7w-image-bed/main/img220260413193144442.jpg)

**/dc ap30**

![ap30]https://raw.githubusercontent.com/1v7w/1v7w-image-bed/main/img220260413193141025.jpg)

**/dc song 6354**

![song 6354](https://raw.githubusercontent.com/1v7w/1v7w-image-bed/main/img220260413193130199.jpg)

### 更新历史

#### v0.2.0
- 增加了随机一首官铺的功能
- /dc song中增加了没有游玩记录的谱面难度显示

#### v0.1.7
- 更改配置项
- 移除templates文件夹的复制

#### v0.1.6
- 战绩显示增加战队名、战队职位
- 战绩显示增加游玩歌曲数目

#### v0.1.5
- ap30允许选择官铺or自制谱。
- 添加手机号登录功能
- 修复二维码登录的一些bug

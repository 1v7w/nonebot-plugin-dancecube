from nonebot import on_command, on_message, require, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.log import logger

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")

from .download import http_get_raw, http_post_raw
from .tokens import Token, TokenManager, TokenBuilder
from .utils import calc_time_difference
from .recording import MusicInfoManager
from .userinfo import UserInfo
from .pic import create_rating_analysis_img, create_ap30_img, create_single_song_record_img, update_official_covers
from .config import Config, user_tokens_file


from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="舞立方插件",
    description="提供舞立方战力分析等基础功能",
    usage="发送【/dc】获取帮助",

    type="application",     
    homepage="https://github.com/1v7w/nonebot-plugin-dancecube",

    config=Config,
    
    supported_adapters={"~onebot.v11"},
)

SUPERUSERS = set(get_driver().config.superusers)

dc = on_command('dc', aliases={'dancecube', '舞立方'}, priority=50, block=True)

HELP_TEXT = (
    "舞立方bot使用帮助\n"
    "/dc myrt 获取战力分析\n"
    "/dc myrtall 获取战力分析(包含自制谱)\n"
    "/dc ap30 [o/c] 获取最好的30首AP战绩(默认混合, o官方, c自制)\n"
    "/dc song [id] 获取歌曲id为[id]的个人成绩\n"
    "/dc login 登录舞立方账号(仅私聊可用)\n"
    # "/dc updatecover 更新官方曲目封面(仅机器人管理员可用)\n"
)

@dc.handle()
async def handle_dc(bot: Bot, event: MessageEvent):
    qq_userid = event.user_id
    args = str(event.get_plaintext()).split(' ')
    cmd = args[1].lower() if len(args) > 1 else None

    # 帮助
    if cmd in (None, 'help', 'h'):
        await dc.finish(HELP_TEXT)

    # 登录
    if cmd == 'login':
        if event.message_type != 'private':
            await dc.finish('请私聊发送"/dc login"来使用登录舞立方账号。')
        _phone_login_sessions[qq_userid] = {'step': 'wait_choice'}
        await dc.finish("请选择登录方式：\n1. 二维码登录\n2. 手机号登录\n\n请回复序号（1或2）：")

    # 更新官方曲目封面（仅超级用户）
    if cmd == 'updatecover':
        if str(qq_userid) not in SUPERUSERS:
            await dc.finish('仅超级用户/机器人管理员可使用此命令。')
        result = await update_official_covers()
        await dc.finish(result)

    # 以下命令仅限群聊
    if event.message_type != 'group':
        await dc.finish('本命令仅限群聊中使用。')

    # 检查 token
    token_or_msg = await _check_token(qq_userid)
    if isinstance(token_or_msg, str):
        await dc.finish(token_or_msg)

    token = token_or_msg
    music_info_manager = MusicInfoManager(token.user_id, token.access_token)
    userinfo = await UserInfo.fetch_user_data(token.access_token, token.user_id)

    if cmd == 'ap30':
        if len(args) >= 3:
            img_bytes = await create_ap30_img(userinfo, music_info_manager, args[2])
        else:
            img_bytes = await create_ap30_img(userinfo, music_info_manager)
        await dc.finish(MessageSegment.image(img_bytes))

    elif cmd == 'myrt':
        img_bytes = await create_rating_analysis_img(userinfo, music_info_manager)
        await dc.finish(MessageSegment.image(img_bytes))

    elif cmd == 'myrtall':
        img_bytes = await create_rating_analysis_img(userinfo, music_info_manager, is_official=False)
        await dc.finish(MessageSegment.image(img_bytes))

    elif cmd == 'song':
        if len(args) < 3:
            await dc.finish('请指定歌曲id，例如: /dc song 10009')
        song_id = args[2]
        success, result = await create_single_song_record_img(userinfo, music_info_manager, song_id)
        if success:
            await dc.finish(MessageSegment.image(result))
        else:
            await dc.finish(str(result))

    else:
        await dc.finish(HELP_TEXT)
        
async def _check_token(qq_userid: int) -> Token | str:
    """检查用户 token 状态，返回 token 或错误消息"""
    token = await TokenManager(user_tokens_file).get_token_by_qq(qq_userid)
    if token is None:
        return '还没有登录。\n请私聊我发送"/dc login"来获取二维码登录吧。'
    if calc_time_difference(token.expires) < 600:
        return '登录过期。\n请私聊我发送"/dc login"来获取二维码登录吧。'
    return token
        
# ========== 手机号登录会话状态 ==========
_phone_login_sessions: dict[int, dict] = {}

async def _in_phone_login(event: MessageEvent) -> bool:
    """检查用户是否在手机号登录流程中"""
    return event.message_type == 'private' and event.user_id in _phone_login_sessions

phone_login = on_message(rule=_in_phone_login, priority=45, block=False)
@phone_login.handle()
async def handle_phone_login(bot: Bot, event: MessageEvent):
    qq_userid = event.user_id
    session = _phone_login_sessions.get(qq_userid)
    if session is None:
        await phone_login.finish()

    text = str(event.get_plaintext()).strip()

    # 如果用户发送了 /dc 命令，清除会话让 dc handler 处理
    if text.lower().startswith('/dc') or text.lower().startswith('/dancecube') or text.lower().startswith('/舞立方'):
        del _phone_login_sessions[qq_userid]
        await phone_login.finish()

    step = session['step']

    if step == 'wait_choice':
        if text == '1':
            # 二维码登录
            del _phone_login_sessions[qq_userid]
            token_builder = TokenBuilder()
            qr_code_url = await token_builder.get_qrcode()
            if not qr_code_url:
                await phone_login.finish("获取二维码失败，请稍后重试 /dc login")
            await token_builder.get_token(qq_userid)
            await phone_login.finish(
                MessageSegment.image(qr_code_url) + "\n请在2分钟内微信扫描二维码"
            )
        elif text == '2':
            # 手机号登录
            session['step'] = 'wait_phone'
            await phone_login.finish("请输入手机号：")
        else:
            del _phone_login_sessions[qq_userid]
            await phone_login.finish("已取消登录。")

    elif step == 'wait_phone':
        phone = text
        # 获取图形验证码
        rep = await http_get_raw(
            "https://dancedemo.shenghuayule.com/Dance/api/Common/GetGraphCode",
            params={"phone": phone}
        )
        if rep.status_code != 200:
            del _phone_login_sessions[qq_userid]
            await phone_login.finish("获取图形验证码失败，请重新发送 /dc login")

        # 响应是带双引号的 base64 字符串，去掉首尾双引号
        graph_code_b64 = rep.text.strip().strip('"')

        session['phone'] = phone
        session['step'] = 'wait_graph_code'

        await phone_login.finish(
            MessageSegment.image(f"base64://{graph_code_b64}") + "请输入图形验证码："
        )

    elif step == 'wait_graph_code':
        graph_code = text
        phone = session['phone']

        # 发送短信验证码请求
        rep = await http_get_raw(
            "https://dancedemo.shenghuayule.com/Dance/api/Common/GetSMSCode",
            params={"phone": phone, "graphCode": graph_code}
        )

        # 成功则响应没有内容
        if rep.status_code == 200 and not rep.text.strip():
            session['step'] = 'wait_sms_code'
            await phone_login.finish("短信验证码已发送，请输入收到的短信验证码：")
        else:
            error_msg = "图形验证码错误"
            try:
                data = rep.json()
                error_msg = data.get("Message", "图形验证码错误")
            except Exception:
                pass
            del _phone_login_sessions[qq_userid]
            await phone_login.finish(f"图形验证码验证失败：{error_msg}\n请重新发送 /dc login")

    elif step == 'wait_sms_code':
        sms_code = text
        phone = session['phone']

        # 使用手机号和短信验证码登录
        rep = await http_post_raw(
            "https://dancedemo.shenghuayule.com/Dance/token",
            data={
                "client_type": "phone",
                "grant_type": "client_credentials",
                "client_id": phone,
                "client_secret": sms_code,
            }
        )

        del _phone_login_sessions[qq_userid]
        logger.info(f"status_code:{rep.status_code}")
        if rep.status_code != 200:
            await phone_login.finish("登录失败，请重新发送 /dc login")

        try:
            data = rep.json()
        except Exception:
            await phone_login.finish("登录失败，请重新发送 /dc login")

        if "error" in data:
            await phone_login.finish("短信验证码错误，请重新发送 /dc login")

        token = Token.from_dict(data)
        token.qq = str(qq_userid)
        await TokenManager(user_tokens_file).update_token(token)
        await phone_login.finish(
            f"登录成功。登录的舞立方ID：{token.user_id}\n如果不是你的舞立方ID号，请重新登录！"
        )

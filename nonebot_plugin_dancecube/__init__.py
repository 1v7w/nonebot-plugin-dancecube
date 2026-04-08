from nonebot import on_command, require, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")

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
    "/dc myrt 获取战力分析\n"
    "/dc myrtall 获取战力分析(包含自制谱)\n"
    "/dc ap30 获取战绩最好的30首ap歌曲\n"
    "/dc song [id] 获取歌曲id=[id]的个人成绩\n"
    "/dc login 获取登录二维码(仅私聊可用)\n"
    "/dc updatecover 更新官方曲目封面(仅超级用户)\n"
    "/dc help 显示本帮助"
)


async def _check_token(qq_userid: int) -> Token | str:
    """检查用户 token 状态，返回 token 或错误消息"""
    token = await TokenManager(user_tokens_file).get_token_by_qq(qq_userid)
    if token is None:
        return '还没有登录。\n请私聊我发送"/dc login"来获取二维码登录吧。'
    if calc_time_difference(token.expires) < 600:
        return '登录过期。\n请私聊我发送"/dc login"来获取二维码登录吧。'
    return token


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
        token_builder = TokenBuilder()
        qr_code_url = await token_builder.get_qrcode()
        await token_builder.get_token(qq_userid)
        await dc.finish(user_id=qq_userid, message=MessageSegment.image(qr_code_url) + "请在2分钟内微信扫描二维码")

    # 更新官方曲目封面（仅超级用户）
    if cmd == 'updatecover':
        if str(qq_userid) not in SUPERUSERS:
            await dc.finish('仅超级用户可使用此命令。')
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
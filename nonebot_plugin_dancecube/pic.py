import asyncio
import os
from datetime import datetime

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_htmlrender import template_to_pic

from .download import http_get, http_get_image
from .recording import MusicInfoManager, RankMusicInfo, LastPlayMusicInfo
from .userinfo import UserInfo
from .utils import LEVEL_TYPE_TO_STR, LEVEL_TYPE_LIST
from .config import cover_dir, templates_dir, dc_config, thumb_dir, driver

# 图片生成配置
IMAGE_DEVICE_SCALE_FACTOR = 1  # 降低设备缩放因子以减小图片体积
IMAGE_JPEG_QUALITY = 80  # JPEG 质量（0-100）
COVER_MAX_SIZE = 300  # 封面图最大边长（像素），用于压缩已下载封面

async def get_music_cover_path(music_id: int) -> str:
    """获取音乐封面缩略图路径（用于网页渲染），如原图不存在则下载，然后生成缩略图。
    下载失败时直接返回默认封面，不复制到音乐封面路径，以便后续定时任务仍可下载真正的封面。"""
    cover_path = cover_dir / f"{music_id}.jpg"
    default_cover_path = cover_dir / "-1.jpg"
    default_thumb_path = thumb_dir / "-1.jpg"
    thumb_path = thumb_dir / f"{music_id}.jpg"

    # 原图不存在则尝试下载
    if not os.path.exists(cover_path):
        logger.debug(f"下载封面: music {music_id}")
        await _download_and_save_cover(music_id)

    # 下载失败则返回默认封面缩略图（不复制到音乐封面路径）
    if not os.path.exists(cover_path):
        if not os.path.exists(default_thumb_path):
            _generate_thumbnail(default_cover_path, default_thumb_path)
        return str(default_thumb_path)

    # 缩略图不存在则从原图生成
    if not os.path.exists(thumb_path):
        _generate_thumbnail(cover_path, thumb_path)

    return str(thumb_path)


async def _download_and_save_cover(music_id: int) -> None:
    """下载自制谱封面并保存原图"""
    get_goods_info_api = "https://dancedemo.shenghuayule.com/Dance/api/MusicData/GetGoodsInfo"
    rep = await http_get(get_goods_info_api, params={"musicId": music_id})
    if rep is None:
        return

    for list_file in rep.get("ListFile", []):
        if list_file.get("FileType") == 3:
            image_url = list_file.get("Url")
            img = await http_get_image(image_url)
            _save_cover(img, cover_dir / f"{music_id}.jpg")
            return


def _save_cover(img, save_path) -> None:
    """保存封面原图（不压缩）"""
    from PIL import Image
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(save_path, "JPEG", quality=95, optimize=True)


def _generate_thumbnail(src_path, thumb_path, max_size=COVER_MAX_SIZE) -> None:
    """从原图生成压缩缩略图，用于网页渲染"""
    from PIL import Image
    thumb_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_path)
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(thumb_path, "JPEG", quality=85, optimize=True)


async def _generate_score_entry(music_info: RankMusicInfo | LastPlayMusicInfo) -> dict:
    """生成单曲数据字典"""
    level_type_str = LEVEL_TYPE_TO_STR[music_info.level_type]
    cover_path = await get_music_cover_path(music_info.id)
    return {
        "songName": music_info.name,
        "coverUrl": cover_path,
        "id": music_info.id,
        "difficulty": level_type_str[-2:],      # 基础、进阶、专家、大师、传奇
        "level": music_info.level,
        "levelType": level_type_str[:-3],        # 经典/show
        "accuracy": music_info.accuracy,         # 0.00~100.00
        "rating": int(music_info.rating),
        "playTime": music_info.record_time,
    }


def _base_template_data(user_info: UserInfo) -> dict:
    """生成模板通用数据"""
    return {
        "generatedTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "playerName": user_info.username,
        "avatarUrl": user_info.head_img_url,
        "powerValue": user_info.rating,
        "points": user_info.score,
        "playedNumbers": user_info.played_numbers,
        "teamName": user_info.team_name,
        "teamPosition": user_info.team_position,
        "botName": dc_config.dancecube_botname,
    }


async def _render_template(template_name: str, template_data: dict,
                           viewport_width: int = 1200, viewport_height: int = 100) -> bytes:
    """通用模板渲染方法，包含图片优化"""
    img_bytes = await template_to_pic(
        template_path=str(templates_dir),
        template_name=template_name,
        templates=template_data,
        pages={
            "viewport": {"width": viewport_width, "height": viewport_height},
        },
        wait=2000,
        type="jpeg",
        quality=IMAGE_JPEG_QUALITY,
        device_scale_factor=IMAGE_DEVICE_SCALE_FACTOR,
    )
    return img_bytes


def _take_n(items: list, n: int) -> list:
    """取列表前 n 项"""
    return items[:n]


async def create_rating_analysis_img(user_info: UserInfo, music_info_manager: MusicInfoManager,
                                      is_official: bool = True) -> bytes:
    """生成战力分析图片"""
    if is_official:
        await music_info_manager.get_all_rank_official_list()
        all_rank_list = music_info_manager.all_rank_official_list
    else:
        await music_info_manager.get_all_rank_list()
        all_rank_list = music_info_manager.all_rank_list

    await music_info_manager.get_recent_record_list()

    template_data = _base_template_data(user_info)
    template_data["pageTitle"] = "舞立方战力分析" if is_official else "舞立方战力分析(含自制谱)"
    template_data["best30"] = [await _generate_score_entry(m) for m in _take_n(all_rank_list, 30)]
    template_data["recent30"] = [await _generate_score_entry(m) for m in _take_n(music_info_manager.recent_record_list, 30)]
    template_data["best30Count"] = len(template_data["best30"])
    template_data["recent30Count"] = len(template_data["recent30"])

    return await _render_template("myrt.html", template_data)


async def create_ap30_img(user_info: UserInfo, music_info_manager: MusicInfoManager, mode: str = "all") -> bytes:
    """生成 AP30 图片"""
    template_data = _base_template_data(user_info)
    
    await music_info_manager.get_all_rank_list()
    if mode in { "official", "o", "官铺" }:
        all_ap_list = [x for x in music_info_manager.all_rank_list if x.accuracy == 100 and x.is_official]
        template_data["pageTitleEnding"] = "(官铺)"
    elif mode in { "custom", "c", "自制谱" }:
        all_ap_list = [x for x in music_info_manager.all_rank_list if x.accuracy == 100 and not x.is_official]
        template_data["pageTitleEnding"] = "(自制谱)"
    else:
        all_ap_list = [x for x in music_info_manager.all_rank_list if x.accuracy == 100]
        template_data["pageTitleEnding"] = "(官铺+自制谱)"
        
    
    template_data["apCount"] = len(all_ap_list)
    template_data["apListCount"] = min(len(all_ap_list), 30)
    template_data["apList"] = [await _generate_score_entry(m) for m in _take_n(all_ap_list, 30)]

    return await _render_template("ap30.html", template_data)


async def create_single_song_record_img(user_info: UserInfo, music_info_manager: MusicInfoManager,
                                         song_id: str) -> tuple[bool, bytes | str]:
    """生成单曲成绩图片，返回 (成功标志, 图片bytes或错误消息)"""
    await music_info_manager.get_all_rank_list()
    rank_list = sorted(
        [x for x in music_info_manager.all_rank_list if str(x.id) == str(song_id)],
        key=lambda x: x.level_type,
    )
    if not rank_list:
        return False, f"未找到id:{song_id}游玩记录，请检查歌曲id是否正确。"

    cover_path = await get_music_cover_path(rank_list[0].id)

    template_data = _base_template_data(user_info)
    template_data["songName"] = rank_list[0].name
    template_data["songId"] = rank_list[0].id
    template_data["coverUrl"] = cover_path
    template_data["records"] = []

    # 构建各难度记录
    rank_dict = {r.level_type: r for r in rank_list}
    for lt in LEVEL_TYPE_LIST:
        level_type_str = LEVEL_TYPE_TO_STR[lt]
        difficulty = level_type_str[-2:]
        level_type_prefix = level_type_str[:-3]
        if lt in rank_dict:
            r = rank_dict[lt]
            template_data["records"].append({
                "hasRecord": True,
                "difficulty": difficulty,
                "levelType": level_type_prefix,
                "level": r.level,
                "accuracy": r.accuracy,
                "combo": r.combo,
                "miss": r.miss,
                "rating": int(r.rating),
                "playTime": r.record_time,
            })
        else:
            template_data["records"].append({
                "hasRecord": False,
                "difficulty": difficulty,
                "levelType": level_type_prefix,
            })

    img_bytes = await _render_template("song.html", template_data,
                                        viewport_width=800, viewport_height=900)
    return True, img_bytes


async def update_official_covers() -> str:
    """更新官方曲目封面"""
    logger.info("开始更新官方曲目封面")

    music_ranking_api = "https://dancedemo.shenghuayule.com/Dance/api/User/GetMusicRankingNew"
    page_size = 50
    downloaded = 0
    skipped = 0
    failed = 0
    api_max_retries = 5
    consecutive_failures = 0
    max_consecutive_failures = 3  # 连续失败页数上限，超过则跳到下一类别

    try:
        for music_index in range(2, 7):  # 2-6: 国语、粤语、韩语、欧美、其它
            page = 1
            consecutive_failures = 0
            while True:
                # 请求失败时自动重试，直到成功获取数据
                rep = None
                for retry in range(1, api_max_retries + 1):
                    rep = await http_get(
                        music_ranking_api,
                        params={"musicIndex": music_index, "page": page, "pagesize": page_size},
                    )
                    if rep is not None:
                        break
                    logger.warning(
                        f"获取官方曲目列表失败: musicIndex={music_index}, page={page}, "
                        f"第 {retry}/{api_max_retries} 次重试"
                    )
                    if retry < api_max_retries:
                        await asyncio.sleep(retry)

                if rep is None:
                    consecutive_failures += 1
                    logger.error(
                        f"获取官方曲目列表最终失败: musicIndex={music_index}, page={page}，"
                        f"连续失败 {consecutive_failures}/{max_consecutive_failures} 次"
                    )
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(f"连续 {max_consecutive_failures} 页获取失败，跳到下一类别")
                        break
                    page += 1
                    continue

                consecutive_failures = 0  # 成功后重置连续失败计数

                music_list = rep.get("List", [])
                if not music_list:
                    break  # 无更多数据，下一类别

                for music in music_list:
                    music_id = music.get("MusicID")
                    cover_url = music.get("Cover")
                    cover_path = cover_dir / f"{music_id}.jpg"

                    if os.path.exists(cover_path):
                        skipped += 1
                        continue

                    if not cover_url:
                        failed += 1
                        continue

                    # 去掉 Cover URL 末尾的尺寸后缀（如 "/200"）以获取原图
                    if cover_url.endswith("/200"):
                        cover_url = cover_url[:-4]

                    try:
                        img = await http_get_image(cover_url)
                        _save_cover(img, cover_path)
                        downloaded += 1
                        logger.debug(f"下载官方封面: {music_id}")
                    except Exception as e:
                        failed += 1
                        logger.debug(f"下载官方封面失败: {music_id}, {e}")

                page += 1

    except Exception as e:
        logger.error(f"更新官方封面时发生错误: {e}")
        return f"官方曲目封面更新出错：{e}\n已下载 {downloaded} 张，跳过 {skipped} 张，失败 {failed} 张"

    logger.info(f"官方曲目封面更新完成: 下载 {downloaded}, 跳过 {skipped}, 失败 {failed}")
    return f"官方曲目封面更新完成！\n新下载: {downloaded} 张\n已存在: {skipped} 张\n失败: {failed} 张"


@driver.on_startup
async def _register_cover_update_job():
    """根据配置的 cron 表达式注册定时更新官方封面任务"""
    from apscheduler.triggers.cron import CronTrigger
    trigger = CronTrigger.from_crontab(dc_config.dancecube_cover_update_cron)
    scheduler.add_job(
        update_official_covers,
        trigger,
        id="update_official_covers",
        replace_existing=True,
    )
    logger.info(f"已注册定时更新官方封面任务，cron: {dc_config.dancecube_cover_update_cron}")
    
@driver.on_startup
async def _ensure_default_cover() -> None:
    """确保默认封面 cover/-1.jpg 存在，如不存在则生成占位图"""
    default_cover_path = cover_dir / "-1.jpg"
    if default_cover_path.exists():
        return

    from PIL import Image, ImageDraw, ImageFont

    cover_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (175, 202), color=(180, 180, 180))
    draw = ImageDraw.Draw(img)
    text = "MISSING"
    font = ImageFont.load_default(size=41)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (175 - text_w) // 2
    y = (202 - text_h) // 2
    draw.text((x, y), text, fill=(80, 80, 80), font=font)
    img.save(default_cover_path, "JPEG", quality=85)
    logger.info("已生成默认占位封面 cover/-1.jpg")

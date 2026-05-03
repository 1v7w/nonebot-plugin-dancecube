from pathlib import Path

from nonebot import get_driver, get_plugin_config, require
require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_plugin_data_dir
from pydantic import BaseModel

driver = get_driver()

class Config(BaseModel):
    dancecube_botname: str = 'nisky'                # 机器人名字，生成图片底部会展示
    dancecube_cover_update_cron: str = "0 3 * * *"  # 定时更新官方封面的 cron 表达式，默认每天凌晨3点


dc_config = get_plugin_config(Config)

data_dir: Path = get_plugin_data_dir()
data_dir.mkdir(parents=True, exist_ok=True)

user_tokens_file: Path = data_dir / 'user_tokens.json'
official_cache_file: Path = data_dir / 'official_music_list.json'
cover_dir: Path = data_dir / 'cover'
templates_dir: Path = Path(__file__).resolve().parent / "templates"

thumb_dir = cover_dir / "thumb" # 封面缩略图目录（用于网页渲染）
thumb_dir.mkdir(parents=True, exist_ok=True)

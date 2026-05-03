import json
from datetime import date

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from .config import data_dir, driver, official_cache_file
from .download import http_get

OFFICIAL_MUSIC_API = "https://dancedemo.shenghuayule.com/Dance/Music/GetMusicList"


class OfficialMusic:
    __slots__ = ("music_id", "name", "difficulties")

    def __init__(self, music_id: int, name: str, difficulties: list[dict]):
        self.music_id = music_id
        self.name = name
        self.difficulties = difficulties

    def to_dict(self) -> dict:
        return {"MusicID": self.music_id, "Name": self.name, "MusicItemList": self.difficulties}

    @classmethod
    def from_dict(cls, data: dict) -> "OfficialMusic":
        return cls(data["MusicID"], data["Name"], data.get("MusicItemList", []))

    def get_level_map(self) -> dict[int, int]:
        """返回 {MusicLevNew: MusicLevel}，仅包含存在的难度（MusicLevel != -1）"""
        return {
            d["MusicLevNew"]: d["MusicLevel"]
            for d in self.difficulties
            if d.get("MusicLevNew") is not None and d.get("MusicLevel", -1) != -1
        }


def _load_cache() -> tuple[date | None, list[OfficialMusic]]:
    try:
        with open(official_cache_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cache_date = date.fromisoformat(raw["date"])
        music_list = [OfficialMusic.from_dict(m) for m in raw["music_list"]]
        return cache_date, music_list
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return None, []


def _save_cache(music_list: list[OfficialMusic]) -> None:
    data = {
        "date": date.today().isoformat(),
        "music_list": [m.to_dict() for m in music_list],
    }
    with open(official_cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def update_official_music_cache() -> list[OfficialMusic]:
    logger.info("开始更新官铺列表缓存")
    rep = await http_get(OFFICIAL_MUSIC_API, params={"getNotDisplay": True, "getitem": True})
    if rep is None:
        logger.error("获取官铺列表失败")
        return []

    music_list = [OfficialMusic.from_dict(m) for m in rep]
    _save_cache(music_list)
    logger.info(f"官铺列表缓存更新完成，共 {len(music_list)} 首歌")
    return music_list


_official_music_index: dict[int, OfficialMusic] = {}
_official_music_list: list[OfficialMusic] = []


def _ensure_index(music_list: list[OfficialMusic]) -> None:
    global _official_music_index, _official_music_list
    if _official_music_list is not music_list:
        _official_music_list = music_list
        _official_music_index = {m.music_id: m for m in music_list}


async def get_official_music(music_id: int) -> OfficialMusic | None:
    """按 music_id 查找官铺，使用缓存的 dict 索引做 O(1) 查找"""
    if not _official_music_index:
        await get_official_music_list()
    return _official_music_index.get(music_id)


async def get_official_music_list() -> list[OfficialMusic]:
    cache_date, music_list = _load_cache()
    if cache_date == date.today() and music_list:
        _ensure_index(music_list)
        return music_list

    updated = await update_official_music_cache()
    result = updated if updated else music_list
    _ensure_index(result)
    return result


def filter_by_level(music_list: list[OfficialMusic], level: int | None) -> list[tuple[OfficialMusic, dict]]:
    results: list[tuple[OfficialMusic, dict]] = []
    for music in music_list:
        for diff in music.difficulties:
            if level is None or diff.get("MusicLevel") == level:
                results.append((music, diff))
    return results


@driver.on_startup
async def _register_official_cache_update_job():
    from apscheduler.triggers.cron import CronTrigger

    trigger = CronTrigger.from_crontab("0 4 * * *")
    scheduler.add_job(
        update_official_music_cache,
        trigger,
        id="update_official_music_cache",
        replace_existing=True,
    )
    logger.info("已注册定时更新官铺列表缓存任务，cron: 0 4 * * *")

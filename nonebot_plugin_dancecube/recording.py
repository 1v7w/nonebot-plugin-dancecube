from .download import http_get_with_token
from .utils import compute_rating


class RecordedMusicInfo:
    """已记录音乐信息基类"""

    def __init__(self, music_id: int, name: str, cls: int, difficulty: int,
                 level: int, level_type: int, accuracy: float,
                 score: int, combo: int, miss: int, record_time: str):
        self.id: int = music_id
        self.name: str = name
        self.cls: int = cls
        self.difficulty: int = difficulty  # show 为 -1
        self.level: int = level           # 1-19
        self.level_type: int = level_type  # 经典1x show 10x
        self.accuracy: float = accuracy
        self.score: int = score
        self.combo: int = combo
        self.miss: int = miss
        self.rating: float = compute_rating(level, accuracy)
        self.record_time: str = record_time


class RankMusicInfo(RecordedMusicInfo):
    """排行榜音乐信息"""

    def __init__(self, music_id: int, name: str, cls: int, owner_type: int, details: dict):
        super().__init__(
            music_id=music_id,
            name=name,
            cls=cls,
            difficulty=int(details.get("MusicLevOld")),
            level=int(details.get("MusicRank")),
            level_type=int(details.get("MusicLev")),
            accuracy=float(details.get("PlayerPercent")) / 100,
            score=int(details.get("PlayerScore")),
            combo=int(details.get("ComboCount")),
            miss=int(details.get("PlayerMiss")),
            record_time=details.get("RecordTime"),
        )
        self.is_official: bool = owner_type == 1
        self.ranking: int = int(details.get("MusicRanking"))

    def __str__(self):
        return (f'RankMusicInfo {{"difficulty": {self.difficulty}, "level": {self.level}, '
                f'"level_type": {self.level_type}, "accuracy": {self.accuracy:.2f}, '
                f'"rating": {self.rating:.2f}}}')


class LastPlayMusicInfo(RecordedMusicInfo):
    """最近游玩音乐信息"""

    def __init__(self, music_id: int, name: str, details: dict):
        super().__init__(
            music_id=music_id,
            name=name,
            cls=0,
            difficulty=int(details.get("MusicLevOld")),
            level=int(details.get("MusicLevel")),
            level_type=int(details.get("MusicLev")),
            accuracy=float(details.get("PlayerPercent")) / 100,
            score=int(details.get("PlayerScore")),
            combo=int(details.get("ComboCount")),
            miss=int(details.get("PlayerMiss")),
            record_time=details.get("RecordTime"),
        )
        self.perfect: int = int(details.get("PlayerPerfect"))
        self.great: int = int(details.get("PlayerGreat"))
        self.good: int = int(details.get("PlayerGood"))


class MusicInfoManager:
    """音乐成绩管理器"""

    RANK_LIST_API = "https://dancedemo.shenghuayule.com/Dance/api/User/GetMyRankNew"
    RECENT_PLAY_API = "https://dancedemo.shenghuayule.com/Dance/api/User/GetLastPlay"

    def __init__(self, user_id: str, access_token: str):
        self.user_id: str = user_id
        self.access_token: str = access_token
        self.all_rank_list: list[RankMusicInfo] = []
        self.all_rank_official_list: list[RankMusicInfo] = []
        self.recent_record_list: list[LastPlayMusicInfo] = []

    async def _fetch_rank_list(self, official_only: bool = False) -> list[RankMusicInfo]:
        """获取排行榜列表，可按官方谱过滤"""
        result: list[RankMusicInfo] = []
        for cls_index in range(2, 7):  # 2-6: 国语、粤语、韩语、欧美、其它
            rep = await http_get_with_token(self.RANK_LIST_API, {"musicIndex": cls_index}, self.access_token)
            if rep is None:
                continue
            for music_info in rep:
                music_id = music_info.get("MusicID")
                name = music_info.get("Name")
                owner_type = int(music_info.get("OwnerType"))

                if official_only and owner_type != 1:
                    continue

                for record_info in music_info.get("ItemRankList"):
                    # 官方谱过滤：仅保留等级 1-19
                    if official_only:
                        rank_val = record_info.get("MusicRank")
                        if rank_val is not None and (rank_val > 19 or rank_val < 1):
                            continue
                    result.append(RankMusicInfo(music_id, name, cls_index, owner_type, record_info))

        result.sort(key=lambda x: x.rating, reverse=True)
        return result

    async def get_all_rank_list(self) -> list[RankMusicInfo]:
        """获取所有排行榜（含自制谱）"""
        self.all_rank_list = await self._fetch_rank_list(official_only=False)
        return self.all_rank_list

    async def get_all_rank_official_list(self) -> list[RankMusicInfo]:
        """获取官方谱排行榜"""
        self.all_rank_official_list = await self._fetch_rank_list(official_only=True)
        return self.all_rank_official_list

    async def get_recent_record_list(self) -> list[LastPlayMusicInfo]:
        """获取最近游玩记录"""
        rep = await http_get_with_token(self.RECENT_PLAY_API, {}, self.access_token)
        if rep is None:
            self.recent_record_list = []
            return self.recent_record_list

        self.recent_record_list = [
            LastPlayMusicInfo(item.get("MusicID"), item.get("MusicName"), item)
            for item in rep
        ]
        return self.recent_record_list
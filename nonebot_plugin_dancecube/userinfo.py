from nonebot.log import logger

from .download import http_get_with_token
from .utils import TEAM_MEMBER_TYPE_MAP


class UserInfo:
    def __init__(self):
        self.user_id: str = ""
        self.head_img_url: str = ""
        self.username: str = ""
        self.rating: int = 0                # 战力值
        self.score: int = 0                 # 积分
        self.title_url: str = ""            # 头衔
        self.head_img_box_url: str = ""     # 头像边框
        self.played_numbers: int = 0        # 游玩次数(暂未实现
        self.team_name: str = ""            # 战队名称
        self.team_position: str = ""        # 战队职位

    @staticmethod
    async def fetch_user_data(token: str, user_id: str) -> "UserInfo":
        url: str = "https://dancedemo.shenghuayule.com/Dance/api/User/GetInfo"
        query: dict[str, str | bool] = {
            "userId": str(user_id),
            "getNationRank": True,
        }
        user_data = await http_get_with_token(url, query, token)
        user = UserInfo()
        if user_data:
            user.user_id = user_data.get("UserID", user_id)
            user.head_img_url = user_data.get("HeadimgURL", "")
            user.username = user_data.get("UserName", "")
            user.rating = user_data.get("LvRatio", 0)
            user.score = user_data.get("MusicScore", 0)
            user.title_url = str(user_data.get("TitleUrl", "")).removesuffix('/256')
            user.head_img_box_url = str(user_data.get("HeadimgBoxPath", "")).removesuffix('/256')

            # 获取游玩次数
            try:
                play_count_url = "https://dancedemo.shenghuayule.com/Dance/api/ReplyTextItem/GetAllList"
                play_count_data = await http_get_with_token(play_count_url, {"machineId": "0"}, token)
                if play_count_data:
                    for item in play_count_data:
                        if item.get("ReplyTextItemID") == 5 and item.get("ItemType") == 5:
                            user.played_numbers = int(item.get("Content", 0))
                            break
            except Exception as e:
                logger.warning(f"获取游玩次数失败: {e}")

            # 获取战队信息
            team_id = user_data.get("TeamID", 0)
            if team_id:
                try:
                    team_url = "https://dancedemo.shenghuayule.com/Dance/api/Team/GetTeamInfo"
                    team_data = await http_get_with_token(team_url, {"teamId": str(team_id)}, token)
                    if team_data:
                        user.team_name = team_data.get("TeamName", "")
                        member_type = team_data.get("UserInfo", {}).get("MemberType", 0)
                        user.team_position = TEAM_MEMBER_TYPE_MAP.get(member_type, "未知")
                except Exception as e:
                    logger.warning(f"获取战队信息失败: {e}")

        return user

    def __str__(self):
        return f"user_id: {self.user_id}, head_img_url: {self.head_img_url}, username: {self.username}, rating: {self.rating}"
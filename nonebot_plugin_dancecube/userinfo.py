from .download import http_get_with_token


class UserInfo:
    def __init__(self):
        self.user_id: str = ""
        self.head_img_url: str = ""
        self.username: str = ""
        self.rating: int = 0                # 战力值
        self.score: int = 0                 # 积分
        self.title_url: str = ""            # 头衔
        self.head_img_box_url: str = ""     # 头像边框

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
        return user

    def __str__(self):
        return f"user_id: {self.user_id}, head_img_url: {self.head_img_url}, username: {self.username}, rating: {self.rating}"
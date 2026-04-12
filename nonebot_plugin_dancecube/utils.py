from datetime import datetime


def calc_time_difference(given_time_str: str) -> int:
    """获取给定时间与当前时间的差值（秒）"""
    given_time = datetime.strptime(given_time_str, "%Y-%m-%d %H:%M:%S")
    return int((given_time - datetime.now()).total_seconds())


# 难度类型映射
LEVEL_TYPE_LIST = [11, 12, 13, 14, 15, 101, 102, 103, 104, 105]

# 战队职位映射
TEAM_MEMBER_TYPE_MAP = {
    1: "队长",
    2: "副队",
    3: "队员",
    4: "精英",
}

LEVEL_TYPE_TO_STR = {
    11: "经典-基础",
    12: "经典-进阶",
    13: "经典-专家",
    14: "经典-大师",
    15: "经典-传奇",
    101: "show+基础",
    102: "show+进阶",
    103: "show+专家",
    104: "show+大师",
    105: "show+传奇",
}


def compute_rating(level: int, acc: float) -> int:
    """
    返回 level 级谱面 acc 准度贡献的战力。
    level: 谱面等级（1-19）
    acc: 记录百分比（0-100，两位小数）
    """
    acc_int = max(0, min(int(acc * 100), 10000))
    if level < 1 or level > 19:
        return 0

    base_ratings: list[float] = [
        (level + 2) * 100.0,                            # 100
        (level + 1) * 100.0,                            # [98, 100)
        level * 100.0,                                  # [95, 98)
        (level - 1) * 100.0,                            # [90, 95)
        (level - 2 + (19 - level) / 19.0) * 100.0,      # [85, 90)
        (level - 3 + 2 * (19 - level) / 19.0) * 100.0,  # [80, 85)
        (level - 4 + 3 * (19 - level) / 19.0) * 100.0,  # [75, 80)
        (level - 5 + 4 * (19 - level) / 19.0) * 100.0,  # [70, 75)
    ]

    if acc_int == 10000:
        base, offset = base_ratings[0], 0.0
    elif acc_int >= 9800:
        base, offset = base_ratings[1], (acc_int - 9800) / 200.0 * 100
    elif acc_int >= 9500:
        base, offset = base_ratings[2], (acc_int - 9500) / 300.0 * 100
    elif acc_int >= 9000:
        base, offset = base_ratings[3], (acc_int - 9000) / 500.0 * 100
    elif acc_int >= 8500:
        base = base_ratings[4]
        offset = (acc_int - 8500) / 500.0 * (base_ratings[3] - base)
    elif acc_int >= 8000:
        base = base_ratings[5]
        offset = (acc_int - 8000) / 500.0 * (base_ratings[4] - base)
    elif acc_int >= 7500:
        base = base_ratings[6]
        offset = (acc_int - 7500) / 500.0 * (base_ratings[5] - base)
    elif acc_int >= 7000:
        base = base_ratings[7]
        offset = (acc_int - 7000) / 500.0 * (base_ratings[6] - base)
    else:
        base, offset = 0.0, 0.0

    return int(base + offset)
import json
from datetime import datetime, timedelta
from pathlib import Path

from nonebot import get_bot
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from .download import http_get, http_post, http_post_raw
from .config import user_tokens_file

import asyncio

_tokens_lock = asyncio.Lock()
_token_manager: "TokenManager | None" = None


def get_token_manager() -> "TokenManager":
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager(user_tokens_file)
    return _token_manager

class Token:
    def __init__(self, access_token: str = "", refresh_token: str = "", expires: str = "",
                 refresh_token_expires: str = "", user_id: str = "", qq: str = ""):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires = expires
        self.refresh_token_expires = refresh_token_expires
        self.user_id = user_id
        self.qq = qq

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires": self.expires,
            "refresh_token_expires": self.refresh_token_expires,
            "user_id": self.user_id,
            "qq": self.qq,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Token":
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            expires=data.get("expires", ""),
            refresh_token_expires=data.get("refresh_token_expires", data.get("refreshExpires", "")),
            user_id=data.get("user_id", data.get("userId", "")),
            qq=data.get("qq", "0"),
        )


class TokenBuilder:
    """处理二维码登录流程"""

    QRCODE_URL_API = "https://dancedemo.shenghuayule.com/Dance/api/Common/GetQrCode"
    GET_TOKEN_API = "https://dancedemo.shenghuayule.com/Dance/token"

    def __init__(self):
        self.id: str = ""
        self.qrcode_url: str = ""

    async def get_qrcode(self) -> str:
        """获取登录二维码 URL"""
        rep = await http_get(self.QRCODE_URL_API, {"id": ""})
        if rep is None:
            return ""
        self.qrcode_url = rep.get("QrcodeUrl", "")
        self.id = rep.get("ID", "")
        return self.qrcode_url

    async def get_token(self, qq: int) -> None:
        """启动定时轮询获取 token 的任务"""
        job_id = f"get_token_job_{qq}"
        cancel_job_id = f"cancel_{job_id}"

        # 清理可能残留的同名任务
        for jid in (job_id, cancel_job_id):
            existing = scheduler.get_job(jid)
            if existing:
                scheduler.remove_job(jid)

        async def _poll_token(job_id: str, cancel_job_id: str, client_id: str, qq: int):
            data = {
                "client_type": "qrcode",
                "grant_type": "client_credentials",
                "client_id": client_id,
            }
            try:
                rep = await http_post_raw(self.GET_TOKEN_API, data)
            except Exception:
                return  # 网络异常，等下次轮询重试
            if rep.status_code != 200:
                return  # 未扫码，等下次轮询
            token = Token.from_dict(rep.json())
            token.qq = str(qq)
            await get_token_manager().update_token(token)
            # 登录成功，清理轮询任务和超时取消任务
            scheduler.remove_job(job_id)
            cancel_job = scheduler.get_job(cancel_job_id)
            if cancel_job:
                scheduler.remove_job(cancel_job_id)
            await get_bot().send_private_msg(
                user_id=qq,
                message=f"登录成功。登录的舞立方ID：{token.user_id}\n如果不是你的舞立方ID号，请重新登录！",
            )

        scheduler.add_job(
            _poll_token,
            "interval",
            seconds=5,
            args=[job_id, cancel_job_id, self.id, qq],
            id=job_id,
        )

        async def _cancel_on_timeout(job_id: str, qq: int):
            if scheduler.get_job(job_id):
                logger.info(f"{qq}扫描二维码超时。")
                scheduler.remove_job(job_id)
                await get_bot().send_private_msg(user_id=qq, message="登录失败，请重新发送命令进行登录。")

        scheduler.add_job(
            _cancel_on_timeout,
            "date",
            run_date=datetime.now() + timedelta(minutes=2),
            args=[job_id, qq],
            id=cancel_job_id,
        )


class TokenManager:
    """管理 token 的持久化存储"""

    def __init__(self, file_path: Path | str):
        self.file_path = file_path

    def _load_tokens_unsafe(self) -> list[Token]:
        """不加锁的读取"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return [Token.from_dict(item) for item in json.load(f)]
        except FileNotFoundError:
            return []

    def _save_tokens_unsafe(self, tokens: list[Token]) -> None:
        """不加锁的写入"""
        data = [token.to_dict() for token in tokens]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    async def get_token_by_qq(self, qq: int) -> Token | None:
        """加锁读取指定 QQ 的 token"""
        async with _tokens_lock:
            for token in self._load_tokens_unsafe():
                if token.qq == str(qq):
                    return token
        return None

    async def update_token(self, new_token: Token) -> None:
        """加锁更新 token"""
        async with _tokens_lock:
            tokens = self._load_tokens_unsafe()
            for i, token in enumerate(tokens):
                if token.qq == new_token.qq:
                    tokens[i] = new_token
                    self._save_tokens_unsafe(tokens)
                    return
            tokens.append(new_token)
            self._save_tokens_unsafe(tokens)
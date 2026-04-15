import asyncio
import functools

import httpx
from PIL import Image
from io import BytesIO

from nonebot.log import logger

def retry_on_failure(max_retries: int = 3, delay: float = 1, backoff: float = 2):
    """装饰器：请求失败时自动重试，指数退避"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception: Exception | None = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPError, httpx.HTTPStatusError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.debug(f"第{attempt + 1}次尝试失败，{wait_time}秒后重试: {e}")
                        await asyncio.sleep(wait_time)
            raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator


@retry_on_failure(max_retries=3, delay=1, backoff=2)
async def http_get(url: str, params: dict | None = None, headers: dict | None = None) -> dict | None:
    """GET 请求，返回 JSON 或 None"""
    async with httpx.AsyncClient() as client:
        rep = await client.get(url, headers=headers, params=params)
        if rep.status_code == 200:
            return rep.json()
        logger.debug(f"GET {url} 返回状态码 {rep.status_code}")
        return None


async def http_get_with_token(url: str, params: dict | None = None, token: str = "") -> dict | None:
    """带 Authorization 的 GET 请求"""
    headers = {"Authorization": f"Bearer {token}"}
    return await http_get(url, params=params, headers=headers)


@retry_on_failure(max_retries=3, delay=1, backoff=2)
async def http_post(url: str, data: dict | None = None) -> dict | None:
    """POST 请求，返回 JSON 或 None"""
    async with httpx.AsyncClient() as client:
        rep = await client.post(url, data=data)
        if rep.status_code == 200:
            return rep.json()
        logger.debug(f"POST {url} 返回状态码 {rep.status_code}")
        return None


@retry_on_failure(max_retries=3, delay=1, backoff=2)
async def http_get_image(url: str) -> Image.Image:
    """下载图片并返回 PIL Image 对象"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))


async def http_get_raw(url: str, params: dict | None = None) -> httpx.Response:
    """GET 请求，返回原始 Response 对象（不自动重试）"""
    async with httpx.AsyncClient() as client:
        return await client.get(url, params=params)


async def http_post_raw(url: str, data: dict | None = None) -> httpx.Response:
    """POST 请求，返回原始 Response 对象（不自动重试）"""
    async with httpx.AsyncClient() as client:
        return await client.post(url, data=data)

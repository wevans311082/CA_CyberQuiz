# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from datetime import datetime
from io import BytesIO
from uuid import uuid4

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException

from classquiz.auth import get_current_user
from classquiz.db.models import User, StorageItem, PublicStorageItem
from classquiz.helpers.pixabay import get_images, GetImagesParams, BoolInput, GetImagesResponse, NotFoundError
from classquiz.config import settings, storage, arq
from classquiz.helpers.network import assert_safe_remote_url

settings = settings()
router = APIRouter()


@router.get("/images")
async def search_pixabay_images(query: str, page: int = 1, user: User = Depends(get_current_user)) -> GetImagesResponse:
    if settings.pixabay_api_key is None:
        raise HTTPException(status_code=423, detail="Pixabay not set up")
    return await get_images(settings.pixabay_api_key, GetImagesParams(q=query, safesearch=BoolInput.true, page=page))


@router.post("/save")
async def save_pixabay_image(id: str, user: User = Depends(get_current_user)) -> PublicStorageItem:
    if settings.pixabay_api_key is None:
        raise HTTPException(status_code=423, detail="Pixabay not set up")
    if user.storage_used > settings.free_storage_limit:
        raise HTTPException(status_code=409, detail="Storage limit reached")
    try:
        images = await get_images(settings.pixabay_api_key, GetImagesParams(id=id, safesearch=BoolInput.true))
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Pixabay file not found")
    image = images.hits[0]
    file_id = uuid4()
    file_data = b""
    try:
        await assert_safe_remote_url(image.largeImageURL)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Pixabay image URL was rejected") from exc
    async with ClientSession() as session, session.get(image.largeImageURL, timeout=15, allow_redirects=False) as resp:
        if resp.status != 200:
            raise HTTPException(status_code=502, detail="Pixabay image could not be downloaded")
        async for i in resp.content.iter_chunked(1024):
            file_data += i
            if len(file_data) > 10 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="Pixabay image is too large")
        content_type = resp.headers.get("Content-Type")

    if content_type is None:
        content_type = "image/*"
    file = BytesIO(file_data)
    await storage.upload(file_name=file_id.hex, file_data=file, mime_type=content_type)
    file_obj: StorageItem = StorageItem(
        id=file_id,
        uploaded_at=datetime.now(),
        mime_type=content_type,
        hash=None,
        user=user,
        size=0,
        deleted_at=None,
        alt_text=None,
        imported=True,
    )
    await file_obj.save()
    await arq.enqueue_job("calculate_hash", file_id.hex)
    return PublicStorageItem.from_db_model(file_obj)

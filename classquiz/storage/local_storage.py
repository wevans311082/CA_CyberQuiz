# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import os
from shutil import copyfileobj
from typing import BinaryIO, Generator

import aiofiles
import aiofiles.os

_DEFAULT_CHUNK_SIZE = 32768  # bytes; arbitrary


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)

    def _path(self, file_name: str) -> str:
        candidate = os.path.abspath(os.path.join(self.base_path, file_name))
        if os.path.commonpath((self.base_path, candidate)) != self.base_path:
            raise ValueError("file name resolves outside storage directory")
        return candidate

    async def download(self, file_name: str) -> Generator | None:
        try:
            async with aiofiles.open(file=self._path(file_name), mode="rb") as f:
                while True:
                    chunk = await f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        except FileNotFoundError:
            yield None

    # skipcq: PYL-W0613
    async def upload(
        self,
        file_name: str,
        file: BinaryIO,
        size: int | None,
        mime_type: str | None = None,
    ) -> None:
        with open(file=self._path(file_name), mode="wb") as f:
            copyfileobj(file, f)

    async def delete(self, file_names: [str]) -> None:
        for i in file_names:
            try:
                await aiofiles.os.remove(self._path(i))
            except FileNotFoundError:
                pass
        return None

    def size(self, file_name: str) -> int | None:
        try:
            return os.stat(self._path(file_name)).st_size
        except FileNotFoundError:
            return None

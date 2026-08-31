import asyncio
import socket

import pytest

from classquiz.helpers.network import assert_safe_remote_url


def test_remote_url_rejects_local_and_embedded_credentials():
    with pytest.raises(ValueError):
        asyncio.run(assert_safe_remote_url("http://127.0.0.1/admin"))
    with pytest.raises(ValueError):
        asyncio.run(assert_safe_remote_url("https://user:password@example.com/file"))


def test_remote_url_rejects_private_dns_resolution(monkeypatch):
    async def fake_getaddrinfo(*_args, **_kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.4", 443))]

    monkeypatch.setattr(asyncio, "get_running_loop", lambda: FakeLoop(fake_getaddrinfo))
    with pytest.raises(ValueError, match="protected network"):
        asyncio.run(assert_safe_remote_url("https://example.com/file"))


class FakeLoop:
    def __init__(self, resolver):
        self.resolver = resolver

    def getaddrinfo(self, *args, **kwargs):
        return self.resolver(*args, **kwargs)

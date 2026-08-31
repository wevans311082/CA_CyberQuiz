"""Small SSRF guard for server-side HTTP fetches."""

import asyncio
import ipaddress
import socket
from urllib.parse import urlparse


async def assert_safe_remote_url(url: str, *, allowed_hosts: set[str] | None = None) -> None:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").rstrip(".").lower()
    if parsed.scheme not in {"http", "https"} or not hostname or parsed.username or parsed.password:
        raise ValueError("Only unauthenticated HTTP(S) URLs are allowed")
    if allowed_hosts is not None and hostname not in {host.lower() for host in allowed_hosts}:
        raise ValueError("Remote URL host is not allowed")
    if hostname in {"localhost", "localhost.localdomain"}:
        raise ValueError("Local network URLs are not allowed")
    try:
        addresses = await asyncio.get_running_loop().getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except (OSError, ValueError) as exc:
        raise ValueError("Remote URL host could not be resolved") from exc
    for address in {result[4][0] for result in addresses}:
        ip = ipaddress.ip_address(address)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            raise ValueError("Remote URL resolves to a protected network")

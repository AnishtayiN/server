import base64
import json
import urllib.parse
from typing import Optional
from ..models import Client, Inbound

class LinkGenerator:
    @staticmethod
    def generate_vless(client: Client, inbound: Inbound, host: str) -> str:
        params = {
            "type": inbound.network,
            "security": inbound.security,
            "sni": inbound.sni or host,
            "fp": "chrome",
        }
        
        if inbound.flow:
            params["flow"] = inbound.flow
        
        if inbound.security == "reality":
            settings = inbound.settings or {}
            params["pbk"] = settings.get("public_key", "")
            params["sid"] = settings.get("short_id", "")
        
        if inbound.network == "ws":
            stream = inbound.stream_settings or {}
            params["path"] = stream.get("path", "/")
            params["host"] = stream.get("host", host)
        elif inbound.network == "grpc":
            stream = inbound.stream_settings or {}
            params["serviceName"] = stream.get("service_name", "grpc")
            params["mode"] = "gun"
        
        query = urllib.parse.urlencode(params)
        remark = urllib.parse.quote(client.email)
        
        return f"vless://{client.uuid_str}@{host}:{inbound.port}?{query}#{remark}"
    
    @staticmethod
    def generate_vmess(client: Client, inbound: Inbound, host: str) -> str:
        config = {
            "v": "2",
            "ps": client.email,
            "add": host,
            "port": inbound.port,
            "id": client.vmess_id or client.uuid_str,
            "aid": client.alter_id or 0,
            "net": inbound.network,
            "type": "none",
            "host": "",
            "path": "",
            "tls": inbound.security if inbound.security != "none" else "",
            "sni": inbound.sni or host
        }
        
        if inbound.network == "ws":
            stream = inbound.stream_settings or {}
            config["path"] = stream.get("path", "/")
            config["host"] = stream.get("host", host)
        
        json_str = json.dumps(config, separators=(',', ':'))
        encoded = base64.b64encode(json_str.encode()).decode()
        return f"vmess://{encoded}"
    
    @staticmethod
    def generate_trojan(client: Client, inbound: Inbound, host: str) -> str:
        params = {
            "type": inbound.network,
            "security": inbound.security,
            "sni": inbound.sni or host,
        }
        
        if inbound.network == "ws":
            stream = inbound.stream_settings or {}
            params["path"] = stream.get("path", "/")
            params["host"] = stream.get("host", host)
        
        query = urllib.parse.urlencode(params)
        remark = urllib.parse.quote(client.email)
        password = client.password or client.uuid_str
        
        return f"trojan://{password}@{host}:{inbound.port}?{query}#{remark}"
    
    @staticmethod
    def generate_shadowsocks(client: Client, inbound: Inbound, host: str) -> str:
        settings = inbound.settings or {}
        method = settings.get("method", "chacha20-ietf-poly1305")
        password = client.password or client.uuid_str
        
        user_info = f"{method}:{password}"
        encoded = base64.b64encode(user_info.encode()).decode()
        remark = urllib.parse.quote(client.email)
        
        return f"ss://{encoded}@{host}:{inbound.port}#{remark}"
    
    @classmethod
    def generate_link(cls, client: Client, inbound: Inbound, host: str) -> Optional[str]:
        generators = {
            "vless": cls.generate_vless,
            "vmess": cls.generate_vmess,
            "trojan": cls.generate_trojan,
            "shadowsocks": cls.generate_shadowsocks,
        }
        
        generator = generators.get(inbound.protocol)
        if generator:
            return generator(client, inbound, host)
        return None

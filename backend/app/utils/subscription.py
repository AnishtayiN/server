import base64
import yaml
import json
from typing import List

class SubscriptionBuilder:
    @staticmethod
    def build_v2ray(clients_data: List[dict]) -> str:
        links = [item["link"] for item in clients_data if item.get("link")]
        payload = "\n".join(links)
        return base64.b64encode(payload.encode()).decode()
    
    @staticmethod
    def build_clash(clients_data: List[dict], sub_name: str = "AnishtayiN") -> str:
        proxies = []
        proxy_names = []
        
        for item in clients_data:
            if not item.get("link"):
                continue
                
            client = item["client"]
            inbound = item["inbound"]
            host = item.get("host", "localhost")
            
            if inbound.protocol == "vless":
                proxy = {
                    "name": client.email,
                    "type": "vless",
                    "server": host,
                    "port": inbound.port,
                    "uuid": client.uuid_str,
                    "network": inbound.network,
                    "tls": inbound.security != "none",
                    "udp": True,
                    "flow": inbound.flow or "",
                    "servername": inbound.sni or "",
                    "client-fingerprint": "chrome",
                }
                if inbound.security == "reality":
                    settings = inbound.settings or {}
                    proxy["reality-opts"] = {
                        "public-key": settings.get("public_key", ""),
                        "short-id": settings.get("short_id", ""),
                    }
                proxies.append(proxy)
            
            elif inbound.protocol == "vmess":
                proxies.append({
                    "name": client.email,
                    "type": "vmess",
                    "server": host,
                    "port": inbound.port,
                    "uuid": client.vmess_id or client.uuid_str,
                    "alterId": client.alter_id or 0,
                    "cipher": "auto",
                    "tls": inbound.security != "none",
                    "udp": True,
                    "network": inbound.network,
                    "servername": inbound.sni or "",
                })
            
            elif inbound.protocol == "trojan":
                proxies.append({
                    "name": client.email,
                    "type": "trojan",
                    "server": host,
                    "port": inbound.port,
                    "password": client.password or client.uuid_str,
                    "udp": True,
                    "sni": inbound.sni or "",
                })
            
            proxy_names.append(client.email)
        
        config = {
            "mixed-port": 7890,
            "allow-lan": False,
            "mode": "rule",
            "log-level": "info",
            "unified-delay": True,
            "dns": {
                "enable": True,
                "enhanced-mode": "fake-ip",
                "nameserver": ["8.8.8.8", "1.1.1.1"]
            },
            "proxies": proxies,
            "proxy-groups": [
                {"name": "PROXY", "type": "select", "proxies": proxy_names}
            ],
            "rules": ["MATCH,PROXY"]
        }
        
        return yaml.dump(config, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def build_singbox(clients_data: List[dict], sub_name: str = "AnishtayiN") -> str:
        outbounds = []
        
        for item in clients_data:
            if not item.get("link"):
                continue
            
            client = item["client"]
            inbound = item["inbound"]
            host = item.get("host", "localhost")
            
            if inbound.protocol == "vless":
                outbound = {
                    "type": "vless",
                    "tag": client.email,
                    "server": host,
                    "server_port": inbound.port,
                    "uuid": client.uuid_str,
                    "tls": {
                        "enabled": inbound.security != "none",
                        "server_name": inbound.sni or host,
                    }
                }
                
                if inbound.security == "reality":
                    settings = inbound.settings or {}
                    outbound["tls"]["reality"] = {
                        "enabled": True,
                        "public_key": settings.get("public_key", ""),
                        "short_id": settings.get("short_id", ""),
                    }
                
                if inbound.flow:
                    outbound["flow"] = inbound.flow
                
                outbounds.append(outbound)
        
        config = {
            "log": {"level": "info"},
            "inbounds": [
                {
                    "type": "tun",
                    "tag": "tun-in",
                    "inet4_address": "172.19.0.1/30",
                    "auto_route": True,
                    "strict_route": True,
                    "stack": "system",
                    "sniff": True
                }
            ],
            "outbounds": outbounds + [
                {"type": "direct", "tag": "direct"},
                {"type": "block", "tag": "block"}
            ],
            "route": {
                "final": outbounds[0]["tag"] if outbounds else "direct"
            }
        }
        
        return json.dumps(config, indent=2)

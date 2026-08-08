import json
import base64
from typing import Dict, Any, Optional
from models import User


def generate_user_config(protocol: str, uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate protocol-specific configuration for a user."""
    
    configs = {
        "vmess": generate_vmess_config(uuid, config),
        "vless": generate_vless_config(uuid, config),
        "trojan": generate_trojan_config(uuid, config),
        "shadowsocks": generate_shadowsocks_config(uuid, config),
        "wireguard": generate_wireguard_config(uuid, config),
        "hysteria": generate_hysteria_config(uuid, config),
        "http": generate_http_config(uuid, config),
        "tunnel": generate_tunnel_config(uuid, config),
        "mixed": generate_mixed_config(uuid, config),
        "tun": generate_tun_config(uuid, config),
    }
    
    return configs.get(protocol, {})


def generate_vmess_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "v": "2",
        "ps": config.get("name", "XPanel-VMess"),
        "add": config.get("address", "${SERVER_IP}"),
        "port": str(config.get("port", 443)),
        "id": uuid,
        "aid": str(config.get("alterId", 0)),
        "net": config.get("network", "tcp"),
        "type": config.get("headerType", "none"),
        "host": config.get("host", ""),
        "path": config.get("path", ""),
        "tls": config.get("security", "none"),
        "sni": config.get("sni", ""),
        "fp": config.get("fingerprint", "chrome"),
        "alpn": config.get("alpn", "h2,http/1.1"),
    }


def generate_vless_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    flow = config.get("flow", "")
    security = config.get("security", "reality")
    pbk = config.get("publicKey", "")
    sid = config.get("shortId", "")
    fp = config.get("fingerprint", "chrome")
    
    return {
        "v": "0",
        "ps": config.get("name", "XPanel-VLESS"),
        "add": config.get("address", "${SERVER_IP}"),
        "port": str(config.get("port", 443)),
        "id": uuid,
        "flow": flow,
        "net": config.get("network", "tcp"),
        "type": config.get("headerType", "none"),
        "host": config.get("host", ""),
        "path": config.get("path", ""),
        "security": security,
        "sni": config.get("sni", ""),
        "fp": fp,
        "alpn": config.get("alpn", "h2,http/1.1"),
        "pbk": pbk,
        "sid": sid,
    }


def generate_trojan_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "password": uuid,
        "name": config.get("name", "XPanel-Trojan"),
        "address": config.get("address", "${SERVER_IP}"),
        "port": config.get("port", 443),
        "network": config.get("network", "tcp"),
        "security": config.get("security", "tls"),
        "sni": config.get("sni", ""),
        "alpn": config.get("alpn", "h2,http/1.1"),
    }


def generate_shadowsocks_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    method = config.get("method", "chacha20-poly1305")
    password = config.get("password", uuid[:32])
    
    return {
        "server": config.get("address", "${SERVER_IP}"),
        "port": config.get("port", 8388),
        "method": method,
        "password": password,
        "name": config.get("name", "XPanel-Shadowsocks"),
    }


def generate_wireguard_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "privateKey": config.get("privateKey", ""),
        "address": config.get("address", ["10.0.0.2/32"]),
        "peers": [{
            "publicKey": config.get("serverPublicKey", ""),
            "endpoint": f"{config.get('serverAddress', '${SERVER_IP}')}:{config.get('port', 51820)}",
            "allowedIPs": ["0.0.0.0/0", "::/0"],
            "keepAlive": 25
        }],
        "mtu": config.get("mtu", 1420),
        "name": config.get("name", "XPanel-WireGuard"),
    }


def generate_hysteria_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "server": f"{config.get('address', '${SERVER_IP}')}:{config.get('port', 8443)}",
        "protocol": config.get("protocol", "udp"),
        "auth": uuid,
        "up": config.get("up", "50"),
        "down": config.get("down", "100"),
        "obfs": config.get("obfs", ""),
        "sni": config.get("sni", ""),
        "insecure": config.get("insecure", False),
        "name": config.get("name", "XPanel-Hysteria"),
    }


def generate_http_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "address": config.get("address", "${SERVER_IP}"),
        "port": config.get("port", 8080),
        "username": config.get("username", ""),
        "password": config.get("password", uuid[:16]),
        "name": config.get("name", "XPanel-HTTP"),
    }


def generate_tunnel_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "protocol": config.get("protocol", "tcp"),
        "target": config.get("target", ""),
        "port": config.get("port", 0),
        "name": config.get("name", "XPanel-Tunnel"),
    }


def generate_mixed_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "protocols": ["vmess", "vless", "trojan"],
        "port": config.get("port", 443),
        "address": config.get("address", "${SERVER_IP}"),
        "uuid": uuid,
        "name": config.get("name", "XPanel-Mixed"),
    }


def generate_tun_config(uuid: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "interface": config.get("interface", "tun0"),
        "address": config.get("address", ["10.0.0.1/30"]),
        "mtu": config.get("mtu", 9000),
        "name": config.get("name", "XPanel-TUN"),
    }


def generate_subscription_link(user: User, host: str, port: int) -> str:
    """Generate subscription link for a user."""
    # Base64 encode the config
    config_json = json.dumps(user.config)
    config_base64 = base64.b64encode(config_json.encode()).decode()
    
    return f"http://{host}:{port}/api/v1/subscription/{user.uuid}"


def generate_clash_config(user: User, server_ip: str) -> Dict[str, Any]:
    """Generate Clash configuration for a user."""
    protocol = user.protocol.value
    
    if protocol == "vmess":
        return {
            "name": user.username,
            "type": "vmess",
            "server": server_ip,
            "port": user.config.get("port", 443),
            "uuid": user.uuid,
            "alterId": user.config.get("alterId", 0),
            "cipher": "auto",
            "network": user.config.get("network", "tcp"),
        }
    elif protocol == "vless":
        return {
            "name": user.username,
            "type": "vless",
            "server": server_ip,
            "port": user.config.get("port", 443),
            "uuid": user.uuid,
            "network": user.config.get("network", "tcp"),
            "tls": user.config.get("security", "reality") != "none",
        }
    elif protocol == "trojan":
        return {
            "name": user.username,
            "type": "trojan",
            "server": server_ip,
            "port": user.config.get("port", 443),
            "password": user.uuid,
            "network": user.config.get("network", "tcp"),
        }
    elif protocol == "shadowsocks":
        return {
            "name": user.username,
            "type": "ss",
            "server": server_ip,
            "port": user.config.get("port", 8388),
            "cipher": user.config.get("method", "chacha20-poly1305"),
            "password": user.config.get("password", user.uuid[:32]),
        }
    
    return {}


def xray_config_to_json(config: Dict[str, Any]) -> str:
    """Convert Xray configuration to JSON string."""
    return json.dumps(config, indent=2)

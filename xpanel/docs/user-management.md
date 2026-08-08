# User Management Guide

## Overview

XPanel allows you to manage multiple users with different protocols, traffic limits, and expiry dates through an intuitive web interface.

## Creating Users

### Via Web Interface

1. Navigate to **Users** in the sidebar
2. Click **Add User**
3. Fill in the details:
   - **Username**: Unique identifier for the user
   - **Protocol**: Select from Vmess, Vless, Trojan, ShadowSocks, WireGuard, Hysteria, HTTP, Tunnel, Mixed, or Tun
   - **Traffic Limit (GB)**: Set limit (0 for unlimited)
   - **IP Limit**: Maximum concurrent connections (0 for unlimited)
   - **Expiry (Days)**: Account validity period
   - **Notes**: Optional notes for your reference
4. Click **Create**

### Protocol-Specific Settings

Each protocol has specific configuration options:

#### VMess
- Port: Usually 443 for TLS
- Network: tcp, ws, grpc, etc.
- Security: none, tls, reality

#### VLESS
- Flow: xtls-rprx-vision (for Reality)
- Security: reality, tls, none
- Requires Reality public key for Reality security

#### Trojan
- Password: Auto-generated UUID
- Security: tls recommended

#### ShadowSocks
- Method: chacha20-poly1305, aes-256-gcm, etc.
- Password: Auto-generated

#### WireGuard
- Private Key: Client private key
- Server Public Key: Your server's public key
- Address: Client IP in WireGuard network

#### Hysteria
- Up/Down: Bandwidth limits
- Protocol: udp,wechat-video,faketcp
- Obfuscation: Optional

## Managing Users

### Edit User

1. Go to **Users** list
2. Click the edit icon next to the user
3. Modify settings as needed
4. Click **Save**

### Reset Traffic

To reset a user's traffic counter:
1. Edit the user
2. Set traffic used to 0
3. Save changes

### Extend Expiry

To extend a user's access:
1. Edit the user
2. Update expiry date or add more days
3. Save changes

### Disable/Enable User

Toggle user status to temporarily disable access without deleting the account.

### Delete User

1. Go to **Users** list
2. Click the delete icon
3. Confirm deletion

⚠️ This action cannot be undone!

## User Status

Users can have the following statuses:

- **Active**: Normal operation
- **Expired**: Past expiry date
- **Disabled**: Manually disabled by admin
- **Traffic Exhausted**: Used all allocated traffic

## Subscription Links

Each user gets a unique subscription URL for easy client configuration.

### Getting Subscription Link

1. Go to **Users** list
2. Click the subscription icon next to the user
3. Copy the provided link

### Using Subscription Links

The subscription link can be imported into compatible clients:

- **v2rayN/v2rayNG**: Paste subscription URL
- **Clash**: Convert to Clash format
- **Shadowrocket**: Direct import
- **Quantumult X**: Direct import

### Subscription Formats

XPanel provides multiple formats:

- **Base64**: Standard v2ray subscription
- **Clash**: YAML configuration
- **JSON**: Raw configuration

## Traffic Monitoring

### Real-time Usage

View current traffic usage in the Users list:
- Total used
- Percentage of limit
- Upload/download breakdown

### Traffic Logs

Access detailed traffic logs:
1. Navigate to **Statistics**
2. Select **Traffic Logs**
3. Filter by user or date range

## Bulk Operations

### Create Multiple Users

Use the bulk create feature:
1. Click **Bulk Create**
2. Enter usernames (one per line)
3. Set common parameters
4. Click **Create All**

### Batch Actions

Select multiple users to:
- Delete selected
- Reset traffic
- Extend expiry
- Export configurations

## Best Practices

1. **Naming Convention**: Use descriptive usernames
2. **Traffic Limits**: Set reasonable limits based on usage patterns
3. **Expiry Dates**: Regular review and cleanup
4. **Notes**: Document special requirements
5. **Regular Backups**: Backup before bulk operations

## API Access

For programmatic user management, use the REST API:

```bash
# Create user
curl -X POST http://localhost:8080/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "protocol": "vmess",
    "traffic_limit_gb": 100,
    "expiry_days": 30
  }'

# List users
curl http://localhost:8080/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

See API documentation for complete endpoint reference.

---

⚠️ **LEGAL DISCLAIMER**: Use responsibly and in compliance with all applicable laws.

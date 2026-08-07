package service

import (
"encoding/base64"
"encoding/json"
"fmt"
"strings"
"time"
)

func GenerateQRCodeContent(link string) string {
return link
}

func FormatTraffic(bytes int64) string {
if bytes < 1024 {
return fmt.Sprintf("%d B", bytes)
}
if bytes < 1024*1024 {
return fmt.Sprintf("%.2f KB", float64(bytes)/1024)
}
if bytes < 1024*1024*1024 {
return fmt.Sprintf("%.2f MB", float64(bytes)/(1024*1024))
}
if bytes < 1024*1024*1024*1024 {
return fmt.Sprintf("%.2f GB", float64(bytes)/(1024*1024*1024))
}
return fmt.Sprintf("%.2f TB", float64(bytes)/(1024*1024*1024*1024))
}

func DecodeBase64Subscription(encoded string) (string, error) {
decoded, err := base64.StdEncoding.DecodeString(encoded)
if err != nil {
return "", err
}
return string(decoded), nil
}

func EncodeBase64Subscription(content string) string {
return base64.StdEncoding.EncodeToString([]byte(content))
}

func ParseVMessLink(link string) map[string]interface{} {
if !strings.HasPrefix(link, "vmess://") {
return nil
}

encoded := strings.TrimPrefix(link, "vmess://")
decoded, err := base64.StdEncoding.DecodeString(encoded)
if err != nil {
return nil
}

var config map[string]interface{}
json.Unmarshal(decoded, &config)
return config
}

func GetExpiryDays(expiryTime int64) int {
if expiryTime == 0 {
return -1 // Unlimited
}
now := GetCurrentTimeMs()
remaining := expiryTime - now
if remaining <= 0 {
return 0
}
return int(remaining / (24 * 60 * 60 * 1000))
}

func GetCurrentTimeMs() int64 {
return time.Now().UnixMilli()
}

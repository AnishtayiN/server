package service

import (
"crypto/aes"
"crypto/cipher"
"crypto/rand"
"encoding/base64"
"encoding/hex"
"encoding/json"
"errors"
"fmt"
"io"
"net/url"
"strconv"
"strings"
"time"

"github.com/anishtayin/server/database"
"github.com/google/uuid"
"gorm.io/gorm"
)

var encryptKey = []byte("3xui_encryption_key_2024_secure!")

func generateSubID() string {
bytes := make([]byte, 16)
rand.Read(bytes)
return hex.EncodeToString(bytes)
}

func encrypt(text string) (string, error) {
block, err := aes.NewCipher(encryptKey)
if err != nil {
return "", err
}
plaintext := []byte(text)
ciphertext := make([]byte, aes.BlockSize+len(plaintext))
iv := ciphertext[:aes.BlockSize]
if _, err := io.ReadFull(rand.Reader, iv); err != nil {
return "", err
}
stream := cipher.NewCFBEncrypter(block, iv)
stream.XORKeyStream(ciphertext[aes.BlockSize:], plaintext)
return base64.URLEncoding.EncodeToString(ciphertext), nil
}

func decrypt(encoded string) (string, error) {
block, err := aes.NewCipher(encryptKey)
if err != nil {
return "", err
}
ciphertext, err := base64.URLEncoding.DecodeString(encoded)
if err != nil {
return "", err
}
if len(ciphertext) < aes.BlockSize {
return "", errors.New("ciphertext too short")
}
iv := ciphertext[:aes.BlockSize]
ciphertext = ciphertext[aes.BlockSize:]
stream := cipher.NewCFBDecrypter(block, iv)
stream.XORKeyStream(ciphertext, ciphertext)
return string(ciphertext), nil
}

func checkPassword(hashed, password string) bool {
decrypted, err := decrypt(hashed)
if err != nil {
return false
}
return decrypted == password
}

func Login(username, password string) (bool, error) {
db := database.GetDB()
if db == nil {
return false, errors.New("database not initialized")
}

var user database.User
result := db.Where("username = ?", username).First(&user)
if result.Error != nil {
return false, result.Error
}
if result.RowsAffected == 0 {
return false, errors.New("invalid credentials")
}
if !checkPassword(user.Password, password) {
return false, errors.New("invalid credentials")
}
return true, nil
}

func GetAllInbounds() ([]database.Inbound, error) {
db := database.GetDB()
if db == nil {
return nil, errors.New("database not initialized")
}
var inbounds []database.Inbound
err := db.Preload("Clients").Find(&inbounds).Error
return inbounds, err
}

func GetInbound(id uint) (*database.Inbound, error) {
db := database.GetDB()
if db == nil {
return nil, errors.New("database not initialized")
}
var inbound database.Inbound
err := db.Preload("Clients").First(&inbound, id).Error
return &inbound, err
}

func AddInbound(tag string, port int, protocol string, settings string, streamSettings string, sniffing string, remark string) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
inbound := database.Inbound{
Tag:            tag,
Port:           port,
Protocol:       protocol,
Settings:       settings,
StreamSettings: streamSettings,
Sniffing:       sniffing,
Remark:         remark,
Enable:         true,
}
return db.Create(&inbound).Error
}

func UpdateInbound(id uint, tag string, port int, protocol string, settings string, streamSettings string, sniffing string, remark string, enable bool) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
return db.Model(&database.Inbound{}).Where("id = ?", id).Updates(map[string]interface{}{
"tag":             tag,
"port":            port,
"protocol":        protocol,
"settings":        settings,
"stream_settings": streamSettings,
"sniffing":        sniffing,
"remark":          remark,
"enable":          enable,
}).Error
}

func DeleteInbound(id uint) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
return db.Transaction(func(tx *gorm.DB) error {
tx.Where("inbound_id = ?", id).Delete(&database.Client{})
return tx.Delete(&database.Inbound{}, id).Error
})
}

func AddClient(inboundID uint, email string, clientType string, config map[string]interface{}) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}

subID := generateSubID()
client := database.Client{
InboundID:    inboundID,
Email:        email,
SubID:        subID,
Enable:       true,
TotalTraffic: 0,
UsedTraffic:  0,
ExpiryTime:   0,
}

switch clientType {
case "vmess", "vless":
if uuidVal, ok := config["uuid"].(string); ok {
client.UUID = uuidVal
} else {
client.UUID = uuid.New().String()
}
if flow, ok := config["flow"].(string); ok {
client.Flow = flow
}
if encryption, ok := config["encryption"].(string); ok {
client.Encryption = encryption
}
case "trojan":
if password, ok := config["password"].(string); ok {
client.Password = password
}
case "shadowsocks":
if password, ok := config["password"].(string); ok {
client.Password = password
}
if encryption, ok := config["encryption"].(string); ok {
client.Encryption = encryption
}
}

return db.Create(&client).Error
}

func UpdateClient(id uint, email string, clientType string, config map[string]interface{}, enable bool, totalTraffic int64, expiryTime int64) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}

updates := map[string]interface{}{
"email":       email,
"enable":      enable,
"expiry_time": expiryTime,
}

if totalTraffic > 0 {
updates["total_traffic"] = totalTraffic
}

switch clientType {
case "vmess", "vless":
if uuidVal, ok := config["uuid"].(string); ok {
updates["uuid"] = uuidVal
}
if flow, ok := config["flow"].(string); ok {
updates["flow"] = flow
}
if encryption, ok := config["encryption"].(string); ok {
updates["encryption"] = encryption
}
case "trojan", "shadowsocks":
if password, ok := config["password"].(string); ok {
updates["password"] = password
}
if encryption, ok := config["encryption"].(string); ok {
updates["encryption"] = encryption
}
}

return db.Model(&database.Client{}).Where("id = ?", id).Updates(updates).Error
}

func DeleteClient(id uint) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
return db.Delete(&database.Client{}, id).Error
}

func GetClientBySubID(subID string) (*database.Client, error) {
db := database.GetDB()
if db == nil {
return nil, errors.New("database not initialized")
}
var client database.Client
err := db.Preload("Inbound").Where("sub_id = ?", subID).First(&client).Error
return &client, err
}

func GenerateLink(client *database.Client, inbound *database.Inbound, domain string, isTLS bool) string {
protocol := inbound.Protocol

switch protocol {
case "vmess":
return generateVMessLink(client, inbound, domain, isTLS)
case "vless":
return generateVLESSLink(client, inbound, domain, isTLS)
case "trojan":
return generateTrojanLink(client, inbound, domain, isTLS)
case "shadowsocks":
return generateShadowsocksLink(client, inbound, domain, isTLS)
default:
return ""
}
}

func generateVMessLink(client *database.Client, inbound *database.Inbound, domain string, isTLS bool) string {
network := "tcp"
security := "none"
host := domain

if isTLS {
security = "tls"
}

vmessConfig := map[string]interface{}{
"v":    "2",
"ps":   inbound.Remark + " - " + client.Email,
"add":  domain,
"port": strconv.Itoa(inbound.Port),
"id":   client.UUID,
"aid":  "0",
"net":  network,
"type": "none",
"host": host,
"path": "",
"tls":  security,
}

jsonBytes, _ := json.Marshal(vmessConfig)
encoded := base64.StdEncoding.EncodeToString(jsonBytes)
return "vmess://" + encoded
}

func generateVLESSLink(client *database.Client, inbound *database.Inbound, domain string, isTLS bool) string {
uuid := client.UUID
port := strconv.Itoa(inbound.Port)
security := "none"
if isTLS {
security = "tls"
}

params := url.Values{}
params.Set("type", "tcp")
params.Set("security", security)
if client.Encryption != "" {
params.Set("encryption", client.Encryption)
}

link := fmt.Sprintf("vless://%s@%s:%s", uuid, domain, port)
return link + "?" + params.Encode() + "#" + url.QueryEscape(inbound.Remark+" - "+client.Email)
}

func generateTrojanLink(client *database.Client, inbound *database.Inbound, domain string, isTLS bool) string {
password := client.Password
port := strconv.Itoa(inbound.Port)

link := fmt.Sprintf("trojan://%s@%s:%s", password, domain, port)
return link + "?security=tls#" + url.QueryEscape(inbound.Remark+" - "+client.Email)
}

func generateShadowsocksLink(client *database.Client, inbound *database.Inbound, domain string, isTLS bool) string {
method := client.Encryption
if method == "" {
method = "aes-256-gcm"
}
password := client.Password
port := strconv.Itoa(inbound.Port)

encoded := base64.StdEncoding.EncodeToString([]byte(method + ":" + password))
link := fmt.Sprintf("ss://%s@%s:%s", encoded, domain, port)
return link + "#" + url.QueryEscape(inbound.Remark+" - "+client.Email)
}

func GenerateSubscriptionLink(client *database.Client, domain string, isTLS bool) string {
db := database.GetDB()
var links []string

var inbounds []database.Inbound
db.Where("enable = ?", true).Find(&inbounds)

for _, inbound := range inbounds {
link := GenerateLink(client, &inbound, domain, isTLS)
if link != "" {
links = append(links, link)
}
}

return strings.Join(links, "\n")
}

func GetSetting(key string) string {
db := database.GetDB()
if db == nil {
return ""
}
var setting database.Settings
result := db.Where("key = ?", key).First(&setting)
if result.Error != nil {
return ""
}
return setting.Value
}

func UpdateSetting(key, value string) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
return db.Model(&database.Settings{}).Where("key = ?", key).Update("value", value).Error
}

func ResetClientTraffic(clientID uint) error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
return db.Model(&database.Client{}).Where("id = ?", clientID).Update("used_traffic", 0).Error
}

func ResetAllTraffic() error {
db := database.GetDB()
if db == nil {
return errors.New("database not initialized")
}
return db.Model(&database.Client{}).Update("used_traffic", 0).Error
}

func GetStats() (map[string]interface{}, error) {
db := database.GetDB()
if db == nil {
return nil, errors.New("database not initialized")
}

var totalInbounds, enabledInbounds, totalClients, onlineClients int64
var totalTraffic, usedTraffic int64

db.Model(&database.Inbound{}).Count(&totalInbounds)
db.Model(&database.Inbound{}).Where("enable = ?", true).Count(&enabledInbounds)
db.Model(&database.Client{}).Count(&totalClients)
db.Model(&database.Client{}).Where("enable = ?", true).Count(&onlineClients)

db.Model(&database.Inbound{}).Select("COALESCE(SUM(total_traffic), 0)").Scan(&totalTraffic)
db.Model(&database.Inbound{}).Select("COALESCE(SUM(used_traffic), 0)").Scan(&usedTraffic)

return map[string]interface{}{
"totalInbounds":   totalInbounds,
"enabledInbounds": enabledInbounds,
"totalClients":    totalClients,
"onlineClients":   onlineClients,
"totalTraffic":    totalTraffic,
"usedTraffic":     usedTraffic,
}, nil
}

func GetCurrentTimeMs() int64 {
return time.Now().UnixMilli()
}

func GetExpiryDays(expiryTime int64) int {
if expiryTime == 0 {
return -1
}
now := GetCurrentTimeMs()
remaining := expiryTime - now
if remaining <= 0 {
return 0
}
return int(remaining / (24 * 60 * 60 * 1000))
}

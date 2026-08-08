package database

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"io"
	"sync"
	"time"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var (
	db         *gorm.DB
	once       sync.Once
	encryptKey []byte
)

// generateEncryptKey generates a random encryption key or loads from settings
func generateEncryptKey() {
	key := make([]byte, 32) // AES-256
	if _, err := rand.Read(key); err != nil {
		// Fallback to a default key (should not happen in production)
		key = []byte("fallback_key_32_bytes_long_key!")
	}
	encryptKey = key
}

// User represents admin user
type User struct {
	gorm.Model
	Username string `gorm:"uniqueIndex;not null"`
	Password string `gorm:"not null"`
}

// Inbound represents an inbound configuration
type Inbound struct {
	gorm.Model
	Tag            string   `gorm:"uniqueIndex;not null"`
	Port           int      `gorm:"not null"`
	Protocol       string   `gorm:"not null"`
	Settings       string   `gorm:"type:text"`
	StreamSettings string   `gorm:"type:text"`
	Sniffing       string   `gorm:"type:text"`
	Enable         bool     `gorm:"default:true"`
	Remark         string
	TotalTraffic   int64    `gorm:"default:0"` // bytes
	UsedTraffic    int64    `gorm:"default:0"` // bytes
	ExpiryTime     int64    `gorm:"default:0"` // timestamp in ms
	Clients        []Client `gorm:"foreignKey:InboundID;constraint:OnDelete:CASCADE"`
}

// Client represents a client/user configuration
type Client struct {
	gorm.Model
	InboundID    uint   `gorm:"not null;index"`
	Email        string `gorm:"uniqueIndex;not null"`
	UUID         string
	Flow         string
	Encryption   string
	AlterID      int    `gorm:"default:0"`
	Security     string `gorm:"default:auto"`
	Password     string
	TotalTraffic int64  `gorm:"default:0"` // bytes
	UsedTraffic  int64  `gorm:"default:0"` // bytes
	ExpiryTime   int64  `gorm:"default:0"` // timestamp in ms
	Enable       bool   `gorm:"default:true"`
	SubID        string `gorm:"uniqueIndex"`
	Inbound      Inbound
}

// Stats represents traffic statistics
type Stats struct {
	gorm.Model
	InboundID uint
	ClientID  uint
	Traffic   int64
	Time      time.Time
}

// Settings represents panel settings
type Settings struct {
	gorm.Model
	Key   string `gorm:"uniqueIndex;not null"`
	Value string `gorm:"type:text"`
}

// TrafficLog represents traffic logs for history
type TrafficLog struct {
	gorm.Model
	InboundID   uint
	ClientID    uint
	UpTraffic   int64
	DownTraffic int64
	Date        string `gorm:"index"`
}

// OnlineUser represents currently online users
type OnlineUser struct {
	gorm.Model
	Email     string `gorm:"uniqueIndex"`
	InboundID uint
	IP        string
	LastSeen  time.Time
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

// InitDB initializes the database connection and creates tables
func InitDB() error {
	var initErr error
	once.Do(func() {
		// Generate encryption key on startup
		generateEncryptKey()
		
		db, initErr = gorm.Open(sqlite.Open("/etc/x-ui/x-ui.db?cache=shared"), &gorm.Config{})
		if initErr != nil {
			return
		}
		initErr = db.AutoMigrate(&User{}, &Inbound{}, &Client{}, &Stats{}, &Settings{}, &TrafficLog{}, &OnlineUser{})
		if initErr != nil {
			return
		}
		// Create default admin user if not exists
		var count int64
		db.Model(&User{}).Count(&count)
		if count == 0 {
			hashedPwd := hashPassword("admin")
			db.Create(&User{Username: "admin", Password: hashedPwd})
		}
		// Create default settings
		createDefaultSettings()
	})
	return initErr
}

func createDefaultSettings() {
	settings := []map[string]string{
		{"key": "webPort", "value": "2053"},
		{"key": "webPath", "value": "/xui/"},
		{"key": "webCertFile", "value": ""},
		{"key": "webKeyFile", "value": ""},
		{"key": "subPort", "value": "2096"},
		{"key": "subPath", "value": "/sub/"},
		{"key": "subEncrypt", "value": "true"},
		{"key": "subShowInfo", "value": "true"},
		{"key": "timeLocation", "value": "Asia/Tehran"},
		{"key": "telegramBotToken", "value": ""},
		{"key": "telegramBotChatID", "value": ""},
		{"key": "sessionMaxAge", "value": "0"},
		{"key": "secret", "value": ""},
		{"key": "expireDiff", "value": "0"},
		{"key": "trafficDiff", "value": "0"},
	}
	for _, s := range settings {
		var existing Settings
		result := db.Where("key = ?", s["key"]).First(&existing)
		if result.Error != nil && errors.Is(result.Error, gorm.ErrRecordNotFound) {
			db.Create(&Settings{Key: s["key"], Value: s["value"]})
		}
	}
}

// GetDB returns the database instance
func GetDB() *gorm.DB {
	return db
}

func hashPassword(password string) string {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		// Fallback: should not happen in production
		return ""
	}
	return string(hashed)
}

// CheckPassword verifies a password against its hash
func CheckPassword(hashed, password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hashed), []byte(password))
	return err == nil
}

// CloseDB closes the database connection
func CloseDB() error {
	sqlDB, err := db.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

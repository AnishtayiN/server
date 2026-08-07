package database

import (
	"sync"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var (
	db   *gorm.DB
	once sync.Once
)

type User struct {
	gorm.Model
	Username string `gorm:"uniqueIndex;not null"`
	Password string `gorm:"not null"`
}

type Inbound struct {
	gorm.Model
	Tag      string `gorm:"uniqueIndex;not null"`
	Port     int    `gorm:"not null"`
	Protocol string `gorm:"not null"`
	Settings string `gorm:"type:text"`
	Enable   bool   `gorm:"default:true"`
}

func InitDB() error {
	var err error
	once.Do(func() {
		db, err = gorm.Open(sqlite.Open("/etc/x-ui/x-ui.db"), &gorm.Config{})
		if err != nil {
			return
		}
		err = db.AutoMigrate(&User{}, &Inbound{})
		if err != nil {
			return
		}
	})
	return err
}

func GetDB() *gorm.DB {
	return db
}

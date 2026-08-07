package service

import (
	"crypto/md5"
	"encoding/hex"
	"errors"

	"github.com/anishtayin/server/database"
)

func hashPassword(password string) string {
	hash := md5.Sum([]byte(password))
	return hex.EncodeToString(hash[:])
}

func Login(username, password string) (bool, error) {
	db := database.GetDB()
	if db == nil {
		return false, errors.New("database not initialized")
	}

	var user database.User
	result := db.Where("username = ? AND password = ?", username, hashPassword(password)).First(&user)
	if result.Error != nil {
		return false, result.Error
	}
	if result.RowsAffected == 0 {
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
	err := db.Find(&inbounds).Error
	return inbounds, err
}

func AddInbound(tag string, port int, protocol string, settings string) error {
	db := database.GetDB()
	if db == nil {
		return errors.New("database not initialized")
	}
	inbound := database.Inbound{
		Tag:      tag,
		Port:     port,
		Protocol: protocol,
		Settings: settings,
		Enable:   true,
	}
	return db.Create(&inbound).Error
}

func DeleteInbound(id uint) error {
	db := database.GetDB()
	if db == nil {
		return errors.New("database not initialized")
	}
	return db.Delete(&database.Inbound{}, id).Error
}

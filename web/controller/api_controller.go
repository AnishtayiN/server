package controller

import (
	"net/http"

	"github.com/anishtayin/server/web/service"
	"github.com/gin-gonic/gin"
)

type LoginForm struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type AddInboundForm struct {
	Tag      string `json:"tag" binding:"required"`
	Port     int    `json:"port" binding:"required"`
	Protocol string `json:"protocol" binding:"required"`
	Settings string `json:"settings"`
}

func Login(c *gin.Context) {
	var form LoginForm
	if err := c.ShouldBindJSON(&form); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	success, err := service.Login(form.Username, form.Password)
	if err != nil || !success {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "msg": "Invalid credentials"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Login successful"})
}

func GetInbounds(c *gin.Context) {
	inbounds, err := service.GetAllInbounds()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": inbounds})
}

func AddInbound(c *gin.Context) {
	var form AddInboundForm
	if err := c.ShouldBindJSON(&form); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	if err := service.AddInbound(form.Tag, form.Port, form.Protocol, form.Settings); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Inbound added successfully"})
}

func DeleteInbound(c *gin.Context) {
	_ = c.Param("id")
	if err := service.DeleteInbound(uint(0)); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Inbound deleted successfully"})
}

package controller

import (
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/anishtayin/server/database"
	"github.com/anishtayin/server/web/service"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
)

// JWT secret key - should be loaded from environment in production
var jwtKey = []byte("your-secret-key-change-in-production-2024!")

type Claims struct {
	Username string `json:"username"`
	jwt.RegisteredClaims
}

// AuthMiddleware validates JWT tokens
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tokenString := c.GetHeader("Authorization")
		if tokenString == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"success": false, "msg": "Missing authorization token"})
			c.Abort()
			return
		}

		// Remove Bearer prefix if present
		if strings.HasPrefix(tokenString, "Bearer ") {
			tokenString = strings.TrimPrefix(tokenString, "Bearer ")
		}

		claims := &Claims{}
		token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
			return jwtKey, nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"success": false, "msg": "Invalid or expired token"})
			c.Abort()
			return
		}

		c.Set("username", claims.Username)
		c.Next()
	}
}

type LoginForm struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type AddInboundForm struct {
	Tag            string `json:"tag" binding:"required"`
	Port           int    `json:"port" binding:"required"`
	Protocol       string `json:"protocol" binding:"required"`
	Settings       string `json:"settings"`
	StreamSettings string `json:"streamSettings"`
	Sniffing       string `json:"sniffing"`
	Remark         string `json:"remark"`
	Enable         bool   `json:"enable"`
}

type AddClientForm struct {
	InboundID uint                 `json:"inboundId" binding:"required"`
	Email     string               `json:"email" binding:"required"`
	Type      string               `json:"type" binding:"required"`
	Config    map[string]interface{} `json:"config"`
	Enable    bool                 `json:"enable"`
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

	// Generate JWT token
	claims := &Claims{
		Username: form.Username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":    true,
		"msg":        "Login successful",
		"username":   form.Username,
		"token":      tokenString,
		"expires_in": int64(24 * 60 * 60), // seconds
	})
}

func GetInbounds(c *gin.Context) {
	inbounds, err := service.GetAllInbounds()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": inbounds})
}

func GetInbound(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	inbound, err := service.GetInbound(uint(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": inbound})
}

func AddInbound(c *gin.Context) {
	var form AddInboundForm
	if err := c.ShouldBindJSON(&form); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	if err := service.AddInbound(form.Tag, form.Port, form.Protocol, form.Settings, form.StreamSettings, form.Sniffing, form.Remark); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Inbound added successfully"})
}

func UpdateInbound(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	var form AddInboundForm
	if err := c.ShouldBindJSON(&form); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	if err := service.UpdateInbound(uint(id), form.Tag, form.Port, form.Protocol, form.Settings, form.StreamSettings, form.Sniffing, form.Remark, form.Enable); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Inbound updated successfully"})
}

func DeleteInbound(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	if err := service.DeleteInbound(uint(id)); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Inbound deleted successfully"})
}

func AddClient(c *gin.Context) {
	var form AddClientForm
	if err := c.ShouldBindJSON(&form); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	if err := service.AddClient(form.InboundID, form.Email, form.Type, form.Config); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Client added successfully"})
}

func UpdateClient(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	var form AddClientForm
	if err := c.ShouldBindJSON(&form); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	if err := service.UpdateClient(uint(id), form.Email, form.Type, form.Config, form.Enable, 0, 0); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Client updated successfully"})
}

func DeleteClient(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	if err := service.DeleteClient(uint(id)); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Client deleted successfully"})
}

func GetClientLinks(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	db := database.GetDB()
	var client database.Client
	result := db.Preload("Inbound").First(&client, id)
	if result.Error != nil {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "msg": "Client not found"})
		return
	}

	host := c.Request.Host
	isTLS := strings.HasPrefix(c.Request.URL.Scheme, "https")

	links := service.GenerateLink(&client, &client.Inbound, host, isTLS)
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": gin.H{"links": links, "subId": client.SubID}})
}

func GetQRCode(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	db := database.GetDB()
	var client database.Client
	result := db.Preload("Inbound").First(&client, id)
	if result.Error != nil {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "msg": "Client not found"})
		return
	}

	host := c.Request.Host
	isTLS := strings.HasPrefix(c.Request.URL.Scheme, "https")

	link := service.GenerateLink(&client, &client.Inbound, host, isTLS)
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": gin.H{"qrCodeContent": link, "link": link}})
}

func GetSubscription(c *gin.Context) {
	subID := c.Param("subid")
	
	client, err := service.GetClientBySubID(subID)
	if err != nil {
		c.String(http.StatusNotFound, "Client not found")
		return
	}

	if !client.Enable {
		c.String(http.StatusForbidden, "Client disabled")
		return
	}

	host := c.Request.Host
	isTLS := strings.HasPrefix(c.Request.URL.Scheme, "https")

	subContent := service.GenerateSubscriptionLink(client, host, isTLS)
	
	// Check if subscription should be encrypted
	subEncrypt := service.GetSetting("subEncrypt")
	if subEncrypt == "true" {
		subContent = service.EncodeBase64Subscription(subContent)
	}

	c.Header("Content-Type", "text/plain; charset=utf-8")
	c.String(http.StatusOK, subContent)
}

func GetStats(c *gin.Context) {
	stats, err := service.GetStats()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": stats})
}

func ResetClientTraffic(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": "Invalid ID"})
		return
	}

	if err := service.ResetClientTraffic(uint(id)); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Traffic reset successfully"})
}

func ResetAllTraffic(c *gin.Context) {
	if err := service.ResetAllTraffic(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "msg": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "All traffic reset successfully"})
}

func GetSettings(c *gin.Context) {
	settings := make(map[string]string)
	keys := []string{"webPort", "webPath", "webCertFile", "webKeyFile", "subPort", "subPath", "subEncrypt", "subShowInfo", "timeLocation"}
	
	for _, key := range keys {
		settings[key] = service.GetSetting(key)
	}
	
	c.JSON(http.StatusOK, gin.H{"success": true, "obj": settings})
}

func UpdateSettings(c *gin.Context) {
	var settings map[string]string
	if err := c.ShouldBindJSON(&settings); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "msg": err.Error()})
		return
	}

	for key, value := range settings {
		service.UpdateSetting(key, value)
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "msg": "Settings updated successfully"})
}

package web

import (
	"embed"
	"io/fs"
	"net/http"

	"github.com/anishtayin/server/web/controller"
	"github.com/gin-gonic/gin"
)

//go:embed html/*
var staticFiles embed.FS

func StartWebServer() error {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	api := r.Group("/xui/api")
	{
		// Auth (no auth required for login)
		api.POST("/login", controller.Login)
		
		// All other endpoints require authentication
		api.Use(controller.AuthMiddleware())
		
		// Inbounds
		api.GET("/inbounds", controller.GetInbounds)
		api.GET("/inbound/:id", controller.GetInbound)
		api.POST("/inbound/add", controller.AddInbound)
		api.POST("/inbound/update/:id", controller.UpdateInbound)
		api.DELETE("/inbound/:id", controller.DeleteInbound)
		
		// Clients
		api.POST("/client/add", controller.AddClient)
		api.POST("/client/update/:id", controller.UpdateClient)
		api.DELETE("/client/:id", controller.DeleteClient)
		api.GET("/client/:id/links", controller.GetClientLinks)
		api.GET("/client/:id/qrcode", controller.GetQRCode)
		api.POST("/client/:id/resetTraffic", controller.ResetClientTraffic)
		
		// Stats & Settings
		api.GET("/stats", controller.GetStats)
		api.GET("/settings", controller.GetSettings)
		api.POST("/settings", controller.UpdateSettings)
		api.POST("/resetAllTraffic", controller.ResetAllTraffic)
	}

	// Subscription endpoint (public, no auth required - uses subID for auth)
	r.GET("/sub/:subid", controller.GetSubscription)

	subFS, _ := fs.Sub(staticFiles, "html")
	r.StaticFS("/", http.FS(subFS))

	return r.Run(":2053")
}

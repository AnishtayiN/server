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
		api.POST("/login", controller.Login)
		api.GET("/inbounds", controller.GetInbounds)
		api.POST("/inbound/add", controller.AddInbound)
		api.DELETE("/inbound/:id", controller.DeleteInbound)
	}

	subFS, _ := fs.Sub(staticFiles, "html")
	r.StaticFS("/", http.FS(subFS))

	return r.Run(":2053")
}

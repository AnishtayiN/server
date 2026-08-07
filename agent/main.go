package main

import (
	"flag"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/anishtayin/agent/internal/api"
	"github.com/anishtayin/agent/internal/core"
)

func main() {
	secretPath := flag.String("secret", "/anishtayin-panel", "Secret panel path")
	apiPort := flag.String("port", "8080", "Agent API port")
	xrayAPI := flag.String("xray-api", "127.0.0.1:8080", "Xray gRPC endpoint")
	flag.Parse()

	log.Println("Starting AnishtayiN Agent...")

	xrayMgr, err := core.NewXrayManager(*xrayAPI)
	if err != nil {
		log.Printf("WARNING: Xray API unavailable: %v", err)
	} else {
		defer xrayMgr.Close()
	}

	server := api.NewServer(*secretPath, xrayMgr)

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		if err := server.Start(*apiPort); err != nil {
			log.Fatalf("API server error: %v", err)
		}
	}()

	<-quit
	log.Println("Shutting down...")
}

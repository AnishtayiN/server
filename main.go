package main

import (
"flag"
"fmt"
"log"
"os"
"os/signal"
"syscall"
"time"

"github.com/anishtayin/server/cmd/logger"
"github.com/anishtayin/server/database"
"github.com/anishtayin/server/web"
)

var version = "1.0.0"

func main() {
showVersion := flag.Bool("v", false, "show version")
flag.Parse()

if *showVersion {
fmt.Println(version)
return
}

logger.InitLogger()
log.Println("Starting x-ui server...")

if err := database.InitDB(); err != nil {
log.Fatalf("Failed to initialize database: %v", err)
}

go func() {
if err := web.StartWebServer(); err != nil {
log.Fatalf("Failed to start web server: %v", err)
}
}()

sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
<-sigCh

log.Println("Shutting down server...")
time.Sleep(2 * time.Second)
}

package logger

import (
	"os"
	"path/filepath"

	"github.com/sirupsen/logrus"
)

var log *logrus.Logger

func InitLogger() {
	log = logrus.New()
	log.SetOutput(os.Stdout)
	log.SetFormatter(&logrus.TextFormatter{
		FullTimestamp:   true,
		TimestampFormat: "2006-01-02 15:04:05",
	})
	log.SetLevel(logrus.InfoLevel)

	logDir := "/var/log/x-ui"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		log.Warnf("Failed to create log directory %s: %v", logDir, err)
		// Continue with stdout logging even if file logging fails
	} else {
		file, err := os.OpenFile(filepath.Join(logDir, "x-ui.log"), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
		if err != nil {
			log.Warnf("Failed to open log file: %v", err)
			// Continue with stdout logging
		} else {
			log.SetOutput(file)
		}
	}
}

func Info(args ...interface{}) {
	log.Info(args...)
}

func Error(args ...interface{}) {
	log.Error(args...)
}

func Warn(args ...interface{}) {
	log.Warn(args...)
}

func Debug(args ...interface{}) {
	log.Debug(args...)
}

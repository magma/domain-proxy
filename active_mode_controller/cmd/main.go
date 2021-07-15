package main

import (
	"context"
	"log"
	"os"

	"github.com/domain-proxy/active_move_controller/config"
	"github.com/domain-proxy/active_move_controller/internal/app"
	"github.com/domain-proxy/active_move_controller/internal/signal"
	"github.com/domain-proxy/active_move_controller/internal/time"
)

func main() {
	cfg, err := config.Read()
	if err != nil {
		log.Printf("failed to read config: %s", err)
		os.Exit(1)
	}
	a := app.NewApp(
		app.WithConfig(cfg),
		app.WithClock(&time.Clock{}),
	)
	ctx := context.Background()
	if err := signal.Run(ctx, a); err != nil && err != context.Canceled {
		log.Printf("failed to stop app: %s", err)
		os.Exit(1)
	}
}

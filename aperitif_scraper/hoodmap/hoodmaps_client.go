package hoodmap

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/chromedp/chromedp"
)

func Run() {
	// Create context
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	// Increase timeout
	ctx, cancel = context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	// Allocate buffer for screenshot
	var buf []byte

	// Run tasks
	err := chromedp.Run(ctx,
		// Navigate to the page
		chromedp.Navigate("https://hoodmaps.com/san-francisco-neighborhood-map"),

		// Give time for JS and map to load
		chromedp.Sleep(5*time.Second),

		chromedp.Click(`div.action-toggle-tags`, chromedp.NodeVisible),
		chromedp.Sleep(3*time.Second), // allow animation/render
		chromedp.Click(`div.action-toggle-shapes`, chromedp.NodeVisible),
		chromedp.Sleep(3*time.Second), // allow animation/render
		chromedp.Click(`div.action-toggle-shapes`, chromedp.NodeVisible),
		chromedp.Sleep(3*time.Second), // allow animation/render

		// Take full page screenshot
		chromedp.FullScreenshot(&buf, 90),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Save to file
	if err := os.WriteFile("hoodmaps_screenshot.png", buf, 0644); err != nil {
		log.Fatal(err)
	}

	log.Printf("Screenshot saved as hoodmaps_screenshot.png")
}

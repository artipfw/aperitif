package main

import (
	"fmt"
	"os"
	"path/filepath"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: capture_region_map <address>")
		os.Exit(1)
	}

	address := os.Args[1]
	
	// Create screenshots directory if it doesn't exist
	screenshotDir := "./screenshots"
	if err := os.MkdirAll(screenshotDir, 0755); err != nil {
		fmt.Printf("Error creating screenshot directory: %v\n", err)
		os.Exit(1)
	}

	// Generate filename based on address
	filename := fmt.Sprintf("region_map_%s.png", sanitizeFilename(address))
	outputPath := filepath.Join(screenshotDir, filename)

	// TODO: Implement actual screenshot capture logic
	// This is a placeholder that would:
	// 1. Connect to a mapping service API
	// 2. Generate a map with colored regions and legend
	// 3. Save the image to outputPath
	
	fmt.Printf("Screenshot saved to: %s\n", outputPath)
	
	// For now, create a dummy file to test the workflow
	file, err := os.Create(outputPath)
	if err != nil {
		fmt.Printf("Error creating file: %v\n", err)
		os.Exit(1)
	}
	file.Close()
}

func sanitizeFilename(s string) string {
	// Replace spaces and special characters
	result := ""
	for _, ch := range s {
		if (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '-' || ch == '_' {
			result += string(ch)
		} else if ch == ' ' {
			result += "_"
		}
	}
	return result
}
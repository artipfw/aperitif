package googlemap

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"

	"github.com/chromedp/chromedp"
)

const (
	defaultAddress = "208 Anza St, San Francisco, CA"
	htmlPort       = ":8080"
	outputPNG      = "google_screenshot.png"
)

type GeocodeResponse struct {
	Results []struct {
		Geometry struct {
			Location struct {
				Lat float64 `json:"lat"`
				Lng float64 `json:"lng"`
			} `json:"location"`
		} `json:"geometry"`
	} `json:"results"`
	Status string `json:"status"`
}

func geocode(address, apiKey string) (float64, float64, error) {
	endpoint := "https://maps.googleapis.com/maps/api/geocode/json"
	u := fmt.Sprintf("%s?address=%s&key=%s", endpoint, url.QueryEscape(address), apiKey)

	resp, err := http.Get(u)
	if err != nil {
		return 0, 0, err
	}
	defer resp.Body.Close()

	var result GeocodeResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return 0, 0, err
	}

	if result.Status != "OK" || len(result.Results) == 0 {
		return 0, 0, fmt.Errorf("failed to geocode address: %s", result.Status)
	}

	lat := result.Results[0].Geometry.Location.Lat
	lng := result.Results[0].Geometry.Location.Lng
	return lat, lng, nil
}

func generateMapHTML(lat, lng float64, apiKey string) string {
	return fmt.Sprintf(`
<!DOCTYPE html>
<html>
  <head>
    <title>Map Screenshot</title>
    <style>
      html, body, #map {
        margin: 0;
        padding: 0;
        height: 100%%;
        width: 100%%;
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key=%s"></script>
    <script>
      function initMap() {
        const center = { lat: %f, lng: %f };
        const map = new google.maps.Map(document.getElementById("map"), {
          zoom: 13,
          center: center,
          disableDefaultUI: true
        });
        new google.maps.Marker({
          position: center,
          map: map
        });
      }
      window.onload = initMap;
    </script>
  </head>
  <body>
    <div id="map"></div>
  </body>
</html>`, apiKey, lat, lng)
}

func Run(address ...string) {

	// Use provided address if available, otherwise fallback to default
	selectedAddress := defaultAddress
	if len(address) > 0 && address[0] != "" {
		selectedAddress = address[0]
	}

	// 🔐 Get API key from environment variable
	apiKey := os.Getenv("GOOGLE_MAP_API_KEY")
	if apiKey == "" {
		log.Fatal("GOOGLE_MAP_API_KEY environment variable not set")
	}

	// Step 1: Geocode
	lat, lng, err := geocode(selectedAddress, apiKey)
	if err != nil {
		log.Fatalf("Geocoding failed: %v", err)
	}
	log.Printf("Coordinates: lat=%f, lng=%f", lat, lng)

	// Step 2: Serve the generated HTML
	html := generateMapHTML(lat, lng, apiKey)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, html)
	})
	server := &http.Server{Addr: htmlPort}
	go func() {
		log.Printf("Serving map on http://localhost%s", htmlPort)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()
	defer server.Close()

	// Step 3: Wait and take screenshot
	time.Sleep(3 * time.Second)

	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	var buf []byte
	err = chromedp.Run(ctx,
		chromedp.Navigate("http://localhost"+htmlPort),
		chromedp.Sleep(5*time.Second),
		chromedp.FullScreenshot(&buf, 90),
	)
	if err != nil {
		log.Fatalf("chromedp screenshot failed: %v", err)
	}

	// Step 4: Save screenshot
	if err := os.WriteFile(outputPNG, buf, 0644); err != nil {
		log.Fatalf("Failed to save screenshot: %v", err)
	}
	log.Printf("Screenshot saved to %s", outputPNG)
}

package main

import (
	"github.com/artipfw/aperitif/googlemap"
	"github.com/artipfw/aperitif/hoodmap"
)

func main() {
	// Run Hood Maps client
	hoodmap.Run()

	// Run Google Maps client
	// Address can be set googlemap.Run("your-address-here") if not defaults "208 Anza St, San Francisco, CA"
	googlemap.Run()
}

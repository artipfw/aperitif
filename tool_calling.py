import asyncio
import logging
import os
import subprocess
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

import requests
from playwright.async_api import async_playwright

from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools import tool

DEFAULT_ADDRESS: str = "208 Anza St, San Francisco, CA"
HTML_PORT = 8080
OUTPUT_PNG = "google_screenshot.png"

logging.basicConfig(level=logging.INFO)


@tool(show_result=True)
def hoodmaps(address: str = DEFAULT_ADDRESS) -> str:
    """Captures a screenshot of the San Francisco map from hoodmaps.com."""
    
    async def capture():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://hoodmaps.com/san-francisco-neighborhood-map", timeout=30000)
            await page.wait_for_timeout(5000)

            await page.click("div.action-toggle-tags")
            await page.wait_for_timeout(3000)
            await page.click("div.action-toggle-shapes")
            await page.wait_for_timeout(3000)
            await page.click("div.action-toggle-shapes")
            await page.wait_for_timeout(3000)

            output_path = "hoodmaps_screenshot.png"
            await page.screenshot(path=output_path, full_page=True)

            await browser.close()
            logging.info(f"Screenshot saved to {output_path}")
            return output_path

    # Run the async capture function
    return asyncio.run(capture())

def geocode(address: str, api_key: str):
    params = {
        "address": address,
        "key": api_key,
    }
    url = f"https://maps.googleapis.com/maps/api/geocode/json?{urlencode(params)}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK" or not data["results"]:
        raise Exception(f"Failed to geocode: {data['status']}")

    location = data["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]


def generate_map_html(lat: float, lng: float, api_key: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
  <head>
    <title>Map Screenshot</title>
    <style>
      html, body, #map {{
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
      }}
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key={api_key}"></script>
    <script>
      function initMap() {{
        const center = {{ lat: {lat}, lng: {lng} }};
        const map = new google.maps.Map(document.getElementById("map"), {{
          zoom: 13,
          center: center,
          disableDefaultUI: true
        }});
        new google.maps.Marker({{
          position: center,
          map: map
        }});
      }}
      window.onload = initMap;
    </script>
  </head>
  <body>
    <div id="map"></div>
  </body>
</html>
"""


class MapRequestHandler(BaseHTTPRequestHandler):
    html_content = ""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.html_content.encode("utf-8"))


async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"http://localhost:{HTML_PORT}", timeout=30000)
        await page.wait_for_timeout(5000)
        await page.screenshot(path=OUTPUT_PNG, full_page=True)
        await browser.close()


@tool(show_result=True)
def googlemaps(address: str = DEFAULT_ADDRESS) -> str:
    """
    Takes an address, shows it on a Google Map, and saves a screenshot as 'google_screenshot.png'.
    Returns the file path of the saved screenshot.
    """
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_MAP_API_KEY not set in environment.")

    lat, lng = geocode(address, api_key)
    logging.info(f"Coordinates: lat={lat}, lng={lng}")

    html = generate_map_html(lat, lng, api_key)
    MapRequestHandler.html_content = html

    server = HTTPServer(("localhost", HTML_PORT), MapRequestHandler)
    logging.info(f"Serving map at http://localhost:{HTML_PORT}")

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    try:
        time.sleep(2)
        asyncio.run(take_screenshot())
        logging.info(f"Screenshot saved to {OUTPUT_PNG}")
    finally:
        server.shutdown()
        server.server_close()

    return f"{OUTPUT_PNG}"


def main():
    tt_base_url = os.getenv("TT_BASE_URL")
    model_id = os.getenv("TT_MODEL_ID")

    agent = Agent(
        model=OpenAILike(id=model_id, api_key="nul", base_url=tt_base_url),
        tools=[hoodmaps, googlemaps],
        instructions="""
        You are a Map Agent with access to two mapping tools.

        Your job is to always call **both tools** to retrieve images.

        - Do not interpret or describe the images.
        - Your job is only to call both tools and return the file names.

        When done, end the task silently — no commentary or explanation.
        """,
        markdown=True
    )

    user_query = "Please retrieve images of the location 208 Anza St, San Francisco, CA from both tools."
    agent.print_response(user_query, stream=True)

if __name__ == "__main__":
    main()
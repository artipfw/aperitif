#!/usr/bin/env python3
"""Add a pin to the SF map for testing"""

from PIL import Image, ImageDraw
import os

def add_pin_to_sf_map():
    """Add a visible pin to the SF map"""
    
    # Open the original SF map
    img = Image.open("test_images/sf_map_original.png")
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    
    # Create a copy to draw on
    img_with_pin = img.copy()
    draw = ImageDraw.Draw(img_with_pin)
    
    # Place pin in upper left area where green (Rich) zones typically are
    # Moving pin to upper-left portion of the map
    pin_x = 1400  # More to the left
    pin_y = 900   # Higher up on the map
    
    # Draw a large, visible purple pin (not in our color list)
    # Pin head (circle)
    pin_radius = 40
    draw.ellipse(
        [pin_x - pin_radius, pin_y - pin_radius, 
         pin_x + pin_radius, pin_y + pin_radius],
        fill='purple',  # Using purple - not in our neighborhood colors
        outline='black',
        width=4
    )
    
    # Pin point (triangle)
    draw.polygon(
        [(pin_x, pin_y + pin_radius),
         (pin_x - 25, pin_y + pin_radius + 50),
         (pin_x + 25, pin_y + pin_radius + 50)],
        fill='purple',
        outline='black'
    )
    
    # Add white inner circle for visibility
    draw.ellipse(
        [pin_x - 15, pin_y - 15,
         pin_x + 15, pin_y + 15],
        fill='white'
    )
    
    # Save the result
    output_path = "test_images/sf_map_with_pin.png"
    img_with_pin.save(output_path)
    print(f"Created {output_path} with pin at ({pin_x}, {pin_y})")
    
    return output_path

if __name__ == "__main__":
    add_pin_to_sf_map()
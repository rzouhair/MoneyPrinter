import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def draw_text_with_rectangle(draw, text, font, position, rectangle_color=(255, 255, 0, 128), padding=(20, 10)):
    """
    Draw a rectangle behind text with specified padding
    padding: (horizontal_padding, vertical_padding)
    """
    # Get text dimensions
    bbox = draw.textbbox(position, text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate rectangle dimensions with padding
    rect_x1 = position[0] - padding[0]
    rect_y1 = bbox[1] - padding[1]
    rect_x2 = position[0] + text_width + padding[0]
    rect_y2 = bbox[3] + padding[1]
    
    # Create a separate image for the semi-transparent rectangle
    
    # Draw the rectangle on the overlay
    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill=rectangle_color, width=text_width)
    
    # Composite the overlay onto the main image
    # draw.im.paste(overlay, (0, 0), overlay)

def create_book_quote_image(background_path, quote, output_path, aspect_ratio=(1, 1), font_size=40, font_color=(0, 0, 0), size=(1080, 1080), line_spacing=1.6, rectangle_color=(255, 255, 0, 128), rectangle_padding=(4, 2)):
    # Open the background image
    with Image.open(background_path) as img:
        # Convert to RGBA if not already
        img = img.convert('RGBA')
        
        # Calculate the crop box
        width, height = img.size
        target_ratio = aspect_ratio[0] / aspect_ratio[1]
        current_ratio = width / height
        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            offset = (width - new_width) // 2
            crop_box = (offset, 0, offset + new_width, height)
        else:
            new_height = int(width / target_ratio)
            offset = (height - new_height) // 2
            crop_box = (0, offset, width, offset + new_height)
        
        # Crop the image
        img = img.crop(crop_box)
        
        # Resize the image to the specified size
        standard_size = size
        img = img.resize(standard_size, Image.LANCZOS)
        
        # Create a drawing object
        draw = ImageDraw.Draw(img)
        
        # Load a serif font
        font = ImageFont.truetype(os.path.abspath(os.path.join(os.path.dirname(__file__), "captions/assets/fonts/LibreBaskerville.ttf")), font_size)
        
        # Wrap the text
        margin = 64
        max_width = standard_size[0] - 2 * margin
        wrapped_text = textwrap.fill(quote, width=max_width // (font_size // 2))
        line_spacing_px = int(font_size * line_spacing)
        
        # Get the size of the text
        lines = wrapped_text.split('\n')
        text_width = max(draw.textlength(line, font=font) for line in lines)
        text_height = line_spacing_px * (len(lines) - 1) + font_size * len(lines)
        
        # Calculate the position to center the text both horizontally and vertically
        x = (standard_size[0] - text_width) // 2
        y = (standard_size[1] - (text_height // line_spacing)) // 2
        
        # Draw each line with its rectangle background
        for i, line in enumerate(lines):
            line_width = draw.textlength(line, font=font)
            line_x = (standard_size[0] + line_width)  # Center each line horizontally
            line_y = y + i * line_spacing_px
            
            # Draw rectangle behind the text
            if rectangle_color:
              draw_text_with_rectangle(
                  draw, 
                  line, 
                  font, 
                  (x, line_y), 
                  rectangle_color=rectangle_color,
                  padding=rectangle_padding
              )
            
            # Draw the text
            draw.text((x, line_y), line, font=font, fill=font_color)
        
        # Save the image
        existing_extension = output_path.split('.')[-1]
        png_extension = 'png'
        if existing_extension != png_extension:
            output_path = output_path.replace(f'.{existing_extension}', f'.{png_extension}')
            print(output_path)
        img.save(output_path)
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

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
        
        # Load a serif font
        font = ImageFont.truetype(os.path.abspath(os.path.join(os.path.dirname(__file__), "captions/assets/fonts/LibreBaskerville.ttf")), font_size)
        
        # Resize the image to the specified size
        standard_size = size
        img = img.resize(standard_size, Image.LANCZOS)
        rgba_image = Image.new('RGBA', standard_size, (255, 255, 255, 0))
        rgba_image.paste(img, (standard_size[0] - img.width, standard_size[1] - img.height))
        
        # Create a drawing object
        draw = ImageDraw.Draw(rgba_image)
        
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
            position = (x, line_y)

            if rectangle_color:
              transparent_bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
              transparent_bg = transparent_bg.resize(img.size, Image.LANCZOS)

              current_draw = ImageDraw.Draw(transparent_bg)

              bbox = draw.textbbox(position, line, font=font)
              current_draw.rectangle(bbox, fill=rectangle_color)
              current_draw.text(position, line, font=font, fill=font_color)

              img = Image.alpha_composite(img, transparent_bg)
              # img.paste(transparent_bg, (0, 0), transparent_bg)

            else:
              draw.text((x, line_y), line, font=font, fill=font_color)
            
        
        # Save the image
        existing_extension = output_path.split('.')[-1]
        png_extension = 'png'
        if existing_extension != png_extension:
            output_path = output_path.replace(f'.{existing_extension}', f'.{png_extension}')
            print(output_path)
        img.save(output_path)
        img.show()


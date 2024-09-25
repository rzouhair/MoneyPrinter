import xml.etree.ElementTree as ET

# Path to your type-ghostscript.xml file
file_path = '/usr/local/etc/ImageMagick-7/type-ghostscript.xml'

def add_font_to_typemap(file_path, font_data):
    try:
        # Parse the existing XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Create a new 'type' element with the required attributes
        new_font = ET.Element('type', {
            'encoding': font_data.get('encoding', 'Unicode'),
            'family': font_data['family'],
            'foundry': font_data['foundry'],
            'fullname': font_data['fullname'],
            'glyphs': font_data['glyphs'],
            'name': font_data['name'],
            'stretch': font_data['stretch'],
            'style': font_data['style'],
            'weight': font_data['weight']
        })

        # Append the new font element to the root 'typemap' element
        root.append(new_font)

        # Write the modified XML back to file
        tree.write(file_path, encoding='UTF-8', xml_declaration=True)
        print(f"Font '{font_data['fullname']}' added successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

# Font details to be added
new_font_data = {
    'encoding': 'Unicode',
    'family': 'Montserrat',
    'foundry': 'URW',
    'fullname': 'Montserrat Bold',
    'glyphs': '/usr/share/fonts/truetype/custom/bold_font.ttf',
    'metrics': '/usr/share/fonts/truetype/custom/bold_font.ttf',
    'name': 'Montserrat',
    'stretch': 'Normal',
    'style': 'Bold',
    'weight': '700'
}

# Add the font to the typemap
add_font_to_typemap(file_path, new_font_data)
import xml.etree.ElementTree as ET
from cairosvg import svg2png
import numpy as np

# Path to your original SVG file
input_svg_file = 'italy.svg'

# Path where the modified SVG will be saved
output_svg_file = 'output_image.svg'
output_png_file = 'output_image.png'

population = {
    "valledaosta": 122955,
    "piemonte": 4240736,
    "lombardia": 9950742,
    "trentinoaltoadige": 1075317,
    "veneto": 4838253,
    "friuliveneziagiulia": 1192191, 
    "liguria": 1502624,
    "emiliaromagna": 4426929,
    "toscana": 3651152,
    "marche": 1480839,
    "umbria": 854137,
    "lazio": 5707112,
    "abruzzo": 1269860,
    "molise": 289840,
    "campania": 5592175,
    "puglia": 3900852,
    "basilicata": 536659,
    "calabria": 1841300,
    "sicilia": 4802016,
    "sardegna": 1575028
}

title = "Distribution of the Population of Italy"

# Find the min and max values
min_pop = min(population.values())
max_pop = max(population.values())

palette_values = {
    "0VALUE": int(min_pop),
    "25VALUE": int(min_pop+0.25*(max_pop-min_pop)),
    "50VALUE": int(min_pop+0.5*(max_pop-min_pop)),
    "75VALUE": int(min_pop+0.75*(max_pop-min_pop)),
    "100VALUE": int(max_pop)
}
palette_values["TITLE"] = title

def get_color(value,min_color=(255,255,255),max_color=(255,0,0)):
    # Normalize the value between 0 and 1
    relative_value = (value - min_pop) / (max_pop - min_pop)
    color_vector = [max_color[i] - min_color[i] for i in range(3)]
    color_vector /= np.linalg.norm(color_vector)
    final_color = [int(min_color[i] + relative_value * color_vector[i] * 255) for i in range(3)]

    red = final_color[0]
    green = final_color[1]
    blue = final_color[2]
    # Format as hex color code
    return f'#{red:02X}{green:02X}{blue:02X}'

# Create a new dictionary for color mapping
colors = {region: get_color(pop) for region, pop in population.items()}

# Parse the SVG file
tree = ET.parse(input_svg_file)
root = tree.getroot()

# Namespace handling if your SVG has namespaces
namespaces = {'svg': 'http://www.w3.org/2000/svg'}

# Update the fill color based on the dictionary
for path in root.findall('.//svg:path', namespaces):
    path_id = path.get('id')
    if path_id in colors:
        new_color = colors[path_id]
        style = path.get('style')
        # Split the style into components and modify the fill
        styles = style.split(';')
        new_styles = []
        for s in styles:
            if s.strip().startswith('fill:'):
                # Change the fill color
                new_styles.append(f"fill:{new_color}")
            else:
                new_styles.append(s)
        # Set the modified style back
        path.set('style', ';'.join(new_styles))

# Set the values
for path in root.findall('.//svg:text',namespaces):
    path_id = path.get('id')
    if path_id in palette_values:
        new_text = palette_values[path_id]
        tspan = path.find('svg:tspan',namespaces)
        tspan.text = str(new_text)
    
#find the tag svg/defs/lineargradient with id linearGradient2 and change the first stop-color (within styles) to get_color(max_pop) and the second stop to get_color(min_pop)
for linearGradient in root.findall('.//svg:defs/svg:linearGradient',namespaces):
    if linearGradient.get('id') == 'linearGradient2':
        for stop in linearGradient.findall('svg:stop',namespaces):
            if stop.get('offset') == '0':
                stop.set('style',f'stop-color:{get_color(min_pop)};stop-opacity:1;')
            elif stop.get('offset') == '1':
                stop.set('style',f'stop-color:{get_color(max_pop)};stop-opacity:1;')


# Save the modified SVG
tree.write(output_svg_file)

# Convert the tree back to a string
updated_svg = ET.tostring(root, encoding='unicode')

# Convert the updated SVG to a PNG file
svg2png(bytestring=updated_svg, write_to=output_png_file)

print("SVG has been converted and colored. Output saved as PNG.")


import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract parts
left_pattern = r"(      <!-- Left: Monaco Code Editor -->\n      <section class=\"panel editor-panel\" id=\"editor-panel\">.*?      </section>\n)"
resizer_pattern = r"(\n      <!-- Resizer for Main Layout -->\n      <div class=\"pane-resizer\" id=\"main-pane-resizer\"></div>\n)"
right_pattern = r"(\n      <!-- Right: Review \+ Chat -->\n      <aside class=\"right-panel\" id=\"right-panel\">.*?      </aside>\n)"

left_match = re.search(left_pattern, html, re.DOTALL)
resizer_match = re.search(resizer_pattern, html, re.DOTALL)
right_match = re.search(right_pattern, html, re.DOTALL)

if left_match and resizer_match and right_match:
    left_content = left_match.group(1)
    resizer_content = resizer_match.group(1)
    right_content = right_match.group(1)
    
    # Change comments to reflect new positions
    new_right_content = right_content.replace("<!-- Right: Review + Chat -->", "<!-- Left: Review + Chat -->")
    new_left_content = left_content.replace("<!-- Left: Monaco Code Editor -->", "<!-- Right: Monaco Code Editor -->")
    
    new_html = html[:left_match.start()] + new_right_content.strip("\n") + "\n" + resizer_content + "\n" + new_left_content.strip("\n") + "\n" + html[right_match.end():]
    
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Swapped successfully")
else:
    print("Could not find patterns")

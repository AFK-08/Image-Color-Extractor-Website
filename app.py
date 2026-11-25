from flask import Flask ,render_template,request
from PIL import Image
import numpy as np
import base64
from io import BytesIO

app = Flask(__name__)

def get_top_colors(image, count=10):
    image = image.convert("RGB")
    image.thumbnail((200, 200))  

    small = image.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    palette = np.array(small.getpalette()[:count * 3]).reshape(-1, 3)

    counts = np.bincount(np.array(small).flatten(), minlength=len(palette))[:len(palette)]
    total = counts.sum()

    # Sort from most common to least common
    
    order = np.argsort(counts)[::-1]

    result = []
    for i in order:
        if counts[i] == 0:
            continue
        r, g, b = (int(v) for v in palette[i])
        result.append({
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "percent": round(float(counts[i] / total * 100), 1),
        })
    return result

## small preview of the image to display on the page

def make_preview(image):

    small = image.convert("RGB")
    small.thumbnail((400, 400))
    buffer = BytesIO()
    small.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def home():
    colors, preview, error = None, None, None

    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            error = "Please choose an image."
        else:
            try:
                image = Image.open(file.stream)
                preview = make_preview(image)
                colors = get_top_colors(image)
            except Exception:
                error = "That file is not a valid image."

    return render_template("index.html", colors=colors, preview=preview, error=error)


if __name__ == "__main__":
    app.run(debug=True)

import io
import json
import urllib.request
from PIL import Image
import numpy as np

def predict(name, make_image):
    img = Image.fromarray(make_image())
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    data = buf.getvalue()
    boundary = "----testboundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request("http://localhost:5000/predict", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    resp = urllib.request.urlopen(req)
    out = json.loads(resp.read())
    print(f"\n=== {name} ===")
    print(f"tumor_type: {out.get('tumor_type')} | confidence: {out.get('confidence')}%")
    print(f"probabilities: {out.get('probabilities')}")
    return out

# Glioma-like
predict("glioma", lambda: np.full((224, 224, 3), 200, dtype=np.uint8))

# Medulloblastoma-like posterior
def medullo():
    a = np.zeros((224, 224, 3), dtype=np.uint8)
    a[:100] = 70
    a[130:] = 210
    return a

predict("medulloblastoma", medullo)

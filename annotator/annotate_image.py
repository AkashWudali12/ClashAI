from ultralytics import YOLOE

# Prompt free (i.e. no guiding prompt)
model = YOLOE("yoloe-11l-seg.pt")
names = ["mostly black + blue", "light blue and white", "gold", "red", "text", "countdown"]
model.set_classes(names, model.get_text_pe(names))
results = model.predict("videos/vid_1.mp4",
                        show=True,
                        save=True,
                        show_conf=False,
                        stream=True)
for r in results:
    boxes = r.boxes  # Boxes object for bbox outputs
    masks = r.masks  # Masks object for segment masks outputs
    probs = r.probs  # Class probabilities for classification outputs
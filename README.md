#  facial-recognition

Facial recogntion in Python. Trains on specific images and can then identify faces from more images or a live webcam.

Uses OpenCV.

## Usage

All code should be put in  `__main__`:

First, define an instance of FaceRecogition, and clear the currently trained faces:

```
fr = FaceRecogition()
fr.clear_faces()
```

### Train faces

```
fr.train_face('[PATH_TO_IMAGE]', {
    "name": "[NAME_OF_FACE]"
})
```

### Identify Face by Image

```
print(fr.recognize_faces('[PATH_TO_IMAGE]'))
```

### Identify Face by Live Webcam

```
fr.webcam()
```

## Running

In the root of the project directory:

`$ python3 face_rec.py`

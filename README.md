# PronunciationAssistant

**Overview:**
This project is a comprehensive Pronunciation Assistant with an integrated Object Detection feature. The tool is designed to help users improve their pronunciation while also identifying objects in real-time using a webcam. The application provides feedback on spoken sentences, highlighting pronunciation mistakes and offering corrections. It also detects objects in the user's environment and displays them with labels.

**Some technologies:**
- Tkinter for the Graphical User Interface (GUI)
- Wav2Vec2 for speech-to-text processing and pronunciation analysis
- Yolov5 for object detection via webcam feed
- Google Translate API for pronunciation feedback and real-time translation

**Features**
1. Pronunciation Assistant
Speech-to-Text Conversion: Converts your spoken sentences into text using the Wav2Vec2 model.
Pronunciation Feedback: Identifies pronunciation mistakes and provides suggestions for improvement.
Grammar Check: Highlights grammar mistakes and suggests corrections using language_tool_python.
Translation: Offers real-time translation of input sentences to a desired language.
2. Object Detection
Real-time Object Detection: Uses Yolov5 to detect objects in the user's environment through a webcam feed.
Labeling: Detected objects are labeled and displayed on the GUI.

**Usage**
1. Pronunciation Assistant:
Input a sentence: Enter the sentence you'd like to speak or receive feedback on.
Speak: The program will convert your speech to text and compare it to the input sentence.
Receive Feedback: View pronunciation and grammar suggestions on the GUI.
2. Object Detection
Activate Webcam: The webcam feed will be displayed, and objects detected in real-time will be labeled.
Object Labels: Identified objects will appear with labels in the GUI.

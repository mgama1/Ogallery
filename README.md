# Ogallery

Ogallery is an open-source image gallery application designed to revolutionize the way users manage and interact with their images on desktop. With a focus on user experience, Ogallery combines advanced search capabilities, seamless image viewing and editing functionalities, and robust security features to ensure your photos are not only organized but also protected. 

![image](https://github.com/user-attachments/assets/50b261f9-c025-4c53-80aa-e6197499c0ef)

## Website
Visit the website from ![here](https://ogalleryapp.github.io)

## Explicit list of all the features

### Viewer features:
 - Secure folder
 - Show containing folder
 - Full-screen mode
 - Copy to clipboard
 - Move to trash
 - QR-Code scan
 - Image properties
   
### Editing features:
 - Adjust (Contrast, Brightness, Saturation, Hue)
 - Grayscale 
 - Rotation (clockwise and counterclockwise)
 - Cropping
 - Flipping (vertically and horizontally)
 - Portrait(blur background)
 - Compare
 - Revert
 - Undo
 

### Gallery features:
 - Caching
 - Lazy loading
 - Back to top
 - Select and delete batch
### search features:
 - Search on common classes
 - Search filenames
 - Misspelling handling
 - Autocomplete suggestion 



## installation
If you wish to run the App in a python virtual environment

1- Install venv (if not already installed)

```bash
sudo apt install python3-venv
```
2- Navigate to the project directory and create the environment

```bash
python3 -m venv ogalleryenv
```
3-Activate the virtual environment

```bash
source ogalleryenv/bin/activate
```
4-Install dependencies

```bash
pip install -r requirements.txt
```
5-Finally run the app
```bash
python3 ogallery.py
```



### License

This project is licensed under GPL-3.0 license.
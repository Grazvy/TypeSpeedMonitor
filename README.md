# TypeSpeedMonitor

environment setup
```
conda install anaconda::pyqt 
conda install conda-forge::pynput
pip install appdirs
pip install matplotlib
```
build executable
```
pyinstaller --onedir --windowed \
    --icon=resources/icon.icns \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import pynput \
    --hidden-import pynput.keyboard \
    --hidden-import pynput.mouse \
    --hidden-import matplotlib \
    --hidden-import matplotlib.backends.backend_qtagg \
    --hidden-import appdirs \
    --name "TypeSpeedMonitor" \
    main.py
```
build .dmg file
```
hdiutil create -volname "TypeSpeedMonitor" -srcfolder dist/TypeSpeedMonitor.app -ov -format UDZO TypeSpeedMonitor.dmg    
```
create icon set
```
mkdir icon.iconset
sips -z 16 16     app_icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     app_icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     app_icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     app_icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   app_icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   app_icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   app_icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   app_icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   app_icon.png --out icon.iconset/icon_512x512.png
cp app_icon.png icon.iconset/icon_512x512@2x.png

iconutil -c icns icon.iconset
```

todo:

- increase icon size
- permission settings guide (apple)
  1. add accessibility permissions
  2. (if not working) add to applications
  3. add input monitoring permission
  4. (if not working) delete both permission instances (-)
  5. restart app
  6. add accessibility and input monitoring permission again
- fix tooltip not disheartening

- default config.json
- draw dates on graph instead of title
- fix rounding bug, 2 min off
- fix buggy canvas resizing
- more styles
- performance analysis and optimization
- reset db setting
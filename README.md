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
pyinstaller --onefile --windowed \
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
todo:

- make executables
- make a splash screen?

- default config.json
- draw dates on graph instead of title
- fix rounding bug, 2 min off
- fix buggy canvas resizing
- more styles
- performance analysis and optimization
- reset db setting
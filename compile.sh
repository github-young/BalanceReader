#pyside6-rcc resources.qrc -o resources.py

/usr/lib/qt6/rcc -g python resources.qrc -o resources.py
python -m nuitka --standalone --onefile --enable-plugin=pyside6 --windows-icon-from-ico=icon.ico --disable-console BalanceReader.py

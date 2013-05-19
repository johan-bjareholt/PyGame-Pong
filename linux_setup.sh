#!/bin/bash
echo Removing old version
rm -r ./dist/linux
echo Copying resource files for new version
mkdir ./dist/linux
cp -r ./src/* ./dist/linux
rm -r ./dist/linux/*.py
rm -r ./dist/linux/*.pyc
echo Compiling new version
python ./pyinstaller/pyinstaller.py --onefile --log-level=ERROR "src/client.py"
echo Finishing...
mv dist/client dist/linux/
echo Done!

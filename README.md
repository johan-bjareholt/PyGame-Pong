PyGame-Pong
===========

#### Summary
A Pong game with multiplayer support made in Python with PyGame

### Info 
Python version: 2.7
required libraries:
	PyGame
	PyYAML



###How to run
This is how to run it from source

####Prepare
Install python2.7 and these libraries
```
pip install yaml
pip install pygame
```


####Start
Simply run the client.py from the src folder



###How to Compile
If you want to compile this package by some wierd reason, here's how!

####Mac
Libs needed: Py2app

cd to src directory and run this command:
`python2 mac_compile.py py2app`

####Windows
Libs needed: Py2exe

cd to src directory and run this command:
`python2 win_compile.py py2exe`

####Linux:
Libs needed: PyInstaller

cd to src directory and run this command:
`sh linux_compile.sh`

#Setup for unix-based OS
setup-unix: requirements.txt
	./setup.sh

#Setup for Windows OS
setup-windows: requirements.txt
	cmd /C setup.bat
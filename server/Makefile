.PHONY: install build clean

install:
    pip install -r requirements.txt

build:
    python -m PyInstaller --onefile app_server.py

clean:
    find . -name '*.pyc' -delete
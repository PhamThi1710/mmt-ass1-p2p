.PHONY: install build clean

install:
    pip install -r requirements.txt

build:
    python -m PyInstaller --onefile app_client.py

clean:
    find . -name '*.pyc' -delete
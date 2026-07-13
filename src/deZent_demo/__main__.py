#!/usr/bin/env python3
import sys
from .dZ_demo_app import App

def main():
    app: App = App()
    exit_code: int = app.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
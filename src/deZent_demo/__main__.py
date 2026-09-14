#!/usr/bin/env python3
import sys

from .app import App

def main():
    args: list[str] = sys.argv
    app: App = App(args=args)

    exit_code: int = app.exec()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
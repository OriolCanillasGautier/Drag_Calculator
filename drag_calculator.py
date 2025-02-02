# drag_calculator.py
from ttkthemes import ThemedTk
from gui import WindTunnelApp

def main():
    root = ThemedTk(theme="arc")
    app = WindTunnelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

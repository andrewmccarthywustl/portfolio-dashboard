import tkinter as tk
from stock_portfolio_app import StockPortfolioApp


def main():
    root = tk.Tk()
    app = StockPortfolioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

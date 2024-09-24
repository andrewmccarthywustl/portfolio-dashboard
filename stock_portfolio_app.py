import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import squarify
from datetime import datetime
import os
import numpy as np
from api_client import fetch_stock_data, get_stock_info
from config import CSV_FILE
from utils import load_transactions, save_transactions_to_csv


class StockPortfolioApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Stock Portfolio Visualizer")
        self.master.geometry("1200x800")

        self.create_widgets()
        self.load_transactions()
        self.update_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(main_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)  # Prevent the frame from shrinking

        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columns = (
        "Date", "Symbol", "Quantity", "Buy Price", "Current Price", "Last Updated", "Sector", "Industry", "Beta")
        self.tree = ttk.Treeview(self.left_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=65)  # You might want to adjust widths

        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Add Transaction", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Data", command=self.update_data).pack(side=tk.LEFT, padx=5)

        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_transactions(self):
        transactions = load_transactions(CSV_FILE)
        for transaction in transactions:
            # Fetch additional info if not present
            if len(transaction) < 9:
                symbol = transaction[1]
                sector, industry, beta = get_stock_info(symbol)
                transaction.extend(['', '', sector, industry, beta])
            self.tree.insert("", "end", values=transaction)

    def add_transaction(self):
        symbol = simpledialog.askstring("New Transaction", "Enter stock symbol:")
        if not symbol:
            return

        quantity = simpledialog.askfloat("New Transaction", "Enter quantity (can be fractional):")
        if quantity is None:
            return

        price = simpledialog.askfloat("New Transaction", "Enter purchase price:")
        if price is None:
            return

        date = simpledialog.askstring("New Transaction", "Enter date (YYYY-MM-DD):",
                                      initialvalue=datetime.now().strftime("%Y-%m-%d"))
        if not date:
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        last_updated = ""
        sector, industry, beta = get_stock_info(symbol.upper())

        item = self.tree.insert("", "end",
                                values=(
                                    date, symbol.upper(), f"{quantity:.4f}", f"{price:.2f}", f"{price:.2f}",
                                    last_updated, sector, industry, f"{beta:.2f}"))

        df = pd.DataFrame([[date, symbol.upper(), quantity, price, price, last_updated, sector, industry, beta]],
                          columns=["Date", "Symbol", "Quantity", "Buy Price", "Current Price", "Last Updated",
                                   "Sector", "Industry", "Beta"])
        df.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)

        self.update_single_entry(item)
        self.update_data()

    def update_single_entry(self, item):
        values = self.tree.item(item)["values"]
        date, symbol, quantity, buy_price, current_price, last_updated, sector, industry, beta = values
        quantity = float(quantity)
        buy_price = float(buy_price)

        new_price, new_last_updated = fetch_stock_data(symbol, last_updated)
        if new_price is not None:
            self.tree.item(item, values=(
                date, symbol, f"{quantity:.4f}", f"{buy_price:.2f}", f"{new_price:.2f}", new_last_updated, sector,
                industry, beta))
            self.save_transactions_to_csv()

    def update_data(self):
        portfolio = {}
        total_value = 0
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            date, symbol, quantity, buy_price, current_price, last_updated, sector, industry, beta = values

            try:
                quantity = float(quantity)
                buy_price = float(buy_price)
                current_price = float(current_price)
                beta = float(beta) if beta else float('nan')
            except ValueError:
                print(f"Error converting values for {symbol}: {values}")
                continue

            if symbol not in portfolio:
                portfolio[symbol] = {
                    'transactions': [],
                    'total_quantity': 0,
                    'total_value': 0,
                    'weighted_buy_price': 0,
                    'current_price': 0,
                    'date': date,
                    'last_updated': last_updated,
                    'sector': sector,
                    'industry': industry,
                    'beta': beta
                }

            portfolio[symbol]['transactions'].append({
                'date': date,
                'quantity': quantity,
                'buy_price': buy_price
            })
            portfolio[symbol]['total_quantity'] += quantity
            portfolio[symbol]['total_value'] += quantity * current_price
            total_value += quantity * current_price

            # Calculate weighted average buy price
            total_cost = sum(t['quantity'] * t['buy_price'] for t in portfolio[symbol]['transactions'])
            portfolio[symbol]['weighted_buy_price'] = total_cost / portfolio[symbol]['total_quantity']

            portfolio[symbol]['date'] = min(portfolio[symbol]['date'], date)

            try:
                new_price, new_last_updated = fetch_stock_data(symbol, last_updated)
                if new_price is not None:
                    portfolio[symbol]['current_price'] = new_price
                    portfolio[symbol]['last_updated'] = new_last_updated
                    self.tree.item(item, values=(
                        date, symbol, f"{quantity:.4f}", f"{buy_price:.2f}", f"{new_price:.2f}", new_last_updated,
                        sector, industry, beta))
                else:
                    portfolio[symbol]['current_price'] = current_price

                portfolio[symbol]['pct_change'] = (portfolio[symbol]['current_price'] - portfolio[symbol][
                    'weighted_buy_price']) / portfolio[symbol]['weighted_buy_price'] * 100
                print(
                    f"Debug: {symbol} - Weighted Buy Price: {portfolio[symbol]['weighted_buy_price']:.2f}, Current Price: {portfolio[symbol]['current_price']:.2f}, Pct Change: {portfolio[symbol]['pct_change']:.2f}%")
            except Exception as e:
                print(f"Error updating {symbol}: {str(e)}")
                portfolio[symbol]['current_price'] = current_price
                portfolio[symbol]['pct_change'] = 0

        # Calculate portfolio beta
        if total_value > 0:
            portfolio_beta = sum(stock['beta'] * stock['total_value'] for stock in portfolio.values() if
                                 not np.isnan(stock['beta'])) / total_value
        else:
            portfolio_beta = float('nan')

        print(f"Portfolio Beta: {portfolio_beta:.2f}")

        self.create_treemap(portfolio)
        self.save_transactions_to_csv()

    def create_treemap(self, portfolio):
        self.ax.clear()

        if not portfolio:
            self.ax.text(0.5, 0.5, "No data to display", ha='center', va='center')
            self.ax.axis('off')
            self.canvas.draw()
            return

        sizes = [data['total_value'] for data in portfolio.values()]
        labels = [
            f"{symbol}\nValue: ${data['total_value']:.2f}\n"
            f"Change: {data['pct_change']:.2f}%\n"
            f"Avg Buy: ${data['weighted_buy_price']:.2f}\n"
            f"Current: ${data['current_price']:.2f}\n"
            f"Quantity: {data['total_quantity']:.2f}\n"
            f"Sector: {data['sector']}\n"
            f"Industry: {data['industry']}\n"
            f"Beta: {data['beta']:.2f}"
            for symbol, data in portfolio.items()
        ]

        colors = ['red', 'white', 'green']
        n_bins = 100
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom", colors, N=n_bins)

        pct_changes = [data['pct_change'] for data in portfolio.values()]
        max_abs_pct = max(abs(min(pct_changes)), abs(max(pct_changes)), 10)
        norm = mcolors.Normalize(vmin=-max_abs_pct, vmax=max_abs_pct)

        colors = [custom_cmap(norm(pct_change)) for pct_change in pct_changes]

        squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8, ax=self.ax, text_kwargs={'fontsize': 8})
        self.ax.axis('off')

        total_value = sum(data['total_value'] for data in portfolio.values())
        if total_value > 0:
            portfolio_beta = sum(data['beta'] * data['total_value'] for data in portfolio.values() if
                                 not np.isnan(data['beta'])) / total_value
        else:
            portfolio_beta = float('nan')
        self.ax.set_title(f"Portfolio Beta: {portfolio_beta:.2f}", fontsize=14, fontweight='bold')

        self.fig.tight_layout()
        self.canvas.draw()

    def save_transactions_to_csv(self):
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            data.append(values)
        save_transactions_to_csv(CSV_FILE, data)
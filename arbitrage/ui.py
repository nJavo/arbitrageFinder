import itertools
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from arbitrage.engine import is_arbitrage_multi, calculate_stakes_multi


class ArbitrageUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Arbitrage Bet Mocker")
        
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        self.is_running = False
        self.run_button = ttk.Button(self.control_frame, text="▶ Start Fetching", command=self.toggle_running)
        self.run_button.pack(side="left", padx=5)
        
        self.status_label = ttk.Label(root, text="Last API Update: N/A")
        self.status_label.pack(side="bottom", fill="x")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        self.profitable_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profitable_frame, text="Profitable Arbitrages")

        self.profitable_tree_frame = ttk.Frame(self.profitable_frame)
        self.profitable_tree_frame.pack(fill="both", expand=True)
        
        self.profitable_tree = ttk.Treeview(
            self.profitable_tree_frame,
            columns=("Action", "Match", "Profit", "Time"),
            show="headings",
        )
        
        self.profitable_tree.heading("Action", text="")
        self.profitable_tree.heading("Match", text="Match")
        self.profitable_tree.heading("Profit", text="Profit")
        self.profitable_tree.heading("Time", text="Time")
        
        self.profitable_tree.column("Action", width=30, anchor="center", stretch=False)
        self.profitable_tree.column("Match", width=300)
        self.profitable_tree.column("Profit", width=100)
        self.profitable_tree.column("Time", width=100)

        profitable_scrollbar = ttk.Scrollbar(self.profitable_tree_frame, orient="vertical", command=self.profitable_tree.yview)
        profitable_scrollbar.pack(side="right", fill="y")
        self.profitable_tree.configure(yscrollcommand=profitable_scrollbar.set)
        
        self.profitable_tree.pack(side="left", expand=True, fill="both")
        
        self.profitable_tree.bind("<ButtonRelease-1>", self._on_profitable_tree_click)
        
        self.expanded_items = set()
        
        self.all_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.all_frame, text="All Odds Scanned")

        self.all_tree = ttk.Treeview(
            self.all_frame,
            columns=("Match", "Home", "Away", "Arb?", "Profit", "Time"),
            show="headings",
        )
        for col in self.all_tree["columns"]:
            self.all_tree.heading(col, text=col, command=lambda _col=col: self._treeview_sort_column(self.all_tree, _col, False))
            self.all_tree.column(col, width=120)
        
        all_scrollbar = ttk.Scrollbar(self.all_frame, orient="vertical", command=self.all_tree.yview)
        all_scrollbar.pack(side="right", fill="y")
        self.all_tree.configure(yscrollcommand=all_scrollbar.set)
        
        self.all_tree.pack(expand=True, fill="both")
        self.all_tree.bind("<Double-1>", self._on_double_click)
        
        self.arb_details = {}
        
    def toggle_running(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.run_button.config(text="⏸ Pause Fetching")
            self.status_label.config(text="Fetching odds...")
        else:
            self.run_button.config(text="▶ Start Fetching")
            self.status_label.config(text="Fetching paused. Last update: " + 
                                    datetime.now().strftime("%H:%M:%S"))

    def is_fetching_enabled(self):
        return self.is_running

    def add_arbitrage(self, match_id: str, match_name: str, home: float, away: float, profit: float) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        
        self.arb_details[match_id] = {
            "match_name": match_name,
            "home_odds": home,
            "away_odds": away,
            "profit": profit,
            "time": now
        }
        
        odds_list = [home, away]
        stakes_info = calculate_stakes_multi(odds_list, 100)
        self.arb_details[match_id]["stakes"] = stakes_info["stakes"]
        
        self.profitable_tree.insert(
            "",
            "end",
            iid=match_id,
            values=("➕", match_name, f"${profit:.2f}", now),
            tags=("arb",)
        )
        
        self.profitable_tree.tag_configure("arb", background="#dfffd6")

    def add_any_match(
        self,
        match_id: str,
        match_name: str,
        home: float,
        away: float,
        is_arb: bool,
        profit: float,
    ) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        icon = "✅" if is_arb else "❌"
        color = "green" if is_arb else "red"
        row = self.all_tree.insert(
            "",
            "end",
            iid=match_id,
            values=(match_name, home, away, icon, f"${profit:.2f}", now),
        )
        self.all_tree.item(row, tags=(color,))
        self.all_tree.tag_configure("green", foreground="green")
        self.all_tree.tag_configure("red", foreground="red")

    def load_from_history(self, history_entries: list) -> None:
        counter = 0
        for entry in history_entries:
            if entry.get("is_arb", False):
                match_id = entry.get("match_id", f"hist_{counter}")
                bookmakers = entry.get("bookmakers", [])
                
                if not bookmakers:
                    continue
                    
                home_best = max(b["price_home"] for b in bookmakers if b["price_home"])
                draw_prices = [b.get("price_draw") for b in bookmakers if b.get("price_draw")]
                draw_best = max(draw_prices) if draw_prices else None
                away_best = max(b["price_away"] for b in bookmakers if b["price_away"])
                
                self.add_any_match(
                    match_id=match_id,
                    match_name=match_id,
                    home=home_best,
                    away=away_best,
                    is_arb=True,
                    profit=entry.get("profit", 0.0)
                )
                
                self.add_arbitrage(
                    match_id=match_id,
                    match_name=match_id,
                    home=home_best,
                    away=away_best,
                    profit=entry.get("profit", 0.0)
                )
                
                counter += 1
        
        if counter > 0:
            self.status_label.config(text=f"Loaded {counter} historical arbitrages")

    def update_last_api_time(self) -> None:
        if self.is_running:
            self.status_label.config(text=f"Last API Update: {datetime.now().strftime('%H:%M:%S')}")
    
    def _on_profitable_tree_click(self, event):
        """Handle clicks on the profitable tree"""
        region = self.profitable_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        column = self.profitable_tree.identify_column(event.x)
        if column != "#1":
            return
            
        item_id = self.profitable_tree.identify_row(event.y)
        if not item_id:
            return
        
        if item_id in self.expanded_items:
            self._collapse_item(item_id)
        else:
            self._expand_item(item_id)
    
    def _expand_item(self, item_id):
        """Expand an item to show details"""
        if item_id not in self.arb_details:
            return
            
        details = self.arb_details[item_id]
        
        self.profitable_tree.item(item_id, values=("➖", 
                                                  self.profitable_tree.item(item_id)["values"][1],
                                                  self.profitable_tree.item(item_id)["values"][2],
                                                  self.profitable_tree.item(item_id)["values"][3]))
        
        home_stake = details["stakes"][0]
        away_stake = details["stakes"][1]
        
        home_id = f"{item_id}_home"
        away_id = f"{item_id}_away"
        summary_id = f"{item_id}_summary"
        
        self.profitable_tree.insert(
            "", "end", iid=home_id,
            values=("", f"Home Bet - Odds: {details['home_odds']:.2f}", f"Stake: ${home_stake:.2f}", ""),
            tags=("detail",)
        )
        
        self.profitable_tree.insert(
            "", "end", iid=away_id,
            values=("", f"Away Bet - Odds: {details['away_odds']:.2f}", f"Stake: ${away_stake:.2f}", ""),
            tags=("detail",)
        )
        
        total_stake = sum(details["stakes"])
        self.profitable_tree.insert(
            "", "end", iid=summary_id,
            values=("", "Summary", f"Total: ${total_stake:.2f}", f"ROI: {(details['profit']/total_stake*100):.2f}%"),
            tags=("summary",)
        )
        
        parent_idx = self.profitable_tree.index(item_id)
        self.profitable_tree.move(home_id, "", parent_idx + 1)
        self.profitable_tree.move(away_id, "", parent_idx + 2)
        self.profitable_tree.move(summary_id, "", parent_idx + 3)
        
        self.expanded_items.add(item_id)
        
        self.profitable_tree.tag_configure("detail", background="#f0f0f0")
        self.profitable_tree.tag_configure("summary", background="#e0e0e0", font=("Arial", 9, "bold"))
    
    def _collapse_item(self, item_id):
        """Collapse an item to hide details"""
        if item_id not in self.expanded_items:
            return
            
        self.profitable_tree.item(item_id, values=("➕", 
                                                  self.profitable_tree.item(item_id)["values"][1],
                                                  self.profitable_tree.item(item_id)["values"][2],
                                                  self.profitable_tree.item(item_id)["values"][3]))
        
        self.profitable_tree.delete(f"{item_id}_home")
        self.profitable_tree.delete(f"{item_id}_away")
        self.profitable_tree.delete(f"{item_id}_summary")
        
        self.expanded_items.remove(item_id)

    def _on_double_click(self, _event) -> None:
        match_id = self.all_tree.focus()
        if match_id:
            self._show_detail_window(match_id)

    def _show_detail_window(self, match_id: str) -> None:
        from arbitrage.history import BettingHistory

        entry = next((e for e in BettingHistory().get_all() if e["match_id"] == match_id), None)
        if not entry or not entry.get("bookmakers"):
            messagebox.showinfo("No data", "This entry lacks bookmaker details.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Details – {match_id}")

        ttk.Label(win, text="Bookmaker odds (best price per outcome highlighted)", font=("Arial", 10, "bold")).pack()
        cols1 = ("Site", "Home", "Draw", "Away")
        raw_tree = ttk.Treeview(win, columns=cols1, show="headings", height=6)
        for c in cols1:
            raw_tree.heading(c, text=c)
            raw_tree.column(c, width=110)
        raw_tree.pack(expand=True, fill="x")

        home_best = max(b["price_home"] for b in entry["bookmakers"] if b["price_home"])
        draw_prices = [b.get("price_draw") for b in entry["bookmakers"] if b.get("price_draw")]
        draw_best = max(draw_prices) if draw_prices else None
        away_best = max(b["price_away"] for b in entry["bookmakers"] if b["price_away"])

        for b in entry["bookmakers"]:
            tag_list = []
            if b["price_home"] == home_best:
                tag_list.append("best")
            if draw_best and b.get("price_draw") == draw_best:
                tag_list.append("best")
            if b["price_away"] == away_best:
                tag_list.append("best")
            raw_tree.insert(
                "",
                "end",
                values=(
                    b["site"],
                    b["price_home"] or "-",
                    b.get("price_draw") or "-",
                    b["price_away"] or "-",
                ),
                tags=tuple(tag_list),
            )
        raw_tree.tag_configure("best", background="#dfffd6")

        ttk.Label(win, text="All bookmaker combinations", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        cols2 = ("Site H", "H", "Site D", "D", "Site A", "A", "Arb?", "Profit")

        combo_frame = ttk.Frame(win)
        combo_frame.pack(expand=True, fill="both")

        combo_tree = ttk.Treeview(combo_frame, columns=cols2, show="headings", height=12)
        for c in cols2:
            combo_tree.heading(c, text=c, command=lambda _col=c: self._treeview_sort_column(combo_tree, _col, False))
            combo_tree.column(c, width=90)

        combo_scrollbar = ttk.Scrollbar(combo_frame, orient="vertical", command=combo_tree.yview)
        combo_scrollbar.pack(side="right", fill="y")
        combo_tree.configure(yscrollcommand=combo_scrollbar.set)
        combo_tree.pack(side="left", expand=True, fill="both")

        bookmakers = entry["bookmakers"]
        bankroll = 100
        for i in bookmakers:
            for j in bookmakers:
                for k in bookmakers:
                    if not i["price_home"] or not k["price_away"]:
                        continue
                    draw_price = j.get("price_draw")
                    odds_list = [i["price_home"], k["price_away"]] if draw_price is None else [i["price_home"], draw_price, k["price_away"]]
                    arb, _ = is_arbitrage_multi(odds_list)
                    profit = calculate_stakes_multi(odds_list, bankroll)["profit"] if arb else 0.0
                    tag = "green" if arb else "red"
                    combo_tree.insert(
                        "",
                        "end",
                        values=(
                            i["site"], f"{i['price_home']:.2f}",
                            j["site"], f"{draw_price:.2f}" if draw_price else "-",
                            k["site"], f"{k['price_away']:.2f}",
                            "✅" if arb else "❌",
                            f"${profit:.2f}",
                        ),
                        tags=(tag,),
                    )
        combo_tree.tag_configure("green", foreground="green")
        combo_tree.tag_configure("red", foreground="red")

    def _treeview_sort_column(self, tree, col, reverse):
        data = [(tree.set(iid, col), iid) for iid in tree.get_children('')]
        
        if col == "Arb?":
            data.sort(reverse=reverse, key=lambda x: x[0] != "✅")
        else:
            try:
                data.sort(reverse=reverse, key=lambda x: float(x[0].replace('$', '')))
            except:
                data.sort(reverse=reverse)
        
        for index, (val, iid) in enumerate(data):
            tree.move(iid, '', index)
        
        tree.heading(col, command=lambda: self._treeview_sort_column(tree, col, not reverse))

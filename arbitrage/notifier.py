from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich import box
import time

console = Console()

def format_event_display(event, stakes, margin):
    table = Table(title=f"{event['team_a']} vs {event['team_b']}", box=box.SIMPLE_HEAD)
    table.add_column("Site")
    table.add_column("Odds")
    table.add_column("Stake")

    site_a, site_b = event["odds"].keys()
    odds_a, odds_b = event["odds"][site_a], event["odds"][site_b]

    table.add_row(site_a, str(odds_a), f"${stakes['stake_a']}")
    table.add_row(site_b, str(odds_b), f"${stakes['stake_b']}")

    profit_text = f"Guaranteed Profit: ${stakes['profit']} | Margin: {margin:.4%}"
    panel = Panel.fit(table, title=profit_text, border_style="green")

    return panel


def notify(event, stakes, margin):
    panel = format_event_display(event, stakes, margin)
    console.print(panel)

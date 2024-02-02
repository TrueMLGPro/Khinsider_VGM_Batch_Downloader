import sys

from rich.console import Group, Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, MofNCompleteColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Column

console = Console()
is_utf8 = sys.stdout.encoding == "utf-8"

FINISHED_TEXT = "[bold green]:white_check_mark:" if is_utf8 else " "
ELLIPSIS = "crop" if console.options.ascii_only else "ellipsis" # Original value: ellipsis
SEPARATOR = "[bold]•" if is_utf8 else "[bold]+"

PROGRESS_COLUMN_TASK_NAME = Column(justify="left", vertical="middle", min_width=10, max_width=32)
PROGRESS_COLUMN_SPINNER = Column(justify="left", vertical="middle", ratio=1)
PROGRESS_COLUMN_PROGRESS = Column(justify="right", vertical="middle")
PROGRESS_COLUMN_SEPARATOR = Column(justify="center", vertical="middle")
PROGRESS_COLUMN_PERCENTAGE = Column(justify="center", vertical="middle", min_width=6)

# Inner panel with progress bar for tasks
TASK_PROGRESS_BAR = Progress(
    TextColumn("{task.description}", table_column=PROGRESS_COLUMN_TASK_NAME),
    SpinnerColumn(finished_text=FINISHED_TEXT, table_column=PROGRESS_COLUMN_SPINNER),
    BarColumn(table_column=PROGRESS_COLUMN_PROGRESS),
    DownloadColumn(),
    TextColumn(SEPARATOR, table_column=PROGRESS_COLUMN_SEPARATOR),
    TransferSpeedColumn(),
    TextColumn(SEPARATOR, table_column=PROGRESS_COLUMN_SEPARATOR),
    TextColumn("[progress.percentage]{task.percentage:>3.1f}%", table_column=PROGRESS_COLUMN_PERCENTAGE),
    TextColumn(SEPARATOR, table_column=PROGRESS_COLUMN_SEPARATOR),
    TimeRemainingColumn(),
    expand=True
)

# Inner panel for overall progress
OVERALL_PROGRESS_BAR = Progress(
    TextColumn("{task.description}", table_column=PROGRESS_COLUMN_TASK_NAME),
    SpinnerColumn(finished_text=FINISHED_TEXT, table_column=PROGRESS_COLUMN_SPINNER),
    BarColumn(table_column=PROGRESS_COLUMN_PROGRESS),
    MofNCompleteColumn(),
    TextColumn(SEPARATOR, table_column=PROGRESS_COLUMN_SEPARATOR),
    TextColumn("[progress.percentage]{task.percentage:>3.1f}%", table_column=PROGRESS_COLUMN_PERCENTAGE),
    TextColumn(SEPARATOR, table_column=PROGRESS_COLUMN_SEPARATOR),
    TimeRemainingColumn(),
    expand=True
)

# Progress bar panels
TASK_INNER_PANEL_CONTENT = Panel(TASK_PROGRESS_BAR, title="Tasks", style="cyan", title_align="left")
OVERALL_INNER_PANEL_CONTENT = Panel(OVERALL_PROGRESS_BAR, title="Overall Progress", style="green", title_align="left")

# Group of inner panels
PANELS_GROUP = Group(TASK_INNER_PANEL_CONTENT, OVERALL_INNER_PANEL_CONTENT)

# Outer panel with a group of inner panels
OUTER_PANEL = Panel(PANELS_GROUP, title="Khinsider Batch Downloader", style="blue")
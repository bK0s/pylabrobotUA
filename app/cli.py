import asyncio
from os import popen
import subprocess
from sys import stderr, stdout
import textual
from textual.app import App, ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, ContentSwitcher, Header, Footer, Label, LoadingIndicator, Markdown, Placeholder, RichLog, Rule, Sparkline, Static, TabPane, TabbedContent, TextArea, Log
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from textual.screen import Screen
from textual import on
from textual.worker import Worker

import requests

from subprocess import Popen, PIPE, STDOUT

TITLE = r"""
  ___      _         _    ___     _         _
 | _ \_  _| |   __ _| |__| _ \___| |__  ___| |_
 |  _/ || | |__/ _` | '_ \   / _ \ '_ \/ _ \  _|
 |_|  \_, |____\__,_|_.__/_|_\___/_.__/\___/\__|
      |__/
"""

MARKDOWN_TAB_DEVICES= '''
# Devices

- option 1
- option 2
'''

MARKDOWN_TAB_HOME= '''
# PyLabRobot CLI
Version: 0.0.0\n
Github:\n
Developed for use with PyLabRobot software
'''

class Title(Widget):
  CSS = """
    Screen {
        align: center middle;
    }
    #title {
        background: blue 50%;
        border: wide white;
        width: auto;
    }
    """

  def compose(self) -> ComposeResult:
    yield Static(TITLE)

class ColumnsContainer(Placeholder):
  DEFAULT_CSS = """
  ColumnsContainer {
      width: 2fr;
      height: 1fr;
      border: solid white;
  }
  """

class MenuTabs(Horizontal):
  CSS = """
  ColumnsContainer {
      width: 1fr;
      height: 1fr;
      border: solid white;
  }

  #title {
      content-align: center middle;
      background: blue 50%;
      border: wide white;
      width: auto;
    }
  """
  BINDINGS = [
    ("h", "show_tab('home')", "Home"),
    ("s", "show_tab('status')", "Status"),
    ("d", "show_tab('devices')", "Devices")
  ]

  def compose(self) -> ComposeResult:
    with TabbedContent():
      with TabPane("Home", id="home"):
        # yield Title(id="title")
        yield Static(TITLE, id="title")
        yield Markdown(MARKDOWN_TAB_HOME)
        yield Rule(orientation="horizontal", line_style="double")
        with Horizontal():
          yield Button("Start Controller", id="test")
          yield Button("Clear", id="clear")
          yield Button("Ping", id="ping")
        # yield Log(id="log")
        yield Rule(orientation="horizontal", line_style="double")
        yield RichLog(id="log", highlight=True)
      with TabPane("Status", id="status"):
        yield Markdown("# Status")
      with TabPane("Devices", id="devices"):
        yield Markdown(MARKDOWN_TAB_DEVICES)
      with TabPane("Settings", id="settings"):
        yield Markdown("# Settings")

  def action_show_tab(self, tab: str) -> None:
      """Switch to a new tab."""
      self.get_child_by_type(TabbedContent).active = tab

  async def _start_controller(self) -> None:
    log = self.query_one("#log", RichLog)
    self.notify("Starting Controller...")
    log.write("*" * 5 + " Launching controller " + "*" * 5 + "\n")
    proc = await asyncio.create_subprocess_shell("python3 pylabrobot/app/tecan_controller.py", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    log.write("=" * 20 + f"\n[Tecan Robot] {stdout.decode()}\n" + "="*20 )
    if stderr:
      log.write(f"ERROR: {stderr.decode()}")
    # for line in stdout.decode():
      # log.write_line(f"[Tecan Robot] {line}")

  @on(Button.Pressed, "#test")
  async def start_controller(self, event: Button.Pressed) -> None:
    output = self.query_one("#log", RichLog)
    output.write("Starting Worker\n")

    # proc = asyncio.create_subprocess_shell("python3 pylabrobot/app/tecan_controller.py", stdout=asyncio.subprocess.PIPE)
    self.run_worker(self._start_controller())



  @on(Button.Pressed, "#ping")
  async def ping(self, event:Button.Pressed) -> None:
    response = requests.get("http://127.0.0.1:5000/ping")
    self.query_one("#log", RichLog).write(f"Status: {response.status_code} \nData: {response.text}\n")

  @on(Button.Pressed, "#clear")
  def clear_log(self, event: Button.Pressed) -> None:
    output = self.query_one("#log", RichLog)
    output.clear()

class MainContent(Widget):
  DEFAULT_CSS = """
  MainContent {
      width: 2fr;
      height: 1fr;
      border: solid white;
  }
  """
  def compose(self) -> ComposeResult:
    with ContentSwitcher(initial="loading"):
      # yield Markdown("Home", id="home")
      yield LoadingIndicator(id="loading")

class MainScreen(Screen):
  def compose(self) -> ComposeResult:
    yield Header(id="Header")
    yield Footer(id="Footer")
      # yield ColumnsContainer(id="Columns1")
    with Horizontal():
      yield MenuTabs(id="main_menu").focus()
      yield MainContent()
      # yield ColumnsContainer(id="Columns2")
    # yield Label("Log")
    # yield Log(id="log")
  def on_mount(self) -> None:
    self.title = "Pylabrobot"


class CLI(App):
  def on_mount(self) -> None:
    self.push_screen(MainScreen())


if __name__ == '__main__':
  cli = CLI()
  cli.run()

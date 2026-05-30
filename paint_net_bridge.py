import subprocess
import time
from io import BytesIO
import pyautogui
import win32gui
import win32clipboard
import win32con
from PIL import Image
from pathlib import Path

PAINTNET_PATH = r"C:\Program Files\Paint.NET\paintdotnet.exe"
PDN_CLASS = "PaintDotNet.ui.AppShell"


class PaintNetBridge:
    def __init__(self, ref_path):
        self.ref_path = Path(ref_path).resolve()
        self._hwnd = None
        self._overlay_pasted = False

    def find_paintnet(self):
        self._hwnd = None
        def enum_callback(hwnd, _):
            if PDN_CLASS in win32gui.GetClassName(hwnd) and win32gui.IsWindowVisible(hwnd):
                self._hwnd = hwnd
                return False
            return True
        win32gui.EnumWindows(enum_callback, None)
        return self._hwnd is not None

    def activate(self):
        if not self.find_paintnet():
            return False
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self._hwnd)
            time.sleep(0.3)
            return True
        except Exception:
            return False

    def _copy_to_clipboard(self, img):
        img_rgba = img.convert("RGBA")
        bmp_data = BytesIO()
        img_rgba.convert("RGB").save(bmp_data, format="BMP")
        bmp_bytes = bmp_data.getvalue()[14:]
        bmp_data.close()
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_bytes)
        finally:
            win32clipboard.CloseClipboard()

    def open_in_paintnet(self, img, name="output"):
        path = self.ref_path.parent / f"{name}.png"
        img.save(str(path))
        subprocess.Popen([PAINTNET_PATH, str(path)])
        time.sleep(2)

    def open_reference(self):
        subprocess.Popen([PAINTNET_PATH, str(self.ref_path)])
        time.sleep(2)
        self.find_paintnet()

    def _select_overlay_layer(self):
        left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
        w = right - left
        h = bottom - top

        layers_x = left + int(w * 0.87)
        layers_y = top + int(h * 0.67)

        win32gui.SetForegroundWindow(self._hwnd)
        time.sleep(0.15)
        pyautogui.click(layers_x, layers_y)
        time.sleep(0.2)

    def update_overlay(self, overlay_img):
        self._copy_to_clipboard(overlay_img)

        if not self.activate():
            print("  Could not find Paint.NET window")
            return

        if not self._overlay_pasted:
            pyautogui.hotkey("ctrl", "shift", "v")
            time.sleep(0.4)
            self._overlay_pasted = True
            return

        try:
            self._select_overlay_layer()
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.15)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.15)
            pyautogui.press("enter")
            time.sleep(0.2)
        except Exception as e:
            print(f"  Layer replacement failed, pasting new layer: {e}")
            pyautogui.hotkey("ctrl", "shift", "v")
            time.sleep(0.4)

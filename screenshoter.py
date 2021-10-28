from ctypes import windll

import win32ui
import win32gui
from PIL import Image
# from win32 import win32gui


def make_scrsht(window_name):
    hwnd = win32gui.FindWindow(None, window_name)

    # Change the line below depending on whether you want the whole window
    # or just the client area. 
    # left, top, right, bot = win32gui.GetClientRect(hwnd)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    save_bit_map = win32ui.CreateBitmap()
    save_bit_map.CreateCompatibleBitmap(mfc_dc, w, h)

    save_dc.SelectObject(save_bit_map)

    # Change the line below depending on whether you want the whole window
    # or just the client area. 
    # result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)
    result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)
    # print(result)

    bmpinfo = save_bit_map.GetInfo()
    bmpstr = save_bit_map.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(save_bit_map.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result == 1:
        # PrintWindow Succeeded
        im.save(f"{window_name}.png")

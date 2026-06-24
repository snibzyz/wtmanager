"""CustomTkinter UI for WTManager (replacement for the Flet GUI).

ใช้ Tkinter/CustomTkinter ซึ่งติดมากับตัวติดตั้ง Python มาตรฐาน
→ ไม่ต้องโหลด engine ตอนรัน ไม่มี SSL ไม่มี API พังข้ามเวอร์ชันแบบ Flet.
Logic (collectors/config/workspace/paths) ใช้ของเดิมทั้งหมด ไม่แตะ.
"""

from app.gui_ctk.app import run

__all__ = ["run"]

# WTManager

Workspace collector สำหรับรวบรวมและจัดการไฟล์โปรเจกต์แปลมังงะ  
เลือกเรื่อง → เลือกฟังก์ชัน → กด Execute — ไฟล์จัดเรียบร้อยในทีเดียว

---

## ความต้องการ

- **Python 3.10+** (ตอนติดตั้ง แนะนำติ๊ก **Add to PATH** และ **tcl/tk and IDLE**)
- **Git** (สำหรับ clone + auto-update)
- แพ็กเกจใน `requirements.txt`: **CustomTkinter**, **Pillow**

> UI อยู่บน **Tkinter** ที่ติดมากับตัวติดตั้ง Python อยู่แล้ว → ไม่ต้องดาวน์โหลด
> engine ตอนรัน ไม่มีปัญหา SSL/เน็ต และทำงานได้เหมือนกันทุกเครื่อง

---

## การติดตั้ง

ทุกวิธีต้องมี [Python 3.10+](https://www.python.org/downloads/) ก่อน — ตอนติดตั้งติ๊ก **Add python.exe to PATH** และ **tcl/tk and IDLE**

จากนั้นเลือกวิธีใดวิธีหนึ่ง:

### วิธีที่ 1 — Git clone (แนะนำ ✅ มี auto-update)

ได้โค้ดตรงรีโปและอัปเดตเองทุกครั้งที่เปิด ต้องมี [Git for Windows](https://git-scm.com/download/win) ก่อน

```text
git clone https://github.com/snibzyz/wtmanager.git
cd wtmanager
```

แล้วดับเบิลคลิก **`install.bat`** → เปิดด้วย **`run.bat`**

### วิธีที่ 2 — ดาวน์โหลดจาก Release (ไม่ต้องมี Git)

1. เปิด **[หน้า Releases ล่าสุด](https://github.com/snibzyz/wtmanager/releases/latest)**
2. ใต้หัวข้อ **Assets** กด **Source code (zip)** เพื่อดาวน์โหลด
3. แตก ZIP แล้วเข้าโฟลเดอร์ที่ได้
4. ดับเบิลคลิก **`install.bat`** → เปิดด้วย **`run.bat`**

> ⚠️ วิธีนี้ **ไม่มี auto-update** (ไม่มี `.git`) — มีเวอร์ชันใหม่ต้องโหลด ZIP ใหม่เอง หรือเปลี่ยนไปใช้วิธีที่ 1

### วิธีที่ 3 — ดาวน์โหลดโค้ดล่าสุด (ZIP)

ที่หน้า repo กดปุ่มเขียว **`< > Code` → Download ZIP** (ได้โค้ดล่าสุดบนสาขา `master`) แล้วทำเหมือนวิธีที่ 2 ข้อ 3–4

> ⚠️ เหมือนวิธีที่ 2 คือ **ไม่มี auto-update**

ถ้า `install.bat` จบด้วยข้อความ **\[ตรวจสอบ\] พร้อมใช้งาน** แปลว่าติดตั้งสมบูรณ์แล้ว

**หมายเหตุ Windows:** ไฟล์ `*.bat` ที่รากโปรเจกต์ใช้เฉพาะตัวอักษร ASCII และเข้ารหัส UTF-8 พร้อม BOM เพื่อไม่ให้ `cmd.exe` ตีความบรรทัดผิด (อาการ `'...' is not recognized`) เมื่อระบบใช้ code page อื่น ข้อความภาษาไทยอยู่ใน `scripts/*.py`

---

## ติดตั้งซ้ำ (เมื่อมีโฟลเดอร์โปรเจกต์อยู่แล้ว)

ดับเบิลคลิก `install.bat` หรือรัน:

```text
python scripts\install.py
```

---

## เปิดใช้งาน

ดับเบิลคลิก `run.bat` หรือรัน:

```text
python scripts\run.py
```

## อัปเดต

**ถ้าติดตั้งด้วยวิธีที่ 1 (git clone):**
- **Auto-update:** ทุกครั้งที่เปิดโปรแกรม (`run.bat`) จะ `git pull --ff-only` ให้ก่อน — ถ้าไม่มีเน็ต / ไม่มี git / pull ไม่สำเร็จ ก็ข้ามไปเปิดแอปได้ ไม่ค้าง
- อัปเดตเองด้วยมือ: ดับเบิลคลิก **`update.bat`** (จะ `git pull --ff-only` แล้วรัน `scripts\install.py` ซ้ำ)

**ถ้าติดตั้งด้วยวิธีที่ 2/3 (ZIP):** ไม่มี auto-update — เวลามีเวอร์ชันใหม่ให้โหลด ZIP ใหม่จาก [หน้า Releases](https://github.com/snibzyz/wtmanager/releases/latest) แล้วแตกทับ (config เดิมอยู่ในโฟลเดอร์ที่ติดตั้ง ไม่หาย ถ้าแตกคนละที่ให้ก๊อป `app/config/config.json` ตามไป)

---

## วิธีใช้งาน

1. กดปุ่ม **📁 เลือก Workspace** — ชี้ไปที่โฟลเดอร์หลักที่มีเรื่องทั้งหมด
2. เลือก **เรื่อง** ที่ต้องการ (เลือกได้หลายเรื่อง) จาก panel ซ้าย
3. เลือก **ฟังก์ชัน** ที่ต้องการจาก panel ขวา
4. ตั้งค่าเพิ่มเติม (เครดิต / compress / หั่นภาพ) ถ้าจำเป็น
5. กด **Execute** — ดูความคืบหน้าใน log panel

---

## ฟังก์ชัน

| ฟังก์ชัน | ชื่อ | หน้าที่ |
|----------|------|---------|
| `raw` | ดึงไฟล์ดิบ | copy ภาพต้นฉบับจาก root ของแต่ละตอน (`01.jpg`, `02.jpg`, ...) |
| `inp` | ดึงไฟล์คลีน | copy ภาพจากโฟลเดอร์ `inpainted/` |
| `res` | ดึงไฟล์ลงคำ | copy ภาพจากโฟลเดอร์ `result/` |
| `trans` | ดึงไฟล์แปล | copy ไฟล์ `*_translation.txt` |
| `text` | ดึงไฟล์ถอดคำ | copy ไฟล์ `imgtrans_*.json` และ `*_source.txt` |
| `ep` | แยกเป็น episode | จัดไฟล์ trans/text แยกตามตอน |
| `split` | หั่นภาพ | ตัดภาพแนวนอนเป็น N ชิ้น (ต้องเลือก res) |
| `cred` | เพิ่มเครดิต | copy ภาพเครดิตใส่ท้ายทุกตอน (เลือกได้หลายไฟล์) |
| `com` | ย่อไฟล์ | compress ภาพ JPG/PNG (ต้องเลือก res) |

### กฎการเลือก

- **raw / inp / res** เลือกอิสระแยกกันได้ทุกอัน (จะเลือกพร้อมกันกี่อย่างก็ได้)
- **split** และ **com** ต้องเลือก `res` ก่อน (ทำงานบนไฟล์ผลลัพธ์)
- **ep** ต้องเลือก `trans` หรือ `text` ก่อน

### ชื่อโฟลเดอร์ output

สร้างอัตโนมัติจากฟังก์ชันที่เลือก เรียงตามลำดับ:

```
raw > inp > res > trans > text > ep > split > cred > com
```

ตัวอย่าง:

| เลือก | output folder |
|-------|---------------|
| raw + inp | `raw_inp/` |
| res + cred + com | `res_cred_com/` |
| res + trans + text + ep | `res_trans_text_ep/` |
| res + split + cred | `res_split_cred/` |

---

## ตั้งค่า

### ไฟล์เครดิต (`cred`)
- เลือกได้ **หลายไฟล์** — กดปุ่ม ➕ เพื่อเพิ่ม, กด ✕ เพื่อลบทีละไฟล์
- ถ้าเลือก **1 ไฟล์** → ตั้งชื่อ `9999credit.png`
- ถ้าเลือก **หลายไฟล์** → ตั้งชื่อ `9999credit_01.png`, `9999credit_02.png`, ...
- ค่า default: `../logo/9999credit.png` (โฟลเดอร์ข้างๆ โปรเจกต์)

### Compress (`com`)
- รูปแบบ: **JPG** หรือ **PNG**
- คุณภาพ: 1–100 (default 70)

### หั่นภาพ (`split`)
- ระบุจำนวนชิ้น 2–20 (default 2)
- หั่นแนวนอน บนลงล่าง

---

## โครงสร้าง workspace ที่รองรับ

```
D:\Projects\manga-translate\          <- workspace (เลือกโฟลเดอร์นี้)
├── My Story 001\                     <- เรื่อง (story)
│   ├── 0\                            <- ตอน (episode)
│   │   ├── 01.jpg                    <- raw
│   │   ├── 02.jpg
│   │   ├── imgtrans_0.json           <- text
│   │   ├── imgtrans_0_source.txt
│   │   ├── imgtrans_0_translation.txt  <- trans
│   │   ├── inpainted\                <- inp
│   │   │   ├── 01.png
│   │   │   └── 02.png
│   │   └── result\                   <- res
│   │       ├── 01.png
│   │       └── 02.png
│   ├── 1\
│   ├── 2\
│   └── ...
├── My Story 002\
└── ...
```

Output จะถูกสร้างใน:

```
D:\Projects\manga-translate\My Story 001\res_cred_com\
├── 0\
│   ├── 01.jpg
│   ├── 02.jpg
│   └── 9999credit.png
├── 1\
└── ...
```

---

## โครงสร้างโปรเจกต์

```
WTManager/
├── install.bat               # ติดตั้ง (เรียก scripts\install.py)
├── run.bat                   # เปิดแอป (เรียก scripts\run.py, มี auto-update)
├── update.bat                # git pull + ติดตั้งซ้ำ
├── requirements.txt          # customtkinter, Pillow
├── .gitignore
├── scripts/
│   ├── install.py            # pip + ทดสอบโหลด UI (offline)
│   ├── run.py                # entry: auto-update (git pull) + เปิด GUI
│   └── _find_python.bat      # เลือก py -3 / python
├── app/
│   ├── __init__.py           # __version__
│   ├── paths.py              # normalize path ให้ทุกเครื่องอ่านตรงกัน
│   ├── config/               # บันทึก/โหลด settings (config.json)
│   ├── workspace/            # จัดการ workspace path
│   ├── collectors/           # แต่ละไฟล์ = 1 หน้าที่ (raw, inpainted, res,
│   │                         #   trans, text, split, credit, compress)
│   └── gui_ctk/              # UI (CustomTkinter)
│       ├── app.py            # หน้าหลัก + execute (thread + queue)
│       ├── theme.py          # สี + ฟอนต์
│       ├── widgets.py        # การ์ด + หัวข้อ section
│       ├── icons.py          # ไอคอน Segoe MDL2 Assets
│       └── constants.py      # FUNC_ORDER, FUNC_LABELS, build_folder_name
└── .old/                     # UI เดิม (Flet) เก็บไว้อ้างอิง — ไม่ใช้แล้ว
```

---

## Config ที่บันทึกอัตโนมัติ

ไฟล์ `app/config/config.json` (ไม่ถูก commit ขึ้น git):

| Key | ประเภท | คำอธิบาย |
|-----|--------|-----------|
| `last_workspace` | string | path workspace ล่าสุด |
| `selected_functions` | list | ฟังก์ชันที่เลือกไว้ |
| `credit_paths` | list | รายการไฟล์เครดิต |
| `compress_format` | string | `jpg` หรือ `png` |
| `compress_quality` | int | คุณภาพ compress 1–100 |
| `split_parts` | int | จำนวนชิ้นต่อภาพเมื่อใช้ split (2–20, default 2) |

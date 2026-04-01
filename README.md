# WTManager

Workspace collector สำหรับรวบรวมและจัดการไฟล์โปรเจกต์แปลมังงะ  
เลือกเรื่อง → เลือกฟังก์ชัน → กด Execute — ไฟล์จัดเรียบร้อยในทีเดียว

---

## ความต้องการ

- **Python 3.10+**
- **Flet** >= 0.24.0 (GUI framework)
- **Pillow** >= 10.0.0 (compress ภาพ)

---

## ติดตั้ง

ดับเบิลคลิก `install.bat` หรือรันคำสั่ง:

```
python install.py
```

---

## เปิดใช้งาน

ดับเบิลคลิก `run.bat` หรือรันคำสั่ง:

```
python run.py
```

> **Auto-update:** ทุกครั้งที่เปิดโปรแกรม จะดึงอัปเดตล่าสุดจาก GitHub อัตโนมัติ (`git pull`)  
> ถ้าไม่มีเน็ตหรือ git ไม่ถูก install — ข้ามไปเปิดแอปตามปกติ ไม่ค้าง

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

- **raw** กับ **res** เลือกได้อย่างใดอย่างหนึ่ง (mutually exclusive)
- **inp** ต้องเลือก `raw` ก่อน
- **split** และ **com** ต้องเลือก `res` ก่อน
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
├── run.bat / run.py          # เปิดแอป (มี auto-update)
├── install.bat / install.py  # ติดตั้ง dependencies
├── requirements.txt
├── .gitignore
├── app/
│   ├── config/               # บันทึก/โหลด settings (config.json)
│   │   └── manager.py
│   ├── theme/                # สี, gradient, widget helpers
│   │   ├── colors.py
│   │   └── widgets.py
│   ├── workspace/            # จัดการ workspace path
│   │   └── manager.py
│   ├── collectors/           # แต่ละไฟล์ = 1 หน้าที่
│   │   ├── raw.py
│   │   ├── inpainted.py
│   │   ├── res.py
│   │   ├── trans.py
│   │   ├── text.py
│   │   ├── split.py
│   │   ├── credit.py         # post-process: เพิ่มเครดิต (รองรับหลายไฟล์)
│   │   └── compress.py       # post-process: compress ภาพ
│   └── gui/                  # UI components
│       ├── main.py           # ประกอบหน้าหลัก
│       ├── constants.py      # FUNC_ORDER, FUNC_LABELS, build_folder_name
│       ├── styles.py         # chip styles
│       ├── header.py
│       ├── left_panel.py     # เลือก workspace + เรื่อง
│       └── right_panel.py    # ฟังก์ชัน, ตั้งค่า, execute, log
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

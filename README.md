# 🕵️‍♂️ Reverse IP Domain Extractor

Extract domains hosted on the same IP using [reverseipdomain.com](https://reverseipdomain.com).  
This tool is useful for reconnaissance during penetration testing or OSINT investigations.

---

## ✨ Features

- Multithreaded IP scanning
- Parses and extracts domains from reverseipdomain.com
- Filters out unwanted file types and static asset domains
- Skips IPs with less than 3 valid domains
- Saves unique domains to `domains.txt`
- Colorful and informative terminal output

---

## 📸 Screenshot

```
![Screenshot](https://raw.githubusercontent.com/mrTr1cky/reverseip/refs/heads/main/revip.png)
```

---

## 🛠️ Requirements

- Python 3.x
- Modules:
  - `requests`
  - `colorama`

You can install dependencies using:

```bash
pip install requests
pip install colorama
```

---

## 📦 Installation

```bash
git clone https://github.com/mrTr1cky/reverseip.git
cd reverseip
```

Create a file `ips.txt` with one IP per line.

Example:
```
8.8.8.8
1.1.1.1
```

---

## 🚀 Usage

```bash
python reverse-ip.py
```

- Enter the path to your IP list (e.g., `ips.txt`)
- Choose the number of threads (e.g., `10`)

---

## 📄 Output

- Extracted domains are saved to: `domains.txt`
- IPs with fewer than 2 valid domains are **skipped**
- Shows total number of unique domains and skipped IPs at the end

---

## ⚠️ Notes

- Be respectful to `reverseipdomain.com`, do not abuse the service.
- This tool is intended for **educational and ethical use only**.
- If the site changes structure, you may need to update the parsing logic.

---

## 🧑‍💻 Author

**mrTr1cky**  
https://github.com/mrTr1cky

---

## 📜 License

This project is licensed under the No Licence

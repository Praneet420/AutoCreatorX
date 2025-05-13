
# 🛡️ AutoCreatorX Troubleshooting Guide

Commander Quick-Reference Manual

---

## ❓ Common Problems and Instant Solutions

---

### 1. ffmpeg not found

**Problem:** Video generation crashes with ffmpeg errors.

**Solution:**Install ffmpeg:

- Windows: `choco install ffmpeg`
- Linux/Mac: `sudo apt install ffmpeg`

---

### 2. ChromeDriver missing

**Problem:** TikTok or Instagram uploader crashes.

**Solution:**
Download ChromeDriver matching your Chrome browser version:
https://chromedriver.chromium.org/downloads

Add it to your system PATH.

---

### 3. GPU Crashes

**Problem:** Media Producer overloads during rendering.

**Solution:**

- Lower rendering resolution from 1080p to 720p.
- Use the Cloaking Mode (auto_cloaker.py) to reduce load.
- Monitor via Streamlit dashboard system stats.

---

### 4. API Rate Limits Hit

**Problem:** Trend analysis modules suddenly slow or error out.

**Solution:**

- Check API usage limits.
- Enable Dynamic API Key Rotator (only if 3+ valid keys present).
- Reduce scan frequency in config/settings.py.

---

### 5. RAM Overflow

**Problem:** AutoCreatorX freezes due to high RAM consumption.

**Solution:**

- Emergency fallback triggers automatically.
- Manual override: Stop heavy modules via Dashboard.
- Add swap space or upgrade physical RAM if persistent.

---

## 🛠️ Recovery Playbook

- Always check Dashboard alerts.
- Always monitor CPU/RAM during operations.
- Emergency Pause button available on Dashboard.
- Watchman AI automatically defends in case of non-response.

---

# 📜 Reminder:

> Commander is always in control. Empire will always notify before critical actions.

---

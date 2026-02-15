# 🔍 Monitoring Training - Quick Guide

## ✅ Training Status: **RUNNING** 🔥

**Process ID:** 46952  
**Runtime:** 7 minutes  
**CPU:** 1.6%  
**Memory:** 0.3%  

**Status:** Currently downloading model files and initializing

---

## 📊 Cara Monitoring

### **1. Quick Check (Run Anytime)**

```bash
cd python_backend
./monitor_training.sh
```

Output akan show:
- ✅ Training status (running/stopped)
- 📊 CPU & Memory usage
- ⏱️ Runtime
- 💾 Checkpoint count
- 📝 Latest log entries

---

### **2. Auto-Refresh Monitor (Recommended)**

```bash
# Auto-refresh setiap 10 detik
watch -n 10 'cd python_backend && ./monitor_training.sh'
```

Tekan `Ctrl+C` untuk stop monitoring.

---

### **3. Live Log Streaming**

```bash
# Wait sampai training mulai (5-10 min), lalu:
tail -f python_backend/finetune/output/indonesian_xtts_m2/run/training/*/train.log
```

Ini akan show real-time training progress:
```
Epoch 1/10 - Step 50/500 - Loss: 0.234
Epoch 1/10 - Step 100/500 - Loss: 0.198
...
```

---

### **4. Check Terminal Output**

Terminal yang running `./run_finetuning_m2.sh` akan show progress langsung. Jangan close terminal itu!

---

## ⏰ Timeline

**Sekarang (07:08):** Downloading models (~10 min)  
**~07:15:** Training mulai (Epoch 1)  
**~13:00-15:00:** Training selesai ✅

---

## 🎯 Commands Cheat Sheet

```bash
# Quick status check
cd python_backend && ./monitor_training.sh

# Auto-refresh monitor
watch -n 10 'cd python_backend && ./monitor_training.sh'

# Live logs
tail -f python_backend/finetune/output/indonesian_xtts_m2/run/training/*/train.log

# Check if running
ps aux | grep train_standalone.py

# Resource usage
top -pid $(pgrep -f train_standalone.py)
```

---

## 💡 What to Expect

**Phase 1 (Now):** Downloading DVAE + XTTS models  
**Phase 2 (~07:15):** Training starts - Epoch 1  
**Phase 3 (~08:00):** Epoch 2-10 running  
**Phase 4 (~13:00):** Training complete! 🎉

---

## 🚨 Troubleshooting

**Kalau training stop:**
```bash
cd python_backend
./run_finetuning_m2.sh
```

**Kalau stuck (no progress >30 min):**
1. Check terminal output
2. Check log file
3. Restart training

---

**Bottom Line:** Pakai `./monitor_training.sh` untuk quick check, atau `watch -n 10` untuk auto-refresh! 📊

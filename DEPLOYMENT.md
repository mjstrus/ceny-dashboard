# 🚀 Deployment Guide: GitHub + Streamlit Cloud

## Etap 1: Przygotowanie Lokalnie

### 1.1 Otwórz terminal

```bash
cd ceny-dashboard
```

### 1.2 Inicjalizuj Git repo

```bash
git init
git config user.name "Marcin Strus"
git config user.email "twoj.email@gmail.com"
```

### 1.3 Dodaj pliki

```bash
git add .
git status  # sprawdź co będzie dodane
```

### 1.4 Pierwszy commit

```bash
git commit -m "Initial commit: Ceny Dashboard v1.0 - Units 1-6 complete"
```

---

## Etap 2: Przygotowanie GitHub

### 2.1 Utwórz nowy repo na GitHub

1. Wejdź na https://github.com/new
2. **Repository name:** `ceny-dashboard`
3. **Description:** "Streamlit dashboard do ujednolicenia cen — Abacus Centrum"
4. **Public** (żeby Streamlit Cloud mógł dostać)
5. **Nie inicjalizuj** z README/gitignore (już mamy lokalnie)
6. Kliknij **"Create repository"**

### 2.2 Dodaj remote i wyślij kod

```bash
# Zamień mjstrus na Twoją username
git remote add origin https://github.com/mjstrus/ceny-dashboard.git

# Zmień branch na main (Streamlit Cloud prefers main)
git branch -M main

# Wyślij kod
git push -u origin main
```

**Output powinien być:**
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to 8 threads
To https://github.com/mjstrus/ceny-dashboard.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ **Kod na GitHub!**

---

## Etap 3: Deploy na Streamlit Cloud

### 3.1 Wejdź na Streamlit Cloud

1. Otwórz https://streamlit.io/cloud
2. Zaloguj się z GitHub account
3. Kliknij **"New app"**

### 3.2 Utwórz app

W formularzu:
- **Repository:** `mjstrus/ceny-dashboard`
- **Branch:** `main`
- **Main file path:** `streamlit_app.py`

Kliknij **"Deploy!"**

### 3.3 Czekaj na build

- Streamlit Cloud pobiera repo z GitHub
- Instaluje zależności (requirements.txt)
- Buduje i deployuje
- Powinno trwać ~2-3 minuty

**URL Twojego app:**
```
https://share.streamlit.io/mjstrus/ceny-dashboard/main/streamlit_app.py
```

✅ **App live!**

---

## Etap 4: Testowanie

### 4.1 Otwórz app

Kliknij w URL powyżej

### 4.2 Testuj z sample data

1. Wybierz: "📂 Użyj przykładowych danych (dev)"
2. Zmień ceny (Unit 2)
3. Przejrzyj wykresy (Unit 5)
4. Exportuj raport (Unit 6)

### 4.3 Jeśli error

- Sprawdź logs w Streamlit Cloud dashboard
- Najczęstszy problem: brakujące dependency w requirements.txt
- Fix: `pip install X` lokalnie → dodaj do requirements.txt → `git push`
- Streamlit Cloud auto-redeploy

---

## Etap 5: Continuous Deployment

Od teraz każdy `git push` → auto-deploy na Streamlit Cloud

```bash
# Edytuj plik lokalnie
nano streamlit_app.py

# Commit
git add streamlit_app.py
git commit -m "Fix: Unit 3 calculation"

# Push
git push origin main
```

Streamlit Cloud zauważy zmianę i auto-redeploy (1-2 minuty)

---

## 🔧 Troubleshooting

### App nie deployuje / Error

**Check 1: requirements.txt**
```bash
# Upewnij się że wszystkie libraries są tam
grep streamlit requirements.txt
grep pandas requirements.txt
grep plotly requirements.txt
```

**Check 2: Python syntax**
```bash
# Uruchom lokalnie
streamlit run streamlit_app.py
# Jeśli działa lokalnie, problem może być w Streamlit Cloud
```

**Check 3: Logs w Streamlit Cloud**
- Wejdź w dashboard
- Kliknij "Logs"
- Szukaj errora

### Sample data nie ładuje

**Problem:** `sample_data/master_clients_sample.xlsx` nie znalezione
**Solution:** Upewnij się że plik jest w repo
```bash
git ls-files | grep sample_data
# Powinno być: sample_data/master_clients_sample.xlsx
```

### Streamlit Cloud mówi "403 Permission Denied"

**Problem:** Repo jest private
**Solution:** Zmień na public (GitHub Settings → Danger Zone → Make Public)

---

## 📝 Checklist

- [ ] Git init + first commit lokalnie
- [ ] Repo created na GitHub
- [ ] `git push origin main` udane
- [ ] Streamlit Cloud app created
- [ ] App loading bez errora
- [ ] Sample data ładuje
- [ ] Ceny input działa
- [ ] Wykresy renderują
- [ ] Export button działa
- [ ] URL shared z teamem

---

## 🎉 Done!

App jest live i ready do użytku:
```
https://share.streamlit.io/mjstrus/ceny-dashboard/main/streamlit_app.py
```

**Następne kroki:**
1. Testuj z sample data
2. Gdy Marcin da real Excel → zmień upload na real data
3. Fine-tune ceny jeśli potrzeba
4. Exportuj raport i wdrażaj

---

**Support:** Jeśli error, check Streamlit Cloud logs lub kontakt z Marcinem

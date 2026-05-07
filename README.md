# 💰 Ceny Dashboard — Abacus Centrum

Streamlit dashboard do ujednolicenia cen dla ~200 klientów Abacus Centrum.

## 📋 Funkcjonalność

- **Unit 1:** Wczytanie danych historycznych (stare ceny + liczba dokumentów)
- **Unit 2:** Input nowych cen dla 6 typów umów (Kh/KPIR/Ryczałt × z VAT/bez VAT)
- **Unit 3:** Kalkulacja wpływu ceny (stara vs nowa przychód)
- **Unit 4:** Risk Assessment & Segmentacja (Zielony/Żółty/Czerwony)
- **Unit 5:** Wizualizacja & Tabele
- **Unit 6:** Export & Raportowanie (Excel/CSV)

## 🚀 Deployment

### GitHub Setup (Local)

```bash
# 1. Inicjalizuj Git repo
cd ceny-dashboard
git init

# 2. Dodaj pliki
git add .

# 3. Pierwszy commit
git commit -m "Initial commit: Ceny Dashboard v1.0 (Units 1-6)"

# 4. Dodaj remote (zmień mjstrus na Twoją username)
git remote add origin https://github.com/mjstrus/ceny-dashboard.git

# 5. Wyślij na GitHub
git branch -M main
git push -u origin main
```

### Streamlit Cloud (Deployment)

1. **Wejdź na** https://streamlit.io/cloud
2. **Zaloguj się** z GitHub account
3. **Kliknij** "New app" → "From existing repo"
4. **Wybierz:**
   - **Repository:** mjstrus/ceny-dashboard
   - **Branch:** main
   - **Main file path:** streamlit_app.py
5. **Deploy!** — Streamlit Cloud auto-buduje i deployuje
6. **URL:** https://share.streamlit.io/mjstrus/ceny-dashboard/main/streamlit_app.py

### Continuous Deployment

- Po każdym `git push` na GitHub, Streamlit Cloud auto-redeploy
- Logs: dostępne w Streamlit Cloud dashboard
- Monitoring: check status w https://streamlit.io/cloud

---

## 📊 Usage (Live App)

1. Otwórz: https://share.streamlit.io/mjstrus/ceny-dashboard/main/streamlit_app.py
2. Wybierz: "Użyj przykładowych danych (dev)" lub wczytaj swój Excel
3. Ustaw nowe ceny (6 pól)
4. Przejrzyj analizę (wykresy, tabele)
5. Exportuj raport (Excel, CSV, Markdown)

## 📊 Format Danych Wejściowych

Excel `master_clients_sample.xlsx` powinien zawierać arkusz `Clients` z kolumnami:

| Kolumna | Typ | Przykład |
|---------|-----|---------|
| ID | int | 1 |
| Nazwa | str | Acme Ltd |
| Typ_Umowy | str | Kh, KPIR, Ryczałt |
| VAT | str | z VAT, bez VAT |
| Cena_Bazowa | float | 450 |
| Doc_Marzec | int | 10 |
| Doc_Kwiecien | int | 12 |
| Doc_Maj | int | 11 |
| Czy_Rabat | int | 1 (tak), 0 (nie) |
| Data_Umowy | str | 2023-01-15 |

## 🏗️ Struktura Projektu

```
ceny-dashboard/
├── streamlit_app.py          # Main entry point
├── data_loader.py            # Unit 1: Data Input & Parsing
├── price_config.py           # Unit 2: New Price Config (TBD)
├── calculator.py             # Unit 3: Price Impact Calculation (TBD)
├── risk_assessment.py        # Unit 4: Risk Assessment (TBD)
├── visualizations.py         # Unit 5: Viz & Tables (TBD)
├── exporter.py               # Unit 6: Export & Reporting (TBD)
├── requirements.txt          # Python dependencies
├── sample_data/
│   └── master_clients_sample.xlsx  # Example data (5 clients)
└── README.md                 # This file
```

## 🔄 Implementation Status

- [x] Unit 1: Data Input & Parsing ✓
- [x] Unit 2: New Prices Input ✓
- [ ] Unit 3: Price Impact Calculation
- [ ] Unit 4: Risk Assessment & Segmentation
- [ ] Unit 5: Visualizations & Tables
- [ ] Unit 6: Export & Reporting

## 📝 Planowanie

Pełny plan techniczny: `docs/plans/2026-05-06-001-streamlit-ceny-dashboard-plan.md`

## 🤝 Contribute

1. Fork repo
2. Utwórz branch (`git checkout -b feature/X`)
3. Commit zmiany
4. Push do branch (`git push origin feature/X`)
5. Otwórz Pull Request

## 📞 Support

Kontakt: Marcin (@mjstrus)

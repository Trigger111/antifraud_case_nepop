# Genesis Case #3 — Marketing Anti-Fraud

Фінальний аналітичний кейс від TENTENS Tech: пошук marketing fraud у партнерському трафіку, оцінка бізнес-впливу та правила реагування.

## Що є в репозиторії

| Файл | Призначення |
|---|---|
| `case3_antifraud.ipynb` | Повний відтворюваний аналіз на Python + DuckDB |
| `TenTens_antifraud_management_brief.pptx` | Коротка презентація результатів для менеджменту |
| `TenTens_antifraud_dashboard.pbix` | Інтерактивний Power BI dashboard |
| `powerbi_data/` | Готові невеликі вітрини для Power BI |
| `scripts/download_data.py` | Автоматичне завантаження Parquet із GitHub Release |

## Найшвидший запуск на Windows

Після клонування репозиторію запустіть:

```bat
setup_and_run.bat
```

Скрипт автоматично:

1. створить `.venv`;
2. встановить зафіксовані версії бібліотек;
3. завантажить і перевірить чотири Parquet-файли;
4. відкриє ноутбук у JupyterLab.

Після відкриття оберіть **Run → Run All Cells**.

## Ручний запуск

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\download_data.py
.\.venv\Scripts\python.exe -m jupyter lab case3_antifraud.ipynb
```

На macOS/Linux команди аналогічні, але інтерпретатор розташований у `.venv/bin/python`.

## Дані

Сирі CSV не зберігаються у Git: їхній сумарний розмір перевищує 6 ГБ. Для відтворення використовується той самий набір рядків у Parquet із ZSTD-стисненням.

Команда завантаження:

```bash
python scripts/download_data.py
```

Файли завантажуються з release `data-v1` у теку `parquet/`. Розмір, кількість рядків і SHA-256 перевіряються автоматично за `data_manifest.json`.

| Файл | Рядків | Розмір |
|---|---:|---:|
| `activity_log.parquet` | 96 303 584 | 921 МіБ |
| `credits.parquet` | 35 658 710 | 269 МіБ |
| `payments.parquet` | 2 301 720 | 16 МіБ |
| `registrations.parquet` | 8 049 602 | 201 МіБ |

Якщо репозиторій було перейменовано або форкнуто:

```bash
python scripts/download_data.py --repo OWNER/REPOSITORY
```

## Power BI

`TenTens_antifraud_dashboard.pbix` відкривається одразу: імпортовані дані вже збережені всередині файлу.

Для повного оновлення:

1. запустіть ноутбук до кінця — він заново створить дев’ять CSV у `powerbi_data/`;
2. відкрийте PBIX;
3. якщо Power BI попросить шлях до джерела, вкажіть локальну теку `powerbi_data` цього репозиторію;
4. натисніть **Refresh**.

Готові CSV уже включені до репозиторію, тому dashboard можна перевірити навіть без запуску важкого розрахунку.

## Контрольний результат

Після **Run All** очікуються:

- `Spend`: **$41,941,077.24**
- `Net Revenue`: **$242,842,090**
- `Payers`: **182,734**
- мережа `612`: `ROAS · 60+ днів після реєстрації = 0.85`
- мережа `1052`: `CB amount rate · 60+ днів після платежу = 21.24%`
- експортовано **9 CSV** у `powerbi_data/`

Додаткова перевірка структури:

```bash
python scripts/verify_submission.py --require-data
```

## Технічне середовище

- Python 3.11+
- DuckDB
- pandas / NumPy
- matplotlib / seaborn
- pycountry
- Power BI Desktop для перегляду `.pbix`

Обробка великих таблиць виконується у DuckDB, без завантаження всього датасету в pandas.

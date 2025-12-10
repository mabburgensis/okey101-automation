# DracoFusion 101 Selenium Automation (CI ready)

Bu repo, 101 Okey çoklu kullanıcı (host + guests) akışını otomatikleştirir.

## Dosya yapısı

- `101.py` – Host ve guest'lerle 101 akışının tamamı (register, login, masa açma, oturma, nickname, oyun bitişini bekleme)
- `main.py` – Test runner; sadece `101.py`'yi çalıştırır ve `--guests` parametresini iletir
- `locators/okey101_locators.py` – Register, login ve 101 lobisi için tüm XPath locator'ları
- `common/browser_utils.py` – WebDriver açma ve base URL'e gitme (CI'da headless)
- `requirements.txt` – Python bağımlılıkları
- `.github/workflows/okey101.yml` – GitHub Actions workflow

## Lokal çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2 oyuncu (1 host + 1 guest)
python main.py --guests 1

# 4 oyuncu (1 host + 3 guest)
python main.py --guests 3
```

`BASE_URL` ortam değişkeni ile ortam adresini değiştirebilirsin:

```bash
export BASE_URL="https://operator.dracofusion.com/"
python main.py --guests 1
```

## GitHub Actions üzerinden çalıştırma

1. Bu repo'yu GitHub'a push et.
2. `Actions` tab'ine git, `DracoFusion 101 multi-user test` workflow'unu seç.
3. `Run workflow` butonuna bas.
4. Açılan input alanında **guests** için `1` veya `3` seç.
5. Workflow, seçtiğin guest sayısıyla `python main.py --guests N` komutunu çalıştırır.

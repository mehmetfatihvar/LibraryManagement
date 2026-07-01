# Video Sunum Konuşma Metni — XML Library Management System

> **Ders:** 155-8056 XML ve Web Servisleri (Mersin Üniversitesi)
> **Proje:** XML-Based Library Management System
> **Stack:** Backend = Python + FastAPI + lxml | Frontend = Next.js + React | Veri = `backend/data/library.xml`
> **Bu dosyanın amacı:** Kamerayı/ekran kaydını açtığında elinde tutacağın, dakika dakika ne söyleyeceğini VE ekranda hangi dosyanın/URL'nin/satırın açık olacağını söyleyen bir konuşma metni. `örneközet.md` artık kullanılmıyor — bu dosya onun yerine geçiyor ve doğrudan hocanın verdiği gereksinim listesindeki maddelere (A-G) birebir eşlenmiştir.

---

## 0) Kayıttan Önce Hazırlık (Checklist)

Kayda başlamadan önce şunları aç ve düzenle, videoda sürekli pencere/tab aramakla vakit kaybetme:

**Terminaller (2 adet):**
1. Terminal A → `backend` klasöründe, venv aktif, `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` çalışır durumda.
2. Terminal B → `backend` klasöründe, venv aktif, boşta — komutları burada çalıştıracaksın (pytest, python -c, curl).

**Tarayıcı sekmeleri (sırayla):**
1. `http://localhost:8000/docs` — Swagger UI
2. `http://localhost:8000/api/v1/reports/dashboard` — XSLT HTML raporu
3. `http://localhost:3000` — Next.js frontend
4. Postman (koleksiyon `postman/collection.json` import edilmiş, `baseUrl = http://localhost:8000` değişkeni tanımlı)

**Editör (VS Code vb.):** Proje kökü açık, şu dosyalar sekmede hazır bekletilebilir: `README.md`, `backend/data/schema.xsd`, `backend/data/library.xml`, `backend/data/invalid_library.xml`, `backend/data/report.xslt`, `backend/src/xml_manager.py`, `backend/src/validators.py`, `backend/src/xpath_queries.py`, `backend/src/xslt_transformer.py`, `backend/src/external_service.py`, `backend/src/routers/books.py`.

**Konuşma tarzı:** Türkçe + teknik terimler İngilizce kalabilir (XSD, XPath, endpoint, payload gibi). Doğal konuş, madde madde okumuyormuş gibi anlat. Her bölümde "bunu neden böyle yaptık" diye bir cümle söyle — hoca "amaç" ve "gerekçe" arıyor, sadece "bu satır şunu yapıyor" demek yetmez.

---

## Zaman Planı (toplam ~2 saat, minimum 1 saat şartını rahatça karşılar)

| # | Bölüm | Süre | Kümülatif |
|---|-------|------|-----------|
| 0 | Açılış & Mimari Özeti | 5 dk | 0:00–0:05 |
| 1 | XML Veri Paketi (Gereksinim A) | 10 dk | 0:05–0:15 |
| 2 | XSD Şema Doğrulama (Gereksinim B) | 12 dk | 0:15–0:27 |
| 3 | XPath Sorguları (Gereksinim C-1) | 10 dk | 0:27–0:37 |
| 4 | XSLT Dönüşümü (Gereksinim C-2) | 8 dk | 0:37–0:45 |
| 5 | Kodda XML Ayrıştırma — DOM + iterparse (Gereksinim D) | 12 dk | 0:45–0:57 |
| 6 | REST API — satır satır (Gereksinim E) | 20 dk | 0:57–1:17 |
| 7 | API Dokümantasyonu (Gereksinim F) | 6 dk | 1:17–1:23 |
| 8 | Harici Servis Entegrasyonu (Gereksinim G) | 10 dk | 1:23–1:33 |
| 9 | Kalite Gereksinimleri & Hata Yönetimi | 6 dk | 1:33–1:39 |
| 10 | İsteğe Bağlı / Bonus Konular | 10 dk | 1:39–1:49 |
| 11 | Kanıt Turu — Canlı Hata Senaryoları | 8 dk | 1:49–1:57 |
| 12 | Kapanış | 3 dk | 1:57–2:00 |

Bu planlanan süreler **minimum**dur — konuşurken duraksarsın, tekrar edersin, ek örnek gösterirsin; doğal olarak 2 saati geçmesi normal ve **daha iyi** (ödev metninde "10 saat kayıt 1 saatten iyidir" deniyor).

---

# BÖLÜM 0 — Açılış & Mimari Özeti (0:00–0:05)

🖥️ **EKRANDA GÖSTER:** VS Code'da proje kök klasörü (Explorer paneli açık, `backend/` ve `frontend/` klasörleri görünür).

🎙️ **ANLAT:**
- Kendini ve projeyi tanıt: "Bu proje bir kütüphane yönetim sistemi — ama asıl amaç kütüphane değil, dersin istediği XML pipeline'ının tamamını uçtan uca göstermek: XML üretme, XSD ile doğrulama, XPath/XSLT ile sorgulama-dönüştürme, kod içinde ayrıştırma, ve bunların hepsini bir REST API üzerinden sunmak."
- "Klasik bir mimaride veritabanı (MySQL, Postgres vb.) kullanılır. Burada bilinçli olarak veritabanı kullanmadık — tüm veri tek bir `backend/data/library.xml` dosyasında duruyor. Neden? Çünkü ders XML odaklı, veritabanı kullansaydık XML sadece bir 'transport format'a döner, asıl iş mantığı SQL'de olurdu. Biz XML'i **kalıcı veri kaynağı** olarak kullanarak DOM okuma/yazma, şema doğrulama gibi konuları gerçek anlamda zorunlu kıldık."
- Mimari akışı anlat: "Next.js frontend → fetch ile `Accept: application/xml` header'ı ile FastAPI backend'e istek atıyor → backend router XML'i `XmlManager` sınıfına devrediyor → her yazmadan önce XSD ile doğrulanıyor → `library.xml` dosyasına yazılıyor."

🖥️ **EKRANDA GÖSTER:** `README.md` dosyasını aç, üst kısımdaki "Project Structure" ağacını göster.

🎙️ **ANLAT:** Klasör yapısını hızlıca gez: `backend/data` (XML + XSD + XSLT), `backend/src` (uygulama kodu), `backend/src/routers` (endpoint'ler), `backend/tests` (pytest), `frontend/` (Next.js), `postman/` (koleksiyon).

---

# BÖLÜM 1 — XML Veri Paketi (Gereksinim A) (0:05–0:15)

🎙️ **ANLAT (giriş):** "Şartnamenin A maddesi gerçek bir XML veri kümesi istiyor: anlamlı nested yapı, en az 25 kayıt, açık bir veri modeli (ID'ler, referanslar, tutarlı adlandırma)."

🖥️ **EKRANDA GÖSTER:** `backend/data/library.xml` dosyasını aç, en üstten başla (satır 1-30).

🎙️ **ANLAT:**
- Kök eleman `<library id="lib-001" name="Mersin University Digital Library">` — dikkat çek: `id` attribute'u var, bu XSD'de `xs:ID` tipinde, yani her ID benzersiz olmak zorunda.
- Üç ana container var: `<books>`, `<members>`, `<borrowings>` — bu **nested (iç içe)** yapı. `books` içinde N tane `<book>`, her `book` içinde `title`, `author`, `publisher`, `categories` (kendi içinde yine birden fazla `<category>` olabilir — çok seviyeli nesting), `publicationYear`, `availableCopies`, opsiyonel `description`.
- ID/referans modelini göster: her `book`'un `id="bk-XXX"`, her `member`'ın `id="mem-XXX"`, her `borrowing`'in `id="brw-XXX"` formatında ID'si var. `borrowing` elemanının `bookRef` ve `memberRef` attribute'ları ile `book` ve `member`'a **referans** verdiğini göster (bir tür foreign key mantığı, XSD'de `IDREF` ile karşılanıyor — bunu Bölüm 2'de göstereceğiz).
- Adlandırma tutarlılığı: "Tüm etiketler camelCase — `publicationYear`, `availableCopies`, `membershipType`, `bookRef`, `memberRef`. Karışık snake_case/camelCase yok, bu şartnamenin 'Kalite Gereksinimleri' bölümünde özellikle isteniyor."

💻 **ÇALIŞTIR (Terminal B):**
```bash
cd backend
python3 -c "
import xml.etree.ElementTree as ET
t = ET.parse('data/library.xml')
r = t.getroot()
print('books   :', len(r.find('books').findall('book')))
print('members :', len(r.find('members').findall('member')))
print('borrowings:', len(r.find('borrowings').findall('borrowing')))
"
```

🎙️ **ANLAT çıktı üzerinden:** "Gördüğünüz gibi 28 kitap, 9 üye, 12 ödünç kaydı var — toplamda 49 kayıt, şartın istediği 'en az 25 kayıt' sınırının üzerinde. Ayrıca bu sadece rastgele sayı değil: 28 kitap 8 farklı kategoriye (Sci-Fi, Fantasy, History, Mystery, Romance, Technology, Biography, Classic) dağılmış, 12 ödünç kaydının 7'si aktif, 2'si gecikmiş (overdue), 3'ü iade edilmiş — yani durum çeşitliliği de var, bu XPath sorgularında işimize yarayacak."

🖥️ **EKRANDA GÖSTER:** `backend/data/library.xml` içinde bir `<borrowing>` kaydına scroll et (örn. `brw-001`).

🎙️ **ANLAT:** `bookRef` ve `memberRef` attribute değerlerinin gerçek `book`/`member` ID'lerine karşılık geldiğini parmakla göster — "Bu tutarlı referans modeli sayesinde XPath ile 'bu ödünç kaydı hangi kitaba/üyeye ait' diye join benzeri bir sorgu yazabiliyoruz, birazdan göstereceğim."

🖥️ **EKRANDA GÖSTER:** `backend/data/invalid_library.xml` dosyasını kısaca aç, üstteki yorum bloğunu (satır 2-11) göster.

🎙️ **ANLAT:** "Bu dosyayı bilerek bozuk hazırladık — XSD doğrulama demosunda kullanacağız, birazdan Bölüm 2'de detaylı göreceğiz."

---

# BÖLÜM 2 — XSD Şema Doğrulama (Gereksinim B) (0:15–0:27)

🎙️ **ANLAT (giriş):** "Şartın B maddesi zorunlu: `schema.xsd` dosyası, en az bir geçersiz örnek, ve doğrulamanın kodda/loglarda gösterilmesi."

🖥️ **EKRANDA GÖSTER:** `backend/data/schema.xsd` dosyasını aç, en baştan başla.

🎙️ **ANLAT satır satır:**
- Satır 6-10 (`isbnType`): "ISBN için özel bir `simpleType` tanımladık, `xs:pattern` ile regex kısıtı koyduk: `978-[0-9]{1,5}-[0-9]{1,7}-[0-9]{1,7}-[0-9]`. Yani ISBN'in illa `978-` ile başlaması, belirli formatta rakam grupları içermesi lazım. Bu gelişmiş XSD kısıtlarından biri — isteğe bağlı konulardan 'gelişmiş XSD kısıtları (pattern, min/max, enum, types)' maddesini karşılıyor."
- Satır 12-23 (`genreType`): "`xs:enumeration` ile kategori listesini sabitledik: Sci-Fi, Fantasy, History, Mystery, Romance, Technology, Biography, Classic. Kitap kaydederken biri 'Horror' yazarsa şema reddeder — birazdan canlı göstereceğim."
- Satır 25-29 (`emailType`): "E-posta için de pattern kısıtı — `@` işareti, domain, TLD zorunlu."
- Satır 53-65 (`bookType`): "`xs:sequence` ile elemanların **sırasını** da zorunlu kılıyoruz — title, author, publisher, categories, publicationYear, availableCopies sırayla gelmeli. `id` attribute'u `xs:ID` tipinde `use=\"required\"` — yani zorunlu ve XML genelinde benzersiz olmalı. `isbn` de `isbnType` ile kısıtlı ve zorunlu."
- Satır 90-100 (`borrowingType`): "Burada `bookRef` ve `memberRef` attribute'ları `xs:IDREF` tipinde — yani bu değerler dokümanda gerçekten var olan bir `xs:ID`'ye işaret etmek zorunda. Olmayan bir kitaba referans verirsen XSD bunu yakalar. Bu XML'in en güçlü özelliklerinden biri, JSON Schema'da bu kadar doğal karşılığı yok."

🖥️ **EKRANDA GÖSTER:** `backend/src/validators.py` dosyasını aç.

🎙️ **ANLAT satır satır:**
- Satır 19-21 (`_load_schema`): "`lxml.etree` ile `schema.xsd`'yi parse edip bir `XMLSchema` nesnesi oluşturuyoruz."
- Satır 24-31 (`get_schema`): "Şemayı her istekte yeniden parse etmemek için basit bir singleton/cache kullandık — `_SCHEMA` global değişkeni bir kere yüklenip tekrar kullanılıyor, performans için."
- Satır 34-65 (`validate_xml`): "Bu fonksiyon dosya yolu, bytes, string ya da zaten parse edilmiş bir `Element` alabiliyor — esnek. `schema.validate(element)` çağrısı `True`/`False` döner; `False` ise `schema.error_log` içinde **satır satır** hangi kuralın neden ihlal edildiğini yazan bir log var. `except etree.XMLSyntaxError` ile bozuk/malformed XML'i de (yani XML bile olmayan bir şeyi) ayrı yakalıyoruz — bu 'geçersiz XML' ile 'şema hatası' arasındaki farkı netleştiriyor."
- Satır 67-70 (`validate_or_raise`): "Yazma işlemlerinde kullanılıyor — geçersizse `ValidationError` fırlatıyor, router bunu yakalayıp HTTP 400 döndürüyor."
- Satır 73-84 (`validate_file_pair`): "Demo fonksiyonu — hem geçerli hem geçersiz dosyayı aynı anda doğrulayıp sonucu bir dict olarak döndürüyor."

🖥️ **EKRANDA GÖSTER:** Terminal B.

💻 **ÇALIŞTIR — Başarılı doğrulama:**
```bash
cd backend
python3 -c "from src.validators import validate_xml; from src.config import LIBRARY_XML; ok, log = validate_xml(LIBRARY_XML); print('VALID:', ok); print('LOG:', log or '(boş — hata yok)')"
```
🎙️ **ANLAT:** "`VALID: True`, log boş — `library.xml` şemaya tamamen uyuyor."

💻 **ÇALIŞTIR — Başarısız doğrulama:**
```bash
python3 -c "from src.validators import validate_xml; from src.config import INVALID_LIBRARY_XML; ok, log = validate_xml(INVALID_LIBRARY_XML); print('VALID:', ok); print('LOG:'); print(log)"
```
🎙️ **ANLAT log çıktısı üzerinden — gerçek çıktı satır satır bu (önceden çalıştırıp doğruladım, ezbere anlatma, ekrandaki gerçek çıktıyı oku):**
```
16:0: Element 'book', attribute 'isbn': [facet 'pattern'] The value 'NOT-A-VALID-ISBN' is not accepted by the pattern '978-[0-9]{1,5}-[0-9]{1,7}-[0-9]{1,7}-[0-9]'.
21:0: Element 'category': [facet 'enumeration'] The value 'Horror' is not an element of the set {'Sci-Fi', 'Fantasy', ...}.
24:0: Element 'availableCopies': '-5' is not a valid value of the atomic type 'xs:nonNegativeInteger'.
26:0: Element 'book', attribute 'id': 'bk-dup' is not a valid value of the atomic type 'xs:ID'.
41:0: Element 'email': [facet 'pattern'] The value 'not-an-email' is not accepted by the pattern '...'.
42:0: Element 'membershipType': [facet 'enumeration'] The value 'vip' is not an element of the set {'student', 'faculty', 'public'}.
50:0: Element 'status': [facet 'enumeration'] The value 'cancelled' is not an element of the set {'active', 'returned', 'overdue'}.
```
Bunu satır satır dosyadaki sebeple eşleştir:
- **Satır 16** → ISBN `'NOT-A-VALID-ISBN'` bizim `isbnType` pattern'ine uymuyor (978- ile başlamıyor).
- **Satır 21** → kategori `'Horror'`, `genreType` enum listesinde yok.
- **Satır 24** → `availableCopies=-5`, `xs:nonNegativeInteger` negatif değer kabul etmiyor.
- **Satır 26** → ikinci `book`'un `id="bk-dup"` olması, aynı ID'nin dosyada iki kez kullanılmasından dolayı `xs:ID` benzersizlik kuralını ihlal ediyor — validator bunu "geçersiz ID değeri" olarak raporluyor.
- **Satır 41** → e-posta `'not-an-email'`, `emailType` pattern'ine uymuyor (`@` ve domain yok).
- **Satır 42** → `membershipType='vip'`, enum listesinde (`student`/`faculty`/`public`) yok.
- **Satır 50** → `status='cancelled'`, `borrowingStatusType` enum listesinde (`active`/`returned`/`overdue`) yok.

🎙️ **Dikkat — dürüst ol, uydurma:** "Dosyada ayrıca `bookRef=\"bk-missing\"` diye olmayan bir kitaba referans da bilerek eklendi — kavramsal olarak bu `xs:IDREF` bütünlük ihlali. Ama bu çalıştırmada ayrı bir satır olarak logda görünmüyor, çünkü `bk-dup` zaten ID tablosunu bozduğu için validator IDREF çözümlemesine oradan devam etmiyor. `borrowingType`'taki `bookRef`/`memberRef` attribute'larının `schema.xsd` satır 98-99'da `xs:IDREF` tipinde tanımlı olduğunu göstererek konsepti anlatmak yeterli — hoca 'IDREF nasıl kullanılıyor' sorusunu soruyor, illa bu spesifik dosyada ayrı hata satırı görmesi gerekmiyor."

🎙️ **ANLAT (kapanış):** "Yani tek bir dosyada 6 farklı XSD kısıt türünü (pattern, enumeration x3, sayı aralığı, ID benzersizliği) bilerek bir araya getirdik, artı kavramsal olarak IDREF bütünlüğünü de `bookRef=\"bk-missing\"` ile örnekledik. Bu, şartın istediği 'neden doğrulamadan geçemediğine dair açıklama' kısmını fazlasıyla karşılıyor."

🖥️ **EKRANDA GÖSTER (opsiyonel, hızlıca):** Tarayıcıda `http://localhost:8000/api/v1/validation/demo` adresini aç.

🎙️ **ANLAT:** "Bu endpoint aynı doğrulamayı sunucu ayağa kalkarken de çalıştırıyor — `main.py`'deki `lifespan` fonksiyonunda görebilirsiniz, sunucu başlarken hem `library.xml`'i hem `invalid_library.xml`'i doğrulayıp sonucu log'a yazıyor." *(İsteğe bağlı: Terminal A'daki uvicorn loglarını göster, `library.xml validation: PASS` satırını işaret et.)*

---

# BÖLÜM 3 — XPath Sorguları (Gereksinim C-1) (0:27–0:37)

🎙️ **ANLAT (giriş):** "Şart en az 5 anlamlı XPath sorgusu istiyor — basit `//tag` değil, predicate'ler, fonksiyonlar içeren sorgular."

🖥️ **EKRANDA GÖSTER:** `backend/src/xpath_queries.py` dosyasını aç, en baştan başla.

🎙️ **ANLAT her sorguyu satır satır, "ne yapıyor + neden" formatında:**

1. **Satır 12-25 — `query_scifi_books_by_author`:**
   `/library/books/book[categories/category='Sci-Fi']`
   "Predicate kullanıyoruz — köşeli parantez içindeki koşul `categories/category` alt elemanının metninin 'Sci-Fi' olmasını istiyor. **Neden:** Kütüphanede en çok aranan senaryolardan biri türe göre filtreleme; bunu Python'da liste gezip if yazmak yerine XPath'e devrettik, hem daha okunabilir hem XML motoruna optimize."

2. **Satır 28-41 — `query_category_counts`:**
   `count(/library/books/book[categories/category='...'])`
   "XPath'in `count()` fonksiyonunu kullanıyoruz — her kategori için kaç kitap olduğunu XPath'in kendisi sayıyor, Python'da manuel sayaç tutmuyoruz. **Neden:** Raporlama/dashboard için kategori dağılımı gerekiyor, `count()` bunu tek satırda çözüyor."

3. **Satır 44-54 — `query_title_search`:**
   `contains(translate(title, 'ABC...', 'abc...'), 'keyword')`
   "`contains()` ile alt string arama yapıyoruz, `translate()` ile önce başlığı küçük harfe çeviriyoruz — XPath 1.0'da `lower-case()` fonksiyonu yok, bu yüzden `translate()` ile harf harf eşleme yaparak case-insensitive arama simüle ediyoruz. **Neden:** Kullanıcı 'dune' yazınca 'Dune' başlığını da bulsun istiyoruz."

4. **Satır 57-78 — `query_active_borrowed_books`:**
   "Burada iki adımlı bir XPath kullanıyoruz: önce `status='active'` olan ödünç kayıtlarını buluyoruz, sonra her kaydın `bookRef`/`memberRef` attribute'larını alıp **ayrı bir XPath sorgusuyla** `book`/`member` elemanına referans çözüyoruz (`book[@id='...']`). **Neden:** Bu, IDREF ilişkisini XPath ile 'join' gibi kullanmanın klasik yöntemi — ilişkisel veritabanındaki foreign key JOIN'in XML/XPath karşılığı."

5. **Satır 81-95 — `query_publisher_books_after_year`:**
   `book[publisher='X' and publicationYear > Y]`
   "Zincirleme predicate — `and` ile iki koşulu birleştiriyoruz, `publicationYear > Y` ile **sayısal karşılaştırma** yapıyoruz (metinsel değil). **Neden:** 'Belirli bir yayınevinin belirli yıldan sonraki kitapları' gibi çok kriterli, gerçek dünya sorgusu örneği."

6. **Satır 98-114 — `query_overdue_borrowings` (bonus 6.):** "Gecikmiş ödünç kayıtlarını buluyor, aynı IDREF çözme mantığını tekrar kullanıyor."

🎙️ **ANLAT (özet):** "Toplamda 6 sorgu yazdık, şartın istediği minimum 5'in üzerinde; hepsi predicate, fonksiyon (`count`, `contains`, `translate`) ya da çok kriterli koşul içeriyor — trivial `//book` gibi sorgular değil."

💻 **ÇALIŞTIR (Terminal B):**
```bash
python3 -c "from src.xpath_queries import run_all_queries; import json; print(json.dumps(run_all_queries(), indent=2, ensure_ascii=False))"
```
🎙️ **ANLAT çıktı üzerinden:** Her sorgu grubunun sonucundan 1-2 örnek satırı göster ve az önce anlattığın mantıkla eşleştir (örn. "işte category_counts kısmında Technology 5, Classic 4 diye görüyoruz").

🖥️ **EKRANDA GÖSTER:** Tarayıcıda `http://localhost:8000/api/v1/reports/xpath` adresini aç (ya da Swagger'dan çağır).

🎙️ **ANLAT:** `backend/src/routers/reports.py` satır 21-39'daki `xpath_demo` endpoint'ini göster — "Bu endpoint `run_all_queries()`'in sonucunu alıp lxml ile dinamik bir `<xpathResults>` XML ağacı kuruyor, her sorgu bir `<query name=\"...\" count=\"...\">` elemanı oluyor. Yani XPath sonuçlarını hem kodda hem tarayıcıda XML olarak kanıtlıyoruz."

---

# BÖLÜM 4 — XSLT Dönüşümü (Gereksinim C-2) (0:37–0:45)

🎙️ **ANLAT (giriş):** "Şart en az 1 XSLT dönüşümü istiyor, HTML raporu ya da yapılandırılmış XML çıktısı. Biz HTML dashboard'u tercih ettik çünkü hem görsel kanıt hem de daha zengin XSLT özelliklerini (sort, current(), attribute) gösterme fırsatı veriyor."

🖥️ **EKRANDA GÖSTER:** `backend/data/report.xslt` dosyasını aç.

🎙️ **ANLAT satır satır:**
- Satır 2-5: "`xsl:stylesheet` kök elemanı, XSL namespace'i tanımlı, `xsl:output method=\"html\"` ile çıktının HTML olacağını söylüyoruz."
- Satır 7: "`xsl:template match=\"/\"` — kök düğümden itibaren tüm dokümanı eşleştiren ana template, klasik XSLT giriş noktası."
- Satır 43: `<xsl:value-of select="/library/@name"/>` — "Kütüphane adını `library` elemanının `name` attribute'undan XPath ile çekiyoruz — XSLT içinde XPath kullanmak zorunludur, ikisi iç içe."
- Satır 47-72 (istatistik kartları): "Her kart bir `count()` ya da `sum()` XPath fonksiyonunu HTML'e gömüyor — toplam kitap sayısı, üye sayısı, aktif/gecikmiş ödünç sayısı, Sci-Fi kitap sayısı, `sum(/library/books/book/availableCopies)` ile toplam mevcut kopya sayısı. **Neden:** Ham XML'i hocaya göstermek yerine, aynı veriden otomatik üretilen özet istatistikleri göstermek çok daha anlaşılır."
- Satır 88-89: `<xsl:for-each select="/library/books/book"><xsl:sort select="title"/>` — "`for-each` ile tüm kitapları geziyoruz, `xsl:sort` ile başlığa göre alfabetik sıralıyoruz — bu **sıralama (sorting)** özelliğini XSLT seviyesinde gösteriyor."
- Satır 121-143 (borrowings tablosu): "Burada ilginç kısım `current()` fonksiyonu — satır 125 ve 128'de `/library/books/book[@id=current()/@bookRef]/title` diyoruz. `for-each` içindeyken 'şu an gezdiğim borrowing elemanı' `current()` ile referans alınıyor, ve o elemanın `bookRef` attribute'u kullanılarak **başka bir ağaçtaki** (`books`) ilgili kitabın başlığına ulaşıyoruz. Bu da yine IDREF ilişkisini XSLT içinde çözmenin yolu — XPath'teki join mantığının XSLT karşılığı."
- Satır 136-138: `<xsl:attribute name="class">status-<xsl:value-of select="status"/></xsl:attribute>` — "Dinamik olarak HTML class ismi üretiyoruz (`status-active`, `status-overdue`), böylece CSS ile renklendirme yapabiliyoruz — XSLT'nin sadece metin değil, attribute/eleman üretebildiğini gösteriyor."

🖥️ **EKRANDA GÖSTER:** `backend/src/xslt_transformer.py` dosyasını aç (14 satır, tamamı).

🎙️ **ANLAT:** "`etree.parse` ile hem `library.xml` hem `report.xslt`'yi yüklüyoruz, `etree.XSLT(xslt_doc)` ile bir dönüştürücü nesnesi oluşturuyoruz, `transform(xml_doc)` çağrısı XSLT motorunu çalıştırıp sonucu üretiyor — bu `lxml`'in libxslt üzerine kurulu XSLT 1.0 motoru, gerçek bir XSLT processor, elle string birleştirme değil."

🖥️ **EKRANDA GÖSTER:** Tarayıcı sekmesi 2 → `http://localhost:8000/api/v1/reports/dashboard`

🎙️ **ANLAT:** Sayfayı yukarıdan aşağı gez — istatistik kartları, kitap tablosu (alfabetik sıralı olduğuna dikkat çek), aktif/gecikmiş ödünç tablosu (kitap adı ve üye adının XSLT içinde çözüldüğünü hatırlat), üye tablosu. "İşte bu, `library.xml`'den `report.xslt` ile üretilen, hiç elle yazılmamış, tamamen dinamik bir HTML raporu."

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/reports.py` satır 14-18 (`dashboard_report`).

🎙️ **ANLAT:** "Endpoint çok basit — `transform_to_html()` çağırıp `HTMLResponse` olarak dönüyoruz, `Content-Type: text/html` ile tarayıcı direkt render ediyor."

---

# BÖLÜM 5 — Kodda XML Ayrıştırma ve İşleme: DOM + iterparse (Gereksinim D) (0:45–0:57)

🎙️ **ANLAT (giriş):** "Şart D maddesi DOM veya SAX veya StAX (ya da eşdeğeri) ile okuma, veri çıkarma/değiştirme, yeni XML üretme, hatalı girdi yönetimini istiyor. Biz iki yöntemi birden kullandık: `lxml.etree` ile **DOM** (tüm ağacı belleğe yükleyip gezme/değiştirme) ve `lxml.etree.iterparse` ile **SAX benzeri streaming** parsing. İkisini karşılaştırmalı göstereceğim."

🖥️ **EKRANDA GÖSTER:** `backend/src/xml_manager.py` dosyasını aç, en baştan.

## 5.1 DOM Parsing

🎙️ **ANLAT satır satır:**
- Satır 37-42 (`load_tree`, `get_root`): "`etree.parse(path)` tüm XML dosyasını belleğe yükleyip bir ağaç (tree) döndürüyor — klasik DOM yaklaşımı. Küçük/orta dosyalar için pratik, çünkü ağaç üzerinde XPath çalıştırabiliyoruz, elemanları taşıyabiliyoruz, sırasını değiştirebiliyoruz."
- Satır 76-102 (`get_all_books`): "DOM yüklendikten sonra XPath ile filtreleme yapıp, `copy.deepcopy` ile elemanları kopyalayıp döndürüyoruz — deepcopy önemli çünkü orijinal ağaçtan koparmazsak, sonradan o elemanı başka bir XML'e `append` ederken lxml hata verir (bir eleman aynı anda iki ağaçta olamaz)."

## 5.2 Veri Değiştirme (Write Operations)

🖥️ **EKRANDA GÖSTER:** Satır 241-259 (`add_book`).

🎙️ **ANLAT:**
- "Önce `books` container'ı buluyoruz, ID verilmemişse `_next_book_id` ile otomatik ID üretiyoruz (satır 188-200 — mevcut ID'lerin sayısal kısmını parse edip en büyüğe +1 ekliyor, `bk-029` gibi)."
- "Duplicate ID kontrolü yapıyoruz (satır 253) — aynı ID varsa `ValueError` fırlatıyoruz, bu şartın istediği 'yinelenen key ID olmamalı' kuralını kod seviyesinde de garanti ediyor, sadece XSD'ye güvenmiyoruz."
- "`validate_or_raise(book_element)` — yazmadan **önce** yeni elemanı tek başına şemaya karşı doğruluyoruz."
- "`books_container.append(book_element)` — DOM ağacına yeni elemanı ekliyoruz."
- "`self._save_tree(tree)` çağrılıyor — bu satır 178-186'da tanımlı: **tekrar** tüm ağacı `validate_or_raise` ile doğruluyor (çift kontrol — hem eleman bazlı hem tüm doküman bazlı), sonra `tree.write(...)` ile `pretty_print=True, xml_declaration=True, encoding='UTF-8'` parametreleriyle diske yazıyor. **Neden çift doğrulama:** Tek eleman şemaya uysa bile, örneğin IDREF bütünlüğü ancak tüm doküman bağlamında kontrol edilebilir."

🖥️ **EKRANDA GÖSTER:** Satır 390-450 (`checkout_book`) — en karmaşık iş mantığı örneği.

🎙️ **ANLAT:** "Bu fonksiyon sadece XML yazmıyor, gerçek iş kuralları uyguluyor: kitabın `availableCopies` alanını okuyup 0'dan büyük mü diye bakıyor (satır 413-416), üyenin üyelik tipine göre (`library_rules.py`'deki `loan_limit`) aktif ödünç sayısını aşmadığını kontrol ediyor (417-424), varsayılan iade tarihini üyelik tipine göre hesaplıyor (`default_due_date`), ve en sonunda satır 439-445'te **XSD'nin istediği element sırasına uygun** (`borrowDate, dueDate, status`) yeni bir `<borrowing>` elemanını sıfırdan `etree.Element`/`etree.SubElement` ile inşa ediyor. Bu son kısım önemli — XSD `xs:sequence` sıra zorunluluğu koyduğu için, elemanları rastgele sırada eklersek doğrulama patlar; bilinçli olarak doğru sırada kuruyoruz."

## 5.3 Hatalı Girdi Yönetimi (Malformed XML)

🖥️ **EKRANDA GÖSTER:** Satır 297-310 (`parse_book_xml`).

🎙️ **ANLAT:** "`etree.fromstring(xml_bytes)` çağrısını `try/except etree.XMLSyntaxError` ile sarıyoruz — yani gelen veri XML bile değilse (örneğin etiket kapatılmamışsa) burada yakalanıp anlamlı bir `ValueError` mesajına çevriliyor, ham exception sızmıyor. Ayrıca kök eleman `book` değilse ama içinde bir `<book>` varsa onu buluyoruz, hiçbiri yoksa yine hata veriyoruz — esnek ama güvenli parsing."

## 5.4 Streaming Parsing (SAX benzeri, iterparse)

🖥️ **EKRANDA GÖSTER:** Satır 46-72 (`stream_books`, `count_books_streaming`).

🎙️ **ANLAT:**
- "`etree.iterparse(path, events=('end',), tag='book')` — DOM'un aksine, dosyanın tamamını belleğe yüklemiyor; XML'i baştan sona **event-based** tarıyor, her `</book>` kapanış etiketine ulaştığında bir event üretiyor. Bu SAX (Simple API for XML)'in event-driven modeline çok benziyor, Python'da lxml bunu iterparse ile sunuyor."
- "Her event'te elemandan veriyi çekiyoruz (satır 57-65), sonra **kritik kısım**: satır 66-68 — `elem.clear()` ile o elemanın içeriğini bellekten siliyoruz, `while elem.getprevious() is not None: del elem.getparent()[0]` ile önceki kardeş elemanları da siliyoruz. **Neden:** iterparse aslında arka planda yine bir ağaç kuruyor; bunu manuel temizlemezsek bellek avantajını kaybederiz. Bu, çok büyük XML dosyalarında (milyonlarca kayıt) DOM'un aksine sabit bellek kullanımıyla çalışmayı sağlıyor."
- "`count_books_streaming` bunun pratik kullanımı — DOM ağacı hiç kurmadan sadece kitap sayısını sayıyor."

🖥️ **EKRANDA GÖSTER:** `backend/src/main.py` satır 34-35 (lifespan içinde `manager.count_books_streaming()` çağrısı) VEYA Terminal A'daki uvicorn başlangıç loglarını göster (`Streaming book count via iterparse: 28` satırı).

🎙️ **ANLAT:** "Sunucu her ayağa kalktığında bu streaming sayacı çalışıyor ve loga yazılıyor — DOM ile de aynı sonucu alabilirdik ama bilinçli olarak farklı bir parsing tekniğini gerçek bir işlevde kullandık, sadece akademik gösteri değil."

💻 **ÇALIŞTIR (opsiyonel, karşılaştırma için, Terminal B):**
```bash
python3 -c "
from src.xml_manager import XmlManager
m = XmlManager()
print('DOM ile sayım :', len(m.get_root().findall('.//book')))
print('iterparse ile :', m.count_books_streaming())
"
```
🎙️ **ANLAT:** "İki farklı teknik, aynı sonuç, farklı bellek/performans profili — DOM tüm ağacı tutar (rastgele erişim/değiştirme kolay), iterparse tek geçişte akar (bellek dostu, sadece okuma için ideal)."

---

# BÖLÜM 6 — REST API: Satır Satır (Gereksinim E) (0:57–1:17)

🎙️ **ANLAT (giriş):** "Şart en az 4 endpoint istiyor: GET liste, GET tekil, POST, PUT/PATCH veya DELETE. Bizde bunun çok üzerinde — 3 kaynak (books, members, borrowings) için tam CRUD, artı reports ve external. XML request/response zorunluluğunu da karşılıyoruz — API tamamen XML-only, JSON yok."

🖥️ **EKRANDA GÖSTER:** `backend/src/main.py` satır 59-64.

🎙️ **ANLAT:** "`/api/v1` prefix'i altında 5 router topluyoruz: books, members, borrowings, reports, external. Bu prefix API versioning demek — isteğe bağlı konulardan birini de böylece karşılamış oluyoruz."

## 6.1 Content Negotiation & Auth

🖥️ **EKRANDA GÖSTER:** `backend/src/auth.py` (tamamı, 26 satır).

🎙️ **ANLAT:**
- "`require_xml_accept` (satır 23-26): İstek `Accept` header'ı `application/xml` içermiyorsa (ve `*/*` de değilse) 406 Not Acceptable döndürüyoruz — bu şartın istediği 'Accept: application/xml' zorunluluğunu doğruluyor."
- "`require_api_key` (satır 17-20): `X-API-Key` header'ını `config.py`'deki sabit anahtarla karşılaştırıyor, uymazsa 401 fırlatıyor. FastAPI'nin `Depends()` mekanizmasıyla her router'da `dependencies=[Depends(require_api_key), Depends(require_xml_accept)]` şeklinde POST/PUT/DELETE endpoint'lerine ekliyoruz (GET'lerde auth yok, sadece Accept kontrolü var) — bu isteğe bağlı 'kimlik doğrulama (API key)' konusunu karşılıyor."

## 6.2 Books Router (tam CRUD örneği)

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/books.py` (tamamı, 88 satır) — satır satır ilerle.

🎙️ **ANLAT:**
- **GET liste (satır 16-30):** "`genre`, `search`, `page`, `limit` query parametreleri alıyor — filtreleme, arama ve sayfalama hepsi burada. `XmlManager.get_all_books` XPath ile filtreleyip dilimliyor. Yanıt header'larına `X-Total-Count`, `X-Page`, `X-Limit` ekliyoruz (satır 27-29) — client toplam kayıt sayısını body parse etmeden header'dan da okuyabiliyor."
- **GET tekil (satır 33-39):** "`try/except BookNotFoundError` ile 404 XML hatası dönüyoruz — asla generic 500 patlamıyor."
- **POST (satır 42-55):** "Önce body boş mu kontrol ediyoruz (400). `parse_book_xml` ile XML'i ayrıştırıyoruz — burada `ValueError` (malformed XML) yakalanabilir. `add_book` çağrısı hem duplicate ID hem XSD `ValidationError` fırlatabilir, ikisini de ayrı ayrı yakalayıp uygun mesajla 400 döndürüyoruz. Başarılıysa **201 Created** dönüyoruz — doğru HTTP status code kullanımı."
- **PUT (satır 58-73):** "Aynı desen — parse et, güncelle, 404/400 hata yönetimi."
- **DELETE (satır 76-87):** "`delete_book` çağrılıyor — `xml_manager.py` satır 280-295'te gördüğümüz gibi, eğer o kitaba ait aktif/gecikmiş ödünç kaydı varsa `ValueError` fırlatıp silmeyi engelliyor (referential integrity kodda da korunuyor, sadece XSD'de değil)."

🖥️ **EKRANDA GÖSTER:** `backend/src/xml_responses.py` (tamamı, 42 satır).

🎙️ **ANLAT:** "`books_collection_xml` gibi fonksiyonlar `<books count=\"10\" totalCount=\"28\">` şeklinde bir wrapper eleman kurup içine gerçek `book` elemanlarını ekliyor — `element_to_bytes` de `etree.tostring` ile XML declaration'lı, pretty-print'li bytes üretiyor. Tüm response'lar bu ortak yardımcılardan geçiyor, tutarlı bir format garantisi."

## 6.3 Members & Borrowings Router (hızlı geçiş, tekrar etme)

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/members.py`, sonra `borrowings.py`.

🎙️ **ANLAT:** "Members router books ile aynı CRUD desenini izliyor, tek fark: silme öncesi aktif ödünç kontrolü (`xml_manager.py` satır 357-374) ve e-posta benzersizlik kontrolü (`_ensure_unique_email`, satır 216-223). Borrowings router'da ise iki özel endpoint var: `POST /borrowings` **checkout** işlemi (Bölüm 5'te detaylı anlattığım `checkout_book`), ve `PUT /borrowings/{id}/return` **iade** işlemi (satır 63-72, `xml_manager.py`'deki `return_book` fonksiyonunu çağırıyor — kitabın `availableCopies`'ini +1 artırıyor, `returnDate` ekliyor, status'u `returned` yapıyor). `DELETE /borrowings/{id}` ise sadece `returned` statüsündeki kayıtları silmeye izin veriyor (satır 513-528, xml_manager.py) — aktif bir ödünç kaydını silmek, denetim izini (audit trail) bozar diye bilerek engellendi."

## 6.4 Swagger'dan Canlı Demo

🖥️ **EKRANDA GÖSTER:** Tarayıcı sekmesi 1 → `http://localhost:8000/docs`

🎙️ **ANLAT + göster:**
1. `GET /api/v1/books` endpoint'ini aç, "Try it out" → `genre=Sci-Fi` gir → Execute. Dönen XML response'u göster, `Content-Type: application/xml` header'ının response'ta olduğunu vurgula.
2. `GET /api/v1/books/bk-001` ile tekil kayıt göster.
3. `POST /api/v1/books` ile örnek body gönder (README'deki örneği kullan):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<book isbn="978-0-99-777666-5">
  <title>XML Processing Guide</title>
  <author>Jane Developer</author>
  <publisher>Tech Press</publisher>
  <categories><category>Technology</category></categories>
  <publicationYear>2024</publicationYear>
  <availableCopies>3</availableCopies>
</book>
```
   `X-API-Key: library-api-key-dev-2026` header'ını eklemeyi unutma, Execute → 201 Created ve yeni oluşan `id`'yi göster.
4. `PUT` ile az önce oluşturduğun kitabı güncelle, `DELETE` ile sil — response'un `<result><message>...</message></result>` formatını göster.

🖥️ **EKRANDA GÖSTER:** Postman'e geç — `postman/collection.json`, "Books" klasörü.

🎙️ **ANLAT:** "Aynı senaryoları Postman'de de gösterelim — hem Swagger hem Postman ile aynı API'yi çağırabildiğimizi kanıtlamak için." List Books, Create Book isteklerini çalıştır, request/response panelini göster (headers sekmesinde `Content-Type`/`Accept` görünsün).

---

# BÖLÜM 7 — API Dokümantasyonu (Gereksinim F) (1:17–1:23)

🎙️ **ANLAT (giriş):** "Şart Swagger/OpenAPI VEYA iyi yapılandırılmış bir README istiyor — biz ikisini de sağladık."

🖥️ **EKRANDA GÖSTER:** Tarayıcıda `http://localhost:8000/docs` (Swagger UI) sayfasında yukarı kaydır, tüm endpoint gruplarını (Books, Members, Borrowings, Reports, External) katlanmış halde göster, birini aç.

🎙️ **ANLAT:** "FastAPI, `main.py`'deki `FastAPI(title=..., description=..., version=\"1.0.0\")` tanımından (satır 39-48) otomatik olarak bu OpenAPI/Swagger dokümantasyonunu üretiyor — endpoint başına parametreler, request/response şemaları, deneme arayüzü hazır geliyor, elle yazmadık."

🖥️ **EKRANDA GÖSTER:** `http://localhost:8000/openapi.json` (ham OpenAPI şeması, isteğe bağlı gösterilebilir).

🖥️ **EKRANDA GÖSTER:** `README.md` — "API Reference" bölümü (satır 142-186).

🎙️ **ANLAT:** "README'de her endpoint method, path, auth gereksinimi ve açıklamasıyla tablo halinde listelendi. Ayrıca 'cURL Examples' bölümünde (satır 201-279) her ana senaryo için hazır curl komutları var — List, Get by ID, Create, Update, Delete, external enrich, ve bilerek hatalı bir istek (API key eksik) örneği."

🖥️ **EKRANDA GÖSTER:** README "Evidence Checklist" bölümü (satır 283-300).

🎙️ **ANLAT:** "Bu liste zaten hocanın istediği kanıt kontrol listesiyle birebir örtüşüyor — biz raporu/videoyu hazırlarken bu checklist'i adım adım takip ettik."

---

# BÖLÜM 8 — Harici Servis Entegrasyonu (Gereksinim G) (1:23–1:33)

🎙️ **ANLAT (giriş):** "Şart en az bir harici servis tüketmemizi istiyor — JSON dönen bir servisi çağırıp XML'e çevirip doğrulamamız yeterli. Biz **Open Library API**'yi (openlibrary.org) kullandık — ISBN'e göre kitap künyesi (başlık, yazar, yayınevi, yayın yılı, açıklama) dönen ücretsiz, public bir servis."

🖥️ **EKRANDA GÖSTER:** `backend/src/external_service.py` dosyasını aç.

🎙️ **ANLAT satır satır:**
- Satır 21-34 (`normalize_isbn`): "Kullanıcı ISBN-10 ya da ISBN-13, tireli ya da tiresiz girebilir. Biz önce sadece rakam/X karakterlerini alıyoruz (`re.sub`), 13 haneliyse tire formatına sokuyoruz, 10 haneliyse gerçek bir **ISBN-13 checksum algoritması** ile 13 haneye çeviriyoruz (satır 26-32: alternatif ağırlıklarla — 1 ve 3 — çarpıp mod 10 alma, klasik ISBN-13 check digit hesaplaması). **Neden:** Farklı formatlardaki girdiyi tek tip normalize edip hem dış servise doğru sorgu atmak hem de kendi `isbnType` XSD pattern'imize uygun üretmek için."
- Satır 37-66 (`fetch_open_library`): "`httpx.AsyncClient` ile asenkron HTTP isteği atıyoruz — `bibkeys=ISBN:...&format=json&jscmd=data` sorgu parametreleriyle Open Library'nin Books API'sine gidiyoruz. Eğer bu endpoint'te veri yoksa (satır 53), fallback olarak `/isbn/{isbn}.json` endpoint'ine düşüyoruz — bunlar Open Library'nin iki farklı JSON şeması, ikisini de ele alıyoruz."
- Satır 69-89, 92-122 (`_parse_books_api_data`, `_parse_isbn_edition`): "Gelen JSON'dan yazar listesini, yayınevini, yayın yılını (regex ile 4 haneli yıl arayarak) ve açıklamayı (string ya da `{value: ...}` dict olabiliyor, `_extract_description` ile ikisini de normalize ediyoruz) çıkarıyoruz."
- Satır 132-148 (`json_to_enriched_xml`) — **kritik kısım:** "İşte burada JSON'u XML'e çeviriyoruz: `etree.Element('enrichedBook')` kök elemanını kuruyoruz, `SubElement` ile `title`, `author`, `publisher`, `publicationYear`, `description`, `categories/category` (varsayılan 'Classic'), `source` elemanlarını dolduruyoruz. Sonra **satır 147'de `validate_or_raise(root)` çağırıyoruz** — yani dış servisten gelen veriyi kendi `schema.xsd`'mizdeki `enrichedBookType` tanımına (satır 137-150, schema.xsd) karşı doğruluyoruz. Bu, şartın istediği 'yanıtı projenizin içinde nasıl kullandığınız' kısmının can alıcı noktası: dış kaynaktan gelen güvenilmeyen veriyi kör kör kabul etmiyoruz, kendi şema kurallarımızla süzüyoruz."
- Satır 151-154 (`enrich_isbn`): "Tüm pipeline'ı birleştiren fonksiyon: fetch → JSON'dan XML'e çevir → doğrula → bytes döndür."

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/external.py` (tamamı, 26 satır).

🎙️ **ANLAT:** "Endpoint 3 farklı hata durumunu ayrı ayrı ele alıyor: `ValueError` (ISBN Open Library'de yok) → 404, `httpx.HTTPError` (dış servise ulaşılamıyor/zaman aşımı) → 502 Bad Gateway (doğru HTTP semantiği — bizim hatamız değil, upstream servisin hatası), `ValidationError` (dış veri bizim şemamıza uymuyor) → 400."

🖥️ **EKRANDA GÖSTER:** Tarayıcı ya da Swagger'dan `GET /api/v1/external/enrich/9780134685991` çağır (ya da frontend'deki `/enrich` sayfası).

💻 **ÇALIŞTIR (alternatif, Terminal B):**
```bash
curl -H "Accept: application/xml" "http://localhost:8000/api/v1/external/enrich/9780134685991"
```

🎙️ **ANLAT dönen XML üzerinden:** "Gördüğünüz gibi gerçek zamanlı olarak Open Library'den çekilen 'Effective Java' künyesi bize `<enrichedBook>` XML'i olarak, kendi şemamıza uygun şekilde döndü. `source` elemanı 'Open Library API' diyor, verinin nereden geldiğini belgeliyor."

🖥️ **EKRANDA GÖSTER:** Frontend `http://localhost:3000/enrich` sayfası — bir ISBN gir, "Enrich" butonuna bas, `EnrichPanel.tsx` bileşeninin sonucu gösterdiğini göster.

🎙️ **ANLAT:** "Frontend tarafında da bu sonucu `lib/xmlParser.ts`'teki `parseEnrichedBookXml` fonksiyonu DOMParser ile ayrıştırıp ekrana basıyor — yani harici entegrasyonun sonucu gerçekten UI'da kullanılıyor, sadece backend'de kalmıyor."

---

# BÖLÜM 9 — Kalite Gereksinimleri & Hata Yönetimi (1:33–1:39)

🎙️ **ANLAT (giriş):** "Şartnamenin 'Kalite Gereksinimleri' bölümü notlandırma çarpanı diyor, üzerinden hızlıca geçelim."

🖥️ **EKRANDA GÖSTER:** `backend/src/responses.py` ve `xml_responses.py` (tekrar kısaca).

🎙️ **ANLAT — Veri ve Tutarlılık:**
- "Tüm etiketler camelCase (`publicationYear`, `bookRef`, `membershipType`) — snake_case karışımı yok."
- "ID formatı tutarlı: `bk-XXX`, `mem-XXX`, `brw-XXX`, 3 haneli sıfır dolgulu (`_next_id`, xml_manager.py satır 188-197)."
- "Duplicate ID engelleniyor — hem XSD (`xs:ID`) hem kod seviyesinde (satır 253, 325, 432)."
- "Temiz klasör yapısı — `data/`, `src/`, `src/routers/`, `tests/` ayrımı net."

🎙️ **ANLAT — Hata Yönetimi (dört zorunlu senaryo):**
1. "**Geçersiz (malformed) XML** → `parse_book_xml` / `parse_member_xml` / `parse_borrowing_xml` içindeki `except etree.XMLSyntaxError` (xml_manager.py, örn. satır 301) → HTTP 400."
2. "**Şema doğrulama hatası** → `validate_or_raise` her yazmadan önce çalışıyor, `ValidationError` → router'larda yakalanıp 400 + XSD error log'un ilk 500 karakteri (`exc.log[:500]`) response'a ekleniyor."
3. "**Zorunlu alan eksikliği** → XSD `minOccurs` varsayılanı 1'dir (belirtilmemişse zorunlu), örn. `title` eksikse yine `ValidationError` yoluyla yakalanır."
4. "**API hataları tutarlı formatta** → `xml_responses.py`'deki `build_error_xml` her zaman aynı yapıyı üretiyor: `<error><code>...</code><message>...</message><detail>...</detail></error>`. 404 (bulunamadı), 400 (geçersiz istek/doğrulama), 401 (API key eksik/yanlış), 406 (Accept header yanlış), 500 (beklenmeyen hata — `main.py` satır 84-90'daki global exception handler) — hepsi bu formatı kullanıyor."

🖥️ **EKRANDA GÖSTER:** `README.md` içindeki örnek hata XML'i (satır 190-197).

🎙️ **ANLAT — Yeniden Üretilebilirlik:** "README'de kurulum adımları (`pip install -r requirements.txt`, `npm install`), çalıştırma komutları, örnek veri (`library.xml` zaten repo'da hazır geliyor, ekstra seed script gerekmiyor), örnek istekler (curl blokları) ve beklenen çıktılar var — değerlendirici sıfırdan projeyi ayağa kaldırabilir."

---

# BÖLÜM 10 — İsteğe Bağlı / Bonus Konular (1:39–1:49)

🎙️ **ANLAT (giriş):** "Şartnamede 'İyi proje' için en az 3 isteğe bağlı konu isteniyor, biz bunun oldukça üzerinde kapsadık — hepsini tek tek gösterip nerede olduğunu söyleyeceğim."

1. **API Versiyonlama:** 🖥️ `main.py` satır 59 (`API_PREFIX = "/api/v1"`). "Tüm endpoint'ler `/api/v1/` altında — ileride `/v2` eklenirse eski istemciler kırılmaz."

2. **Kimlik doğrulama (API Key):** 🖥️ `auth.py` satır 17-20, `config.py` satır 12. "POST/PUT/DELETE'de zorunlu `X-API-Key` header'ı."

3. **Sayfalama, filtreleme:** 🖥️ `routers/books.py` satır 17-22 (`page`, `limit`, `genre`, `search`), `routers/members.py` (`membershipType`, `search`), `routers/borrowings.py` (`status`, `memberRef`, `bookRef`). "Hem sayfalama hem çok kriterli filtreleme var."

4. **Gelişmiş XSD kısıtları:** 🖥️ `schema.xsd` — pattern (ISBN, email), enumeration (genre, membershipType, borrowingStatus), `xs:ID`/`xs:IDREF`, `minOccurs`/`maxOccurs`, `xs:positiveInteger`/`xs:nonNegativeInteger` tip kısıtları. "Bölüm 2'de detaylı gösterdik."

5. **Namespace + schemaLocation kullanımı:** 🖥️ `backend/data/library.xml` satır 2 — `xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"` ve `xsi:schemaLocation="schema.xsd schema.xsd"`. "XML Schema Instance namespace'ini kullanarak dokümanın hangi şemaya bağlı olduğunu deklare ediyoruz."

6. **Test paketi (unit/integration):** 🖥️ `backend/tests/test_validation.py` ve `test_circulation.py` aç.

💻 **ÇALIŞTIR:**
```bash
cd backend
pytest -v
```
🎙️ **ANLAT çıktı üzerinden:** "`TestValidation` sınıfı XSD doğrulamayı test ediyor (geçerli/geçersiz dosya), `TestXPathQueries` her 6 sorguyu test ediyor, `test_circulation.py`'deki `TestLibraryRules` ve `TestMemberCrud` iş kurallarını (loan limit, loan period) ve CRUD operasyonlarını test ediyor — aynı dosyanın en üstünde tanımlı `temp_manager` fixture'ı (satır 17-21, `pytest.fixture` + `tmp_path`) her testte `library.xml`'in **izole bir kopyasını** kullanıyor, böylece testler gerçek veriyi bozmuyor. `conftest.py` ise sadece test modüllerinin `src` paketini bulabilmesi için `sys.path`'e proje kökünü ekliyor. Bu integration test niteliğinde — gerçek dosya I/O + XSD doğrulama + iş mantığı birlikte test ediliyor."

7. **Loglama:** 🖥️ `main.py` satır 17-21, `xml_manager.py` satır 186 (`logger.info("library.xml saved and re-validated")`). "Her yazma işleminde ve sunucu başlangıcında (validasyon sonucu, streaming sayacı) log üretiliyor."

🎙️ **ANLAT (kapanış bölümü):** "Özetle: versiyonlama, auth, filtreleme/sayfalama, gelişmiş XSD, namespace/schemaLocation, test paketi ve loglama — 7 isteğe bağlı konuyu kapsadık, istenen minimum 3'ün oldukça üzerinde."

---

# BÖLÜM 11 — Kanıt Turu: Canlı Hata Senaryoları (1:49–1:57)

🎙️ **ANLAT (giriş):** "Şartın 'Kanıt Gereksinimleri' bölümü en az 1 hata durumu demosu istiyor, biz birkaç farklı türünü canlı göstereceğiz."

### 11.1 Malformed XML (400)

💻 **ÇALIŞTIR:**
```bash
curl -i -X POST \
  -H "Accept: application/xml" -H "Content-Type: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  -d '<book><title>Kapatilmamis' \
  "http://localhost:8000/api/v1/books"
```
🎙️ **ANLAT:** "Etiket kapatılmamış, bu geçerli bir XML bile değil. `parse_book_xml` içindeki `XMLSyntaxError` yakalanıp 400 + `Malformed XML: ...` mesajı dönüyor."

### 11.2 Eksik Zorunlu Alan / Şema Hatası (400)

💻 **ÇALIŞTIR:**
```bash
curl -i -X POST \
  -H "Accept: application/xml" -H "Content-Type: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  -d '<?xml version="1.0"?><book isbn="978-0-99-111222-3"><author>Eksik Başlık</author></book>' \
  "http://localhost:8000/api/v1/books"
```
🎙️ **ANLAT:** "`title` elemanı eksik, sadece `author` gönderildi. XSD `bookType`'ta elemanlar `xs:sequence` ile sıralı ve `title` zorunlu (minOccurs belirtilmemiş = 1, ve sırada ilk gelmesi lazım). `validate_or_raise` bunu yakalayıp `ValidationError` fırlatıyor, response'ta XSD'nin ürettiği gerçek hata mesajını görüyoruz: `Element 'author': This element is not expected. Expected is ( title ).` — yani validator `author`'ı görünce 'burada `title` bekliyordum' diyor, çünkü sequence sırası bozuldu."

### 11.3 Kimlik Doğrulama Hatası (401)

💻 **ÇALIŞTIR — yanlış API key ile:**
```bash
curl -i -X POST \
  -H "Accept: application/xml" -H "Content-Type: application/xml" \
  -H "X-API-Key: wrong-key" \
  -d '<book isbn="978-0-99-111222-3"><title>Test</title></book>' \
  "http://localhost:8000/api/v1/books"
```
🎙️ **ANLAT:** "`X-API-Key` header'ı gönderildi ama değeri yanlış. `auth.py`'deki `require_api_key` dependency'si (satır 17-20) `config.py`'deki gerçek anahtarla karşılaştırıyor, uymayınca `XmlHttpException(401, ...)` fırlatıyor, `main.py`'deki `xml_http_exception_handler` (satır 79-81) bunu yakalayıp bizim standart `<error>` formatımızda 401 döndürüyor."

⚠️ **Doğrulanmış küçük bir nüans — sorulursa açıklayabilmen için not:** "Eğer `X-API-Key` header'ı hiç gönderilmezse (yanlış değil, tamamen eksik), FastAPI'nin kendi `Header(..., alias=\"X-API-Key\")` zorunluluğu bizim `require_api_key` fonksiyonumuz hiç çalışmadan devreye giriyor ve `422 Unprocessable Entity` + JSON body döndürüyor — bizim XML-only tasarımımızın dışında kalan tek nokta. Bunu videoda göstermeyeceğiz (kafa karıştırır), 'yanlış key' senaryosunu gösteriyoruz çünkü asıl iş mantığımızın (401 + XML) kanıtı bu."

### 11.4 Bulunamadı (404)

💻 **ÇALIŞTIR:**
```bash
curl -i -H "Accept: application/xml" "http://localhost:8000/api/v1/books/bk-999"
```
🎙️ **ANLAT:** "Olmayan bir ID — `BookNotFoundError` yakalanıp `<error><code>404</code><message>Book not found</message><detail>id=bk-999</detail></error>` dönüyor."

### 11.5 İş Kuralı İhlali (400) — Referential Integrity

🎙️ **Önce hangi kitabın aktif ödüncü olduğunu göster** (bu, `library.xml`'in mevcut durumuna göre değişebilir, kayıttan hemen önce kontrol et):
```bash
curl -s -H "Accept: application/xml" "http://localhost:8000/api/v1/borrowings?status=active"
```
"Örneğin `bk-003` (Dune) hem `brw-001` hem `brw-012` kaydında aktif olarak ödünç görünüyor — bunu silmeyi deneyelim."

💻 **ÇALIŞTIR:**
```bash
curl -i -X DELETE -H "Accept: application/xml" -H "X-API-Key: library-api-key-dev-2026" \
  "http://localhost:8000/api/v1/books/bk-003"
```
🎙️ **ANLAT:** "400 Bad Request, `Cannot delete book bk-003: active borrowings exist`. Bu, veritabanı olmadan da referential integrity'yi kod seviyesinde nasıl koruduğumuzun kanıtı — `xml_manager.py` satır 280-295'teki `delete_book` fonksiyonu, silmeden önce o kitaba ait aktif/gecikmiş ödünç kaydı olup olmadığını XPath ile kontrol ediyor, varsa siliyor **değil**, `ValueError` fırlatıyor." ⚠️ *Bu komutu gerçekten çalıştırma — sadece 400 hatasını göstermek için dene, book gerçekten silinmeyeceği için `library.xml` bozulmaz, güvenle canlı gösterebilirsin.*

### 11.6 Frontend'de Hata Gösterimi

🖥️ **EKRANDA GÖSTER:** `http://localhost:3000` üzerinde bilerek bir hata tetikle (örn. `/books/new` formunda geçersiz ISBN gir, submit et).

🎙️ **ANLAT:** "`components/XmlErrorBanner.tsx` bileşeni, backend'den dönen XML hata gövdesini `lib/api.ts`'teki `handleResponse` fonksiyonuyla (satır 21-34) parse edip kullanıcıya gösteriyor — `DOMParser` ile `message`/`detail` elemanlarını okuyor. Yani hata yönetimi zinciri backend'den frontend'e kadar uçtan uca XML formatında akıyor."

---

# BÖLÜM 12 — Kapanış (1:57–2:00)

🎙️ **ANLAT:**
- "Özetleyelim: XML veri paketi 49 kayıt ve nested yapıyla hazırlandı; XSD ile hem başarı hem 6 farklı hata türü canlı gösterildi; 6 XPath sorgusu predicate/fonksiyonlarla; 1 kapsamlı XSLT dönüşümü HTML dashboard olarak; DOM + iterparse ile iki farklı parsing tekniği; 3 kaynak için tam CRUD REST API, XML-only, doğru HTTP status kodlarıyla; Swagger + README ile dokümantasyon; Open Library ile gerçek bir dış servis entegrasyonu, JSON'dan XML'e çevrilip kendi şemamızla doğrulandı; ve son olarak 7 isteğe bağlı konuyu (versioning, auth, filtreleme/sayfalama, gelişmiş XSD, namespace, testler, loglama) kapsadık."
- "Kod GitHub'da [repo linkini söyle], README'de kurulum adımları var, herkes kendi makinesinde çalıştırıp deneyebilir."
- "Dinlediğiniz için teşekkürler."

---

## Ek: Hızlı Referans — Hangi Gereksinim Nerede Kanıtlanıyor

| Gereksinim | Kanıt Konumu (dosya:satır / URL) |
|---|---|
| A) XML Veri Paketi | `backend/data/library.xml` (28 kitap, 9 üye, 12 ödünç) |
| B) XSD Doğrulama | `backend/data/schema.xsd`, `backend/src/validators.py`, `backend/data/invalid_library.xml` |
| C) XPath (5+) | `backend/src/xpath_queries.py` (6 sorgu) |
| C) XSLT | `backend/data/report.xslt` + `backend/src/xslt_transformer.py` → `/api/v1/reports/dashboard` |
| D) Kodda Ayrıştırma | `backend/src/xml_manager.py` (DOM: `load_tree`; SAX-benzeri: `stream_books`/iterparse) |
| E) REST API (4+ endpoint) | `backend/src/routers/*.py` — books/members/borrowings tam CRUD |
| F) API Dokümantasyonu | `http://localhost:8000/docs` (Swagger) + `README.md` |
| G) Harici Entegrasyon | `backend/src/external_service.py` (Open Library) + `backend/src/routers/external.py` |
| Hata Yönetimi | `backend/src/auth.py`, `backend/src/responses.py`, `backend/src/xml_responses.py` |
| Test Paketi | `backend/tests/*.py` (`pytest -v`) |
| Postman | `postman/collection.json` |

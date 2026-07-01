# Video Sunum Konuşma Metni — XML Library Management System

> **Ders:** 155-8056 XML ve Web Servisleri (Mersin Üniversitesi)
> **Proje:** XML-Based Library Management System
> **Stack:** Backend = Python + FastAPI + lxml | Frontend = Next.js + React | Veri = `backend/data/library.xml`
> **Bu dosyanın amacı:** Kayda başlamadan önce elinde tutacağın konuşma metni. Burada anlatım tarzı "şu maddeyi karşılıyoruz" şeklinde değil, **projeni birine tanıtıyormuş gibi, doğal bir sohbet akışında**. Sen kod tabanını gezdiriyorsun, karşındaki kişi de merak ediyor: "bu neden böyle, şurada ne oluyor" diye. Yine de arka planda, her fonksiyona, her satıra değinerek gidiyoruz — hiçbir kod parçası atlanmıyor, sadece "bak bu ödev maddesini karşılıyor" cümlesi kurmuyoruz, onun yerine "bunu şunun için yaptık" diyoruz.

---

## 0) Kayıttan Önce Hazırlık (Checklist)

**Terminaller (2 adet):**
1. Terminal A → `backend` klasöründe, venv aktif, `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` çalışır durumda.
2. Terminal B → `backend` klasöründe, venv aktif, boşta — komutları burada çalıştıracaksın (pytest, python -c, curl).

**Tarayıcı sekmeleri (sırayla):**
1. `http://localhost:8000/docs` — Swagger UI
2. `http://localhost:8000/api/v1/reports/dashboard` — XSLT HTML raporu
3. `http://localhost:3000` — Next.js frontend
4. Postman (koleksiyon `postman/collection.json` import edilmiş, `baseUrl = http://localhost:8000` değişkeni tanımlı)

**Editör (VS Code vb.):** Proje kökü açık, şu dosyalar sekmede hazır bekletilebilir: `README.md`, `backend/data/schema.xsd`, `backend/data/library.xml`, `backend/data/invalid_library.xml`, `backend/data/report.xslt`, `backend/src/xml_manager.py`, `backend/src/validators.py`, `backend/src/xpath_queries.py`, `backend/src/xslt_transformer.py`, `backend/src/external_service.py`, `backend/src/routers/books.py`.

**Konuşma tarzı:** Bir arkadaşına ya da bir işverene projeni gösteriyormuş gibi düşün. "Bak burada şunu yaptım çünkü..." tarzı doğal cümleler kur. Teknik terimler İngilizce kalabilir (endpoint, payload, schema gibi). Zaman zaman "şimdi ilginç kısma geliyoruz" ya da "burada biraz kafa patlattım" gibi doğal geçiş cümleleri kullan — bu bir sunum, ezber okuma değil.

---

## Zaman Planı (toplam ~2 saat, minimum 1 saat şartını rahatça karşılar)

| # | Bölüm | Süre | Kümülatif |
|---|-------|------|-----------|
| 0 | Açılış — Projeyi Tanıtalım | 5 dk | 0:00–0:05 |
| 1 | Veri Modelimiz: library.xml | 10 dk | 0:05–0:15 |
| 2 | Kayıttan Önce Kontrol: XSD Şema Doğrulama | 12 dk | 0:15–0:27 |
| 3 | Veride Arama Yapmak: XPath Sorguları | 10 dk | 0:27–0:37 |
| 4 | Ham XML'den Rapora: XSLT Dönüşümü | 8 dk | 0:37–0:45 |
| 5 | Kod Tarafında XML'i İşlemek: DOM + iterparse | 12 dk | 0:45–0:57 |
| 6 | Her Şeyi Bir Araya Getiren REST API | 20 dk | 0:57–1:17 |
| 7 | API'yi Nasıl Belgeledik | 6 dk | 1:17–1:23 |
| 8 | Dışarıya Açılmak: Open Library Entegrasyonu | 10 dk | 1:23–1:33 |
| 9 | Küçük Ama Önemli Detaylar: Kalite ve Hata Yönetimi | 6 dk | 1:33–1:39 |
| 10 | Üstüne Kattığımız Ekstralar | 10 dk | 1:39–1:49 |
| 11 | Hadi Bozalım: Canlı Hata Senaryoları | 8 dk | 1:49–1:57 |
| 12 | Kapanış | 3 dk | 1:57–2:00 |

Bu süreler planlama amaçlı — doğal konuşurken uzaması gayet normal ve iyi bir şey.

---

# BÖLÜM 0 — Açılış: Projeyi Tanıtalım (0:00–0:05)

🖥️ **EKRANDA GÖSTER:** VS Code'da proje kök klasörü (Explorer paneli açık, `backend/` ve `frontend/` klasörleri görünür).

🎙️ **ANLAT:**
- "Merhaba, ben bu videoda size bir kütüphane yönetim sistemi göstereceğim. Ama şunu baştan söyleyeyim: kütüphane burada bir bahane, asıl amaç XML dünyasının uçtan uca nasıl kullanıldığını göstermek — XML veri üretmekten tutun, o veriyi bir şema ile doğrulamaya, içinde arama yapıp raporlara dönüştürmeye, kodda okuyup işlemeye, ve en sonunda bunların hepsini bir web servisi üzerinden dışarıya açmaya kadar."
- "Şurada tipik bir projede veritabanı görürdünüz — MySQL, Postgres falan. Ben burada bilinçli olarak veritabanı kullanmadım. Neden? Çünkü veritabanı kullansaydım XML sadece bir taşıma formatına dönerdi, asıl mantık SQL'de yaşardı. Ben istedim ki XML gerçekten **kalıcı veri kaynağı** olsun — yani `library.xml` dosyası bizim veritabanımız. Bu da demek oluyor ki DOM ile okuma/yazma, şema doğrulama gibi konular gösteri amaçlı değil, gerçekten zorunlu."
- "Mimari şöyle işliyor: kullanıcı tarafında bir Next.js arayüzü var, o `Accept: application/xml` header'ıyla FastAPI backend'ime istek atıyor, backend gelen isteği bir `XmlManager` sınıfına devrediyor, her yazma işleminden önce şemaya karşı doğruluyor, ve sonunda `library.xml` dosyasına yazıyor."

🖥️ **EKRANDA GÖSTER:** `README.md` dosyasını aç, üst kısımdaki "Project Structure" ağacını göster.

🎙️ **ANLAT:** "Klasör yapısına hızlıca bakalım: `backend/data` içinde veri, şema ve dönüşüm dosyalarım var; `backend/src` uygulama kodu; `backend/src/routers` altında endpoint'lerim; `backend/tests`'te testlerim; `frontend/` React tarafı; `postman/` de hazır bir Postman koleksiyonu. Şimdi baştan başlayıp gezelim."

---

# BÖLÜM 1 — Veri Modelimiz: library.xml (0:05–0:15)

🎙️ **ANLAT (giriş):** "Her şeyden önce elimde ne var, ona bakalım — çünkü geri kalan her şey bu dosyanın üzerine kurulu."

🖥️ **EKRANDA GÖSTER:** `backend/data/library.xml` dosyasını aç, en üstten başla (satır 1-30).

🎙️ **ANLAT:**
- "Kök elemanım `<library id=\"lib-001\" name=\"Mersin University Digital Library\">`. Dikkatinizi çekeyim, `id` attribute'u var — bunu birazdan XSD tarafında `xs:ID` olarak tanımlayacağız, yani her ID benzersiz olmak zorunda."
- "İçinde üç ana bölüm var: `<books>`, `<members>`, `<borrowings>`. Yani kütüphanede kitaplar, üyeler, ve ödünç kayıtları — klasik bir kütüphane otomasyonu senaryosu. `books` içinde bir sürü `<book>` var, her `book`'un `title`, `author`, `publisher`, `categories` (bu da kendi içinde birden fazla `<category>` barındırabiliyor, yani çok seviyeli iç içe geçmiş bir yapı), `publicationYear`, `availableCopies`, isteğe bağlı `description`'ı var."
- "ID ve referans mantığına gelirsek: her kitabın `id=\"bk-XXX\"`, her üyenin `id=\"mem-XXX\"`, her ödünç kaydının `id=\"brw-XXX\"` şeklinde bir kimliği var. Ödünç kayıtları da `bookRef` ve `memberRef` attribute'larıyla ilgili kitaba ve üyeye **referans** veriyor — bir nevi foreign key mantığı, birazdan XSD'de `IDREF` ile bunu nasıl garanti altına aldığımı göstereceğim."
- "Bir de etiket isimlendirmesine dikkat edin: hepsi camelCase — `publicationYear`, `availableCopies`, `membershipType`, `bookRef`. Bilerek tutarlı tuttum, yarısı camelCase yarısı snake_case olursa okumak da işlemek de zorlaşıyor."

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

🎙️ **ANLAT çıktı üzerinden:** "28 kitap, 9 üye, 12 ödünç kaydı — toplam 49 kayıt. Ama sayı önemli değil aslında, önemli olan çeşitlilik: 28 kitap 8 farklı kategoriye dağılmış (Sci-Fi, Fantasy, History, Mystery, Romance, Technology, Biography, Classic), 12 ödünç kaydının 7'si aktif, 2'si gecikmiş, 3'ü iade edilmiş. Bu çeşitliliği bilerek kurdum, çünkü birazdan XPath sorgularında ve raporlarda bu farklı durumları kullanacağım."

🖥️ **EKRANDA GÖSTER:** `backend/data/library.xml` içinde bir `<borrowing>` kaydına scroll et (örn. `brw-001`).

🎙️ **ANLAT:** "İşte burada `bookRef` ve `memberRef` değerlerinin gerçek kitap/üye ID'lerine karşılık geldiğini görüyorsunuz — bu tutarlı referans sayesinde XPath'te 'bu ödünç kaydı hangi kitaba ait, kim almış' diye bir join benzeri sorgu yazabiliyorum."

🖥️ **EKRANDA GÖSTER:** `backend/data/invalid_library.xml` dosyasını kısaca aç, üstteki yorum bloğunu (satır 2-11) göster.

🎙️ **ANLAT:** "Bu dosyayı bilerek bozuk hazırladım, XSD doğrulamayı gösterirken lazım olacak — birazdan detaylı geliyoruz."

---

# BÖLÜM 2 — Kayıttan Önce Kontrol: XSD Şema Doğrulama (0:15–0:27)

🎙️ **ANLAT (giriş):** "Şimdi ilginç kısma geldik. Veritabanı olmadığı için, birinin `library.xml` dosyasına elle ya da API üzerinden saçma sapan bir şey yazmasını nasıl engelliyorum? İşte burada XSD devreye giriyor — XML için bir kural kitabı gibi düşünün."

🖥️ **EKRANDA GÖSTER:** `backend/data/schema.xsd` dosyasını aç, en baştan başla.

🎙️ **ANLAT satır satır:**
- Satır 6-10 (`isbnType`): "ISBN için kendi tipimi tanımladım, `xs:pattern` ile bir regex kısıtı koydum: `978-[0-9]{1,5}-[0-9]{1,7}-[0-9]{1,7}-[0-9]`. Yani biri ISBN'i `978-` ile başlatmazsa ya da format tutmazsa, şema bunu reddediyor."
- Satır 12-23 (`genreType`): "Kategoriler için `xs:enumeration` kullandım, sadece şu sekiz değere izin veriyorum: Sci-Fi, Fantasy, History, Mystery, Romance, Technology, Biography, Classic. Biri 'Horror' yazarsa şema patlıyor — birazdan canlı göstereceğim."
- Satır 25-29 (`emailType`): "E-posta için de bir pattern var, `@` işareti ve domain zorunlu."
- Satır 53-65 (`bookType`): "Burada `xs:sequence` ile elemanların **sırasını** da sabitliyorum — title, author, publisher, categories, publicationYear, availableCopies bu sırayla gelmek zorunda. `id` attribute'u `xs:ID` tipinde ve zorunlu, `isbn` de yukarıdaki `isbnType` ile kısıtlı ve zorunlu."
- Satır 90-100 (`borrowingType`): "Ve işte az önce bahsettiğim IDREF — `bookRef` ve `memberRef` attribute'ları `xs:IDREF` tipinde tanımlı. Bunun anlamı şu: bu değerlerin dokümanda gerçekten var olan bir ID'ye işaret etmesi lazım. Olmayan bir kitaba referans verirsen şema bunu da yakalıyor. XML'in bence en güçlü taraflarından biri bu, JSON'da bu kadar doğal bir karşılığı yok."

🖥️ **EKRANDA GÖSTER:** `backend/src/validators.py` dosyasını aç.

🎙️ **ANLAT satır satır:**
- Satır 19-21 (`_load_schema`): "`lxml.etree` ile `schema.xsd`'yi okuyup bir `XMLSchema` nesnesi kuruyorum."
- Satır 24-31 (`get_schema`): "Şemayı her istekte yeniden parse etmeyeyim diye basit bir cache yaptım — bir kere yüklenip `_SCHEMA` değişkeninde tutuluyor."
- Satır 34-65 (`validate_xml`): "Bu fonksiyon esnek, dosya yolu da alır, bytes de, string de, hazır bir Element de. `schema.validate(element)` `True`/`False` döner; yanlışsa `schema.error_log`'da satır satır hangi kuralın neden ihlal edildiğini gösteren bir log var. `except etree.XMLSyntaxError` ile ayrıca XML bile olmayan (yani bozuk/malformed) veriyi de ayrı yakalıyorum — bu ikisini birbirinden ayırmak önemli: biri 'bu geçerli bir XML ama kurallara uymuyor', diğeri 'bu zaten XML değil'."
- Satır 67-70 (`validate_or_raise`): "Bunu yazma işlemlerinde kullanıyorum — geçersizse `ValidationError` fırlatıyor, router bunu yakalayıp uygun bir hata döndürüyor."
- Satır 73-84 (`validate_file_pair`): "Bu da bir gösteri fonksiyonu — hem geçerli hem geçersiz dosyayı aynı anda doğrulayıp sonucu birlikte döndürüyor, birazdan kullanacağım."

🖥️ **EKRANDA GÖSTER:** Terminal B.

💻 **ÇALIŞTIR — Önce sağlıklı dosya:**
```bash
cd backend
python3 -c "from src.validators import validate_xml; from src.config import LIBRARY_XML; ok, log = validate_xml(LIBRARY_XML); print('VALID:', ok); print('LOG:', log or '(boş — hata yok)')"
```
🎙️ **ANLAT:** "`VALID: True`, log boş. `library.xml` şemaya tamamen uyuyor."

💻 **ÇALIŞTIR — Şimdi bozuk dosya:**
```bash
python3 -c "from src.validators import validate_xml; from src.config import INVALID_LIBRARY_XML; ok, log = validate_xml(INVALID_LIBRARY_XML); print('VALID:', ok); print('LOG:'); print(log)"
```
🎙️ **ANLAT — gerçek çıktı bu, ekrandakini oku:**
```
16:0: Element 'book', attribute 'isbn': [facet 'pattern'] The value 'NOT-A-VALID-ISBN' is not accepted by the pattern '978-[0-9]{1,5}-[0-9]{1,7}-[0-9]{1,7}-[0-9]'.
21:0: Element 'category': [facet 'enumeration'] The value 'Horror' is not an element of the set {'Sci-Fi', 'Fantasy', ...}.
24:0: Element 'availableCopies': '-5' is not a valid value of the atomic type 'xs:nonNegativeInteger'.
26:0: Element 'book', attribute 'id': 'bk-dup' is not a valid value of the atomic type 'xs:ID'.
41:0: Element 'email': [facet 'pattern'] The value 'not-an-email' is not accepted by the pattern '...'.
42:0: Element 'membershipType': [facet 'enumeration'] The value 'vip' is not an element of the set {'student', 'faculty', 'public'}.
50:0: Element 'status': [facet 'enumeration'] The value 'cancelled' is not an element of the set {'active', 'returned', 'overdue'}.
```
"Bakın burada tek bir dosyaya bilerek yedi farklı hata sıkıştırdım: ISBN formatı bozuk, kategori enum dışı ('Horror'), kopya sayısı negatif, aynı ID iki kere kullanılmış, e-posta formatı bozuk, üyelik tipi enum dışı ('vip'), ödünç durumu enum dışı ('cancelled'). Yani sadece 'çalışıyor' demiyorum, gerçekten farklı hata türlerini tek tek tetikleyip gösterebiliyorum."

🎙️ **Küçük bir dürüstlük notu (isterseniz atlayın, isterseniz söyleyin):** "Dosyada ayrıca `bookRef=\"bk-missing\"` diye olmayan bir kitaba referans da var — kavramsal olarak IDREF ihlali. Ama bu çalıştırmada ayrı bir satır olarak logda görünmüyor, çünkü `bk-dup` zaten ID tablosunu bozduğu için validator oraya kadar gitmiyor. Yine de `schema.xsd`'de `bookRef`/`memberRef`'in `xs:IDREF` tipinde tanımlı olduğunu gösterip konsepti anlatmak yeterli."

🖥️ **EKRANDA GÖSTER (opsiyonel, hızlıca):** Terminal A'daki uvicorn başlangıç loglarını göster.

🎙️ **ANLAT:** "Bir de şunu göstereyim — sunucu her ayağa kalktığında bu doğrulamayı otomatik çalıştırıyorum, `main.py`'deki `lifespan` fonksiyonunda. Loglara bakarsanız `library.xml validation: PASS` yazıyor — yani sunucu açılır açılmaz kendi verisini kontrol ediyor, sessizce bozuk veriyle ayağa kalkmıyor."

---

# BÖLÜM 3 — Veride Arama Yapmak: XPath Sorguları (0:27–0:37)

🎙️ **ANLAT (giriş):** "XML'i doğruladık, şimdi içinde nasıl gezinip arama yapıyorum ona bakalım. Burada kullandığım dil XPath — XML'in kendi sorgu dili, SQL'deki SELECT'e benzetebilirsiniz."

🖥️ **EKRANDA GÖSTER:** `backend/src/xpath_queries.py` dosyasını aç, en baştan başla.

🎙️ **ANLAT her sorguyu satır satır, doğal bir "bak burada şunu yapıyorum" tonuyla:**

1. **Satır 12-25 — `query_scifi_books_by_author`:**
   `/library/books/book[categories/category='Sci-Fi']`
   "İlk sorguda predicate kullanıyorum — köşeli parantez içindeki koşul, `categories/category`'nin 'Sci-Fi' olmasını istiyor. Bunu neden yazdım? Çünkü kütüphanede en sık ihtiyaç duyulan şeylerden biri türe göre filtreleme, bunu Python'da elle liste gezip if yazmak yerine doğrudan XPath'e bıraktım — hem kod daha kısa hem de XML motoru zaten bunun için optimize."

2. **Satır 28-41 — `query_category_counts`:**
   `count(/library/books/book[categories/category='...'])`
   "Burada XPath'in `count()` fonksiyonunu kullanıyorum — her kategoride kaç kitap var, bunu XPath'in kendisi sayıyor, ben sayaç tutmuyorum. Dashboard raporunda kategori dağılımı lazım olduğunda tek satırda çözülüyor."

3. **Satır 44-54 — `query_title_search`:**
   `contains(translate(title, 'ABC...', 'abc...'), 'keyword')`
   "Burada `contains()` ile alt string arıyorum ama önce `translate()` ile büyük harfleri küçüğe çeviriyorum. Neden bu kadar dolambaçlı? Çünkü XPath 1.0'da doğrudan bir `lower-case()` fonksiyonu yok, bu yüzden harf harf eşleme yaparak case-insensitive arama simüle ediyorum. Kullanıcı 'dune' yazınca 'Dune' başlığını da bulsun istiyorum."

4. **Satır 57-78 — `query_active_borrowed_books`:**
   "Bu biraz daha karmaşık — önce aktif ödünç kayıtlarını buluyorum, sonra her kaydın `bookRef`/`memberRef` değerini alıp **ayrı bir XPath sorgusuyla** gerçek kitap/üye kaydına ulaşıyorum. Yani IDREF ilişkisini elle 'join' gibi çözüyorum — ilişkisel veritabanındaki foreign key JOIN'in burada XPath karşılığı."

5. **Satır 81-95 — `query_publisher_books_after_year`:**
   `book[publisher='X' and publicationYear > Y]`
   "Burada iki koşulu `and` ile birleştiriyorum, `publicationYear > Y` ile de sayısal karşılaştırma yapıyorum, metin karşılaştırması değil. 'Şu yayınevinin şu yıldan sonraki kitapları' gibi gerçek dünyadan bir sorgu örneği."

6. **Satır 98-114 — `query_overdue_borrowings`:** "Son olarak gecikmiş kayıtları buluyorum, aynı IDREF çözme mantığını burada da kullanıyorum."

🎙️ **ANLAT (özet):** "Toplamda altı sorgu yazdım, hepsi predicate, fonksiyon ya da çok koşullu — 'tüm kitapları getir' gibi basit bir şey değil, gerçek senaryolar."

💻 **ÇALIŞTIR (Terminal B):**
```bash
python3 -c "from src.xpath_queries import run_all_queries; import json; print(json.dumps(run_all_queries(), indent=2, ensure_ascii=False))"
```
🎙️ **ANLAT çıktı üzerinden:** Her sorgu grubundan 1-2 sonucu göster, biraz önce anlattığın mantıkla eşleştir.

🖥️ **EKRANDA GÖSTER:** Tarayıcıda `http://localhost:8000/api/v1/reports/xpath` adresini aç.

🎙️ **ANLAT:** "`backend/src/routers/reports.py` satır 21-39'daki `xpath_demo` endpoint'i bu sorguların hepsini çalıştırıp sonucu dinamik bir `<xpathResults>` XML ağacına döküyor — yani bu sorguları sadece Python konsolunda değil, tarayıcıda da XML olarak görebiliyorsunuz."

---

# BÖLÜM 4 — Ham XML'den Rapora: XSLT Dönüşümü (0:37–0:45)

🎙️ **ANLAT (giriş):** "Ham XML dosyasını birine göstermek pek etkileyici değil, kabul edelim. Onun yerine XSLT ile bunu otomatik bir HTML raporuna çeviriyorum."

🖥️ **EKRANDA GÖSTER:** `backend/data/report.xslt` dosyasını aç.

🎙️ **ANLAT satır satır:**
- Satır 2-5: "`xsl:stylesheet` kök elemanı, XSL namespace'i tanımlı, çıktının HTML olacağını `xsl:output method=\"html\"` ile belirtiyorum."
- Satır 7: "`xsl:template match=\"/\"` — dokümanın kökünden başlayan ana şablon, klasik XSLT girişi."
- Satır 43: `<xsl:value-of select="/library/@name"/>` — "Kütüphanenin adını doğrudan `library` elemanının `name` attribute'undan XPath'le çekiyorum. XSLT'nin içinde her yerde XPath var, ikisi ayrılmaz."
- Satır 47-72 (istatistik kartları): "Her kartta bir `count()` ya da `sum()` çağrısı var — toplam kitap, üye, aktif/gecikmiş ödünç sayısı, Sci-Fi kitap sayısı, ve `sum(/library/books/book/availableCopies)` ile toplam mevcut kopya sayısı. Ham veriyi göstermek yerine, aynı veriden otomatik üretilmiş özet rakamlar çok daha çarpıcı."
- Satır 88-89: `<xsl:for-each select="/library/books/book"><xsl:sort select="title"/>` — "Tüm kitapları geziyorum, `xsl:sort` ile başlığa göre alfabetik sıralıyorum. Yani sıralama işini de XSLT'ye yaptırıyorum."
- Satır 121-143 (borrowings tablosu): "Burada işin biraz eğlenceli tarafı — `current()` fonksiyonu. `for-each` içinde gezerken 'şu an baktığım borrowing elemanı' anlamına geliyor, satır 125 ve 128'de `current()/@bookRef` ile o kaydın kitap referansını alıp `/library/books/book[@id=current()/@bookRef]/title` diyerek **başka bir ağaçtaki** kitabın başlığına ulaşıyorum. Yine aynı IDREF çözme mantığı, ama bu sefer XSLT içinde."
- Satır 136-138: `<xsl:attribute name="class">status-<xsl:value-of select="status"/></xsl:attribute>` — "Burada dinamik olarak bir HTML class ismi üretiyorum — `status-active`, `status-overdue` gibi — böylece CSS ile renklendirebiliyorum. XSLT sadece metin değil, attribute de üretebiliyor."

🖥️ **EKRANDA GÖSTER:** `backend/src/xslt_transformer.py` dosyasını aç (14 satır, tamamı).

🎙️ **ANLAT:** "Kod tarafı çok kısa aslında — `etree.parse` ile hem `library.xml`'i hem `report.xslt`'yi okuyorum, `etree.XSLT(xslt_doc)` ile bir dönüştürücü kuruyorum, `transform(xml_doc)` çağrısı gerçek bir XSLT 1.0 motorunu (lxml'in altındaki libxslt) çalıştırıp sonucu üretiyor. Elle string birleştirmiyorum, gerçek bir XSLT processor kullanıyorum."

🖥️ **EKRANDA GÖSTER:** Tarayıcı sekmesi 2 → `http://localhost:8000/api/v1/reports/dashboard`

🎙️ **ANLAT:** Sayfayı yukarıdan aşağı gez. "İşte bu — istatistik kartları, alfabetik sıralı kitap tablosu, aktif/gecikmiş ödünç tablosu (kitap adı ve üye adı XSLT içinde çözüldü), üye tablosu. Hiçbirini elle yazmadım, hepsi `library.xml`'den `report.xslt` ile otomatik üretildi."

---

# BÖLÜM 5 — Kod Tarafında XML'i İşlemek: DOM + iterparse (0:45–0:57)

🎙️ **ANLAT (giriş):** "Şimdi işin motor kısmına geçelim — XML'i kodda nasıl okuyup değiştiriyorum, nasıl yeni kayıt ekliyorum, hatalı girdi gelirse ne oluyor. Burada iki farklı teknik kullandım: `lxml.etree` ile klasik **DOM** (tüm dosyayı belleğe yükleyip gezmek) ve `lxml.etree.iterparse` ile **SAX benzeri streaming** okuma. İkisini de göstereceğim, ne zaman hangisini kullandığımı da anlatacağım."

🖥️ **EKRANDA GÖSTER:** `backend/src/xml_manager.py` dosyasını aç, en baştan.

## 5.1 DOM ile Okuma

🎙️ **ANLAT satır satır:**
- Satır 37-42 (`load_tree`, `get_root`): "`etree.parse(path)` tüm dosyayı belleğe yükleyip bir ağaç döndürüyor — klasik DOM. Küçük/orta boy dosyalar için gayet pratik, çünkü ağaç üzerinde hem XPath çalıştırabiliyorum hem de elemanları taşıyıp değiştirebiliyorum."
- Satır 76-102 (`get_all_books`): "DOM'u yükledikten sonra XPath ile filtreleyip `copy.deepcopy` ile elemanları kopyalıyorum. Deepcopy'yi bilerek yapıyorum, çünkü orijinal ağaçtan koparmazsam sonra o elemanı başka bir XML'e eklemeye çalıştığımda lxml hata veriyor — bir eleman aynı anda iki ağaçta olamıyor."

## 5.2 Veriyi Değiştirmek

🖥️ **EKRANDA GÖSTER:** Satır 241-259 (`add_book`).

🎙️ **ANLAT:**
- "Önce `books` container'ını buluyorum, ID verilmemişse `_next_book_id` ile otomatik üretiyorum — satır 188-200'de mevcut ID'lerin sayısal kısmını parse edip en büyüğüne bir ekliyorum, `bk-029` gibi çıkıyor."
- "Satır 253'te duplicate ID kontrolü var — aynı ID zaten varsa hata fırlatıyorum. Bunu sadece XSD'ye bırakmıyorum, kod seviyesinde de kontrol ediyorum çünkü hata mesajını daha erken ve daha anlamlı verebiliyorum."
- "`validate_or_raise(book_element)` ile yazmadan önce yeni elemanı tek başına şemaya karşı doğruluyorum, sonra `books_container.append(book_element)` ile DOM ağacına ekliyorum."
- "En sonda `self._save_tree(tree)` çağrılıyor — bu fonksiyon satır 178-186'da tanımlı ve ilginç bir şey yapıyor: **tekrar** tüm dokümanı `validate_or_raise` ile doğruluyor, yani hem tek eleman bazında hem tüm doküman bazında çift kontrol var. Sonra `tree.write(...)`'ı `pretty_print=True, xml_declaration=True, encoding='UTF-8'` ile diske yazıyor. Çift doğrulamanın sebebi şu: tek eleman şemaya uysa bile, mesela IDREF bütünlüğü ancak tüm doküman bağlamında anlaşılabilir."

🖥️ **EKRANDA GÖSTER:** Satır 390-450 (`checkout_book`) — projenin en karmaşık iş mantığı burada.

🎙️ **ANLAT:** "Bu fonksiyon sadece XML yazmıyor, gerçek bir iş akışı yönetiyor: önce kitabın `availableCopies`'ini okuyup sıfırdan büyük mü diye bakıyor (satır 413-416), sonra üyenin tipine göre (`library_rules.py`'deki `loan_limit`) kaç aktif ödünç kaydı olduğunu kontrol ediyor (417-424), varsayılan iade tarihini üyelik tipine göre hesaplıyor. En ilginç kısmı satır 439-445 — yeni `<borrowing>` elemanını `etree.Element`/`etree.SubElement` ile **XSD'nin istediği sırada** (`borrowDate, dueDate, status`) sıfırdan kuruyorum. Bunu bilerek böyle yaptım çünkü `xs:sequence` sıra zorunluluğu koyuyor; elemanları rastgele sırada eklersem doğrulama patlıyor."

## 5.3 Hatalı Girdi Geldiğinde

🖥️ **EKRANDA GÖSTER:** Satır 297-310 (`parse_book_xml`).

🎙️ **ANLAT:** "`etree.fromstring(xml_bytes)` çağrısını `try/except etree.XMLSyntaxError` ile sarıyorum — yani gelen veri XML bile değilse (mesela bir etiket kapatılmamışsa) burada yakalanıp anlamlı bir hataya çevriliyor, ham bir exception dışarı sızmıyor. Kök eleman `book` değilse ama içinde bir `<book>` varsa onu buluyorum, hiçbiri yoksa da hata veriyorum — esnek ama güvenli."

## 5.4 Büyük Dosyalar İçin: Streaming (iterparse)

🖥️ **EKRANDA GÖSTER:** Satır 46-72 (`stream_books`, `count_books_streaming`).

🎙️ **ANLAT:**
- "`etree.iterparse(path, events=('end',), tag='book')` — DOM'un aksine dosyanın tamamını belleğe yüklemiyor, baştan sona **event-based** tarıyor, her `</book>` kapanışına geldiğinde bir event üretiyor. Bu, SAX'ın (Simple API for XML) event-driven modeline çok benziyor, lxml bunu iterparse ile sunuyor."
- "Her event'te veriyi çekiyorum (satır 57-65), sonra kritik bir şey yapıyorum: satır 66-68'de `elem.clear()` ile o elemanın içeriğini bellekten siliyorum, önceki kardeş elemanları da temizliyorum. Bunu yapmazsam iterparse arka planda yine bir ağaç kurar ve bellek avantajını kaybederim. Bu sayede çok büyük dosyalarda bile sabit bellek kullanımıyla çalışabiliyorum."
- "`count_books_streaming` bunun pratik kullanımı — DOM ağacı hiç kurmadan sadece kitap sayısını sayıyor."

🖥️ **EKRANDA GÖSTER:** Terminal A'daki uvicorn başlangıç loglarını göster (`Streaming book count via iterparse: 28` satırı).

🎙️ **ANLAT:** "Sunucu her açıldığında bu streaming sayaç çalışıyor. DOM ile de aynı sonucu alabilirdim ama bilerek farklı bir tekniği gerçek bir işlevde kullanmak istedim, sadece akademik gösteri olmasın diye."

💻 **ÇALIŞTIR (opsiyonel, karşılaştırma için, Terminal B):**
```bash
python3 -c "
from src.xml_manager import XmlManager
m = XmlManager()
print('DOM ile sayım :', len(m.get_root().findall('.//book')))
print('iterparse ile :', m.count_books_streaming())
"
```
🎙️ **ANLAT:** "İki farklı teknik, aynı sonuç, farklı bellek profili — DOM tüm ağacı tutar, rastgele erişim ve değişiklik kolaydır; iterparse tek geçişte akar, bellek dostu, sadece okuma için ideal."

---

# BÖLÜM 6 — Her Şeyi Bir Araya Getiren REST API (0:57–1:17)

🎙️ **ANLAT (giriş):** "Şimdiye kadar gördüğümüz her şey — doğrulama, XPath, XSLT, DOM/iterparse — bir REST API'nin arkasında toplanıyor. Üç kaynağım var: kitaplar, üyeler, ödünç kayıtları, üçü için de tam CRUD var. API tamamen XML odaklı — JSON yok, her şey `application/xml`."

🖥️ **EKRANDA GÖSTER:** `backend/src/main.py` satır 59-64.

🎙️ **ANLAT:** "`/api/v1` önekiyle beş router topluyorum: books, members, borrowings, reports, external. Bu önek aynı zamanda API'ye bir versiyon numarası veriyor — ileride `/v2` çıkarsam eski istemciler kırılmaz."

## 6.1 İçeri Girmeden Önce: Content Negotiation & Auth

🖥️ **EKRANDA GÖSTER:** `backend/src/auth.py` (tamamı, 26 satır).

🎙️ **ANLAT:**
- "`require_xml_accept` (satır 23-26): İstek `Accept` header'ında `application/xml` yoksa (ve `*/*` de değilse) 406 döndürüyorum — yani API'm sadece XML konuşacağını baştan söylüyor."
- "`require_api_key` (satır 17-20): `X-API-Key` header'ını sabit bir anahtarla karşılaştırıyor, uymazsa 401. FastAPI'nin `Depends()` mekanizmasıyla bunu POST/PUT/DELETE endpoint'lerine ekliyorum — GET'lerde auth istemiyorum, herkes okuyabilsin, ama yazma işlemleri korumalı."

## 6.2 Books Router — Baştan Sona Bir CRUD

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/books.py` (tamamı, 88 satır) — satır satır ilerle.

🎙️ **ANLAT:**
- **GET liste (satır 16-30):** "`genre`, `search`, `page`, `limit` diye dört query parametresi alıyorum — filtreleme, arama, sayfalama hepsi burada. Response header'larına da `X-Total-Count`, `X-Page`, `X-Limit` ekliyorum, böylece istemci toplam kayıt sayısını body'yi parse etmeden de öğrenebiliyor."
- **GET tekil (satır 33-39):** "`try/except BookNotFoundError` ile 404'ü XML formatında dönüyorum, hiçbir zaman çıplak 500 patlamıyor."
- **POST (satır 42-55):** "Önce body boş mu diye bakıyorum. `parse_book_xml` ile ayrıştırıyorum — burada malformed XML hatası çıkabilir. `add_book` da hem duplicate ID hem şema hatası fırlatabilir, ikisini ayrı yakalayıp uygun mesajla dönüyorum. Başarılıysa 201 Created — doğru HTTP status kodunu kullanmaya özen gösterdim."
- **PUT (satır 58-73):** "Aynı desen tekrar ediyor — ayrıştır, güncelle, 404/400 hata yönetimi."
- **DELETE (satır 76-87):** "`delete_book` çağrılıyor, ve `xml_manager.py` satır 280-295'te gördüğümüz gibi eğer o kitabın aktif ya da gecikmiş bir ödünç kaydı varsa silmeyi engelliyorum — referential integrity'yi sadece şemaya değil koda da yediriyorum."

🖥️ **EKRANDA GÖSTER:** `backend/src/xml_responses.py` (tamamı, 42 satır).

🎙️ **ANLAT:** "`books_collection_xml` gibi yardımcı fonksiyonlar `<books count=\"10\" totalCount=\"28\">` şeklinde bir wrapper kurup içine gerçek `book` elemanlarını dolduruyor, `element_to_bytes` de XML declaration'lı, düzgün girintili bytes üretiyor. Tüm response'larım bu ortak fonksiyonlardan geçiyor, böylece format her yerde tutarlı kalıyor."

## 6.3 Members & Borrowings — Tekrar Etmiyorum Ama Farkları Söyleyeyim

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/members.py`, sonra `borrowings.py`.

🎙️ **ANLAT:** "Members router aynı CRUD desenini izliyor, tek farkı: silmeden önce aktif ödünç kontrolü (satır 357-374, xml_manager.py) ve e-posta benzersizlik kontrolü var (`_ensure_unique_email`, satır 216-223). Borrowings router'da ise iki özel endpoint var: `POST /borrowings` ile **checkout** yapıyorum — az önce Bölüm 5'te detaylı anlattığım `checkout_book` fonksiyonunu çağırıyor — ve `PUT /borrowings/{id}/return` ile **iade** alıyorum, `return_book` fonksiyonu kitabın kopya sayısını artırıp iade tarihini ekliyor, durumu 'returned' yapıyor. `DELETE /borrowings/{id}` de sadece iade edilmiş kayıtları silmeye izin veriyor — aktif bir kaydı silmek denetim izini bozar diye bilerek yasakladım."

## 6.4 Şimdi Canlı Deneyelim

🖥️ **EKRANDA GÖSTER:** Tarayıcı sekmesi 1 → `http://localhost:8000/docs`

🎙️ **ANLAT + göster:**
1. `GET /api/v1/books` endpoint'ini aç, "Try it out" → `genre=Sci-Fi` gir → Execute. "Bakın, dönen response'un `Content-Type`'ı `application/xml`, tam istediğim gibi."
2. `GET /api/v1/books/bk-001` ile tekil kayıt göster.
3. `POST /api/v1/books` ile örnek bir kitap ekle:
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
   `X-API-Key: library-api-key-dev-2026` header'ını eklemeyi unutma. "201 Created döndü, yeni ID'yi de otomatik verdi."
4. `PUT` ile güncelle, `DELETE` ile sil, response formatını göster (`<result><message>...</message></result>`).

🖥️ **EKRANDA GÖSTER:** Postman'e geç — `postman/collection.json`, "Books" klasörü.

🎙️ **ANLAT:** "Aynı senaryoları Postman'de de göstereyim — hem Swagger hem Postman'den aynı API'ye ulaşabiliyoruz, ikisi de aynı şekilde çalışıyor." List Books, Create Book isteklerini çalıştır, headers panelinde `Content-Type`/`Accept`'i göster.

---

# BÖLÜM 7 — API'yi Nasıl Belgeledik (1:17–1:23)

🎙️ **ANLAT (giriş):** "Bir API ne kadar iyi olursa olsun, nasıl kullanılacağı belli değilse işe yaramaz. Ben iki katmanlı gittim."

🖥️ **EKRANDA GÖSTER:** Tarayıcıda `http://localhost:8000/docs` (Swagger UI) sayfasında yukarı kaydır, endpoint gruplarını (Books, Members, Borrowings, Reports, External) göster, birini aç.

🎙️ **ANLAT:** "Bunu elle yazmadım — `main.py`'deki `FastAPI(title=..., description=..., version=\"1.0.0\")` tanımından (satır 39-48) FastAPI otomatik olarak bu Swagger sayfasını üretiyor. Her endpoint için parametreler, örnek şemalar, hatta 'dene' butonu bile hazır geliyor."

🖥️ **EKRANDA GÖSTER:** `http://localhost:8000/openapi.json` (ham OpenAPI şeması, isteğe bağlı gösterilebilir).

🖥️ **EKRANDA GÖSTER:** `README.md` — "API Reference" bölümü.

🎙️ **ANLAT:** "README'de her endpoint'i method, path, auth durumu ve açıklamasıyla tablo halinde listeledim. Ayrıca cURL örnekleri var — listeleme, tekil getirme, oluşturma, güncelleme, silme, dış servis çağrısı, ve bilerek hatalı bir istek örneği (API key eksik). Yani Swagger'ı hiç açmadan da README okuyarak API'yi tamamen anlayabilirsiniz."

🖥️ **EKRANDA GÖSTER:** README "Evidence Checklist" bölümü.

🎙️ **ANLAT:** "Bu listeyi ben de bu videoyu hazırlarken kendi kontrol listem olarak kullandım — her maddesini tek tek gösterdiğimden emin olmak için."

---

# BÖLÜM 8 — Dışarıya Açılmak: Open Library Entegrasyonu (1:23–1:33)

🎙️ **ANLAT (giriş):** "Şimdiye kadar hep kendi verimle konuştuk. Peki dışarıdaki bir servisten veri çekip onu da bu sisteme dahil edebilir miyim? Evet — **Open Library**'yi (openlibrary.org) kullandım, ISBN'e göre kitap bilgisi (başlık, yazar, yayınevi, yıl, açıklama) dönen ücretsiz ve public bir servis."

🖥️ **EKRANDA GÖSTER:** `backend/src/external_service.py` dosyasını aç.

🎙️ **ANLAT satır satır:**
- Satır 21-34 (`normalize_isbn`): "Kullanıcı ISBN-10 ya da ISBN-13, tireli ya da tiresiz girebilir. Ben önce sadece rakam/X karakterlerini alıyorum, 13 haneliyse tire formatına sokuyorum, 10 haneliyse gerçek bir **ISBN-13 checksum algoritmasıyla** (satır 26-32 — alternatif ağırlıklarla, yani 1 ve 3 ile çarpıp mod 10 alarak) 13 haneye çeviriyorum. Bunu yapmamın sebebi, farklı formatlarda gelen girdiyi tek tipe indirip hem doğru sorguyu atmak hem de kendi `isbnType` kuralıma uygun üretmek."
- Satır 37-66 (`fetch_open_library`): "`httpx.AsyncClient` ile asenkron istek atıyorum, Open Library'nin Books API'sine `bibkeys=ISBN:...&format=json&jscmd=data` diye sorgu yapıyorum. Orada veri bulamazsam (satır 53), `/isbn/{isbn}.json` diye ikinci bir endpoint'e düşüyorum — Open Library'nin iki farklı JSON şemasını da karşılıyorum."
- Satır 69-89, 92-122: "Gelen JSON'dan yazar listesini, yayınevini, yılı (regex ile 4 haneli bir sayı arayarak) ve açıklamayı (bazen string bazen `{value: ...}` diye dict geliyor, ikisini de aynı fonksiyonla normalize ediyorum) çıkarıyorum."
- Satır 132-148 (`json_to_enriched_xml`) — **işin can alıcı kısmı burası:** "JSON'u XML'e çeviriyorum — `etree.Element('enrichedBook')` kuruyorum, içine `title`, `author`, `publisher`, `publicationYear`, `description`, `categories/category`, `source` elemanlarını dolduruyorum. Sonra **satır 147'de `validate_or_raise(root)` çağırıyorum** — yani dış servisten gelen veriyi kör kör kabul etmiyorum, kendi `schema.xsd`'mdeki `enrichedBookType` tanımına karşı doğruluyorum. Dışarıdan gelen veriye güvenmemek gerektiğini burada pratik olarak gösteriyorum."
- Satır 151-154 (`enrich_isbn`): "Tüm akışı birleştiren fonksiyon — çek, XML'e çevir, doğrula, döndür."

🖥️ **EKRANDA GÖSTER:** `backend/src/routers/external.py` (tamamı, 26 satır).

🎙️ **ANLAT:** "Burada üç farklı hata durumunu ayrı ayrı ele alıyorum: ISBN Open Library'de yoksa 404, dış servise ulaşılamıyorsa (zaman aşımı vs.) 502 Bad Gateway — bunu bilerek seçtim çünkü hata bende değil, upstream'de — dış veri kendi şemama uymuyorsa 400."

🖥️ **EKRANDA GÖSTER:** Swagger'dan ya da frontend'deki `/enrich` sayfasından `GET /api/v1/external/enrich/9780134685991` çağır.

💻 **ÇALIŞTIR (alternatif, Terminal B):**
```bash
curl -H "Accept: application/xml" "http://localhost:8000/api/v1/external/enrich/9780134685991"
```

🎙️ **ANLAT dönen XML üzerinden:** "İşte gerçek zamanlı olarak Open Library'den çekilen 'Effective Java' bilgisi, benim kendi şemama uygun bir `<enrichedBook>` XML'i olarak geldi. `source` elemanı da verinin nereden geldiğini belgeliyor."

🖥️ **EKRANDA GÖSTER:** Frontend `http://localhost:3000/enrich` sayfası — bir ISBN gir, "Enrich" butonuna bas.

🎙️ **ANLAT:** "Frontend tarafında da bu sonucu `lib/xmlParser.ts`'teki `parseEnrichedBookXml` fonksiyonu DOMParser ile ayrıştırıp ekrana basıyor — yani dış servisten gelen veri sadece backend'de kalmıyor, gerçekten arayüzde kullanılıyor."

---

# BÖLÜM 9 — Küçük Ama Önemli Detaylar: Kalite ve Hata Yönetimi (1:33–1:39)

🎙️ **ANLAT (giriş):** "Şimdi biraz geri çekilip projenin genel kalitesinden bahsedeyim — çünkü kod çalışıyor olması yetmiyor, tutarlı ve öngörülebilir olması da lazım."

🖥️ **EKRANDA GÖSTER:** `backend/src/responses.py` ve `xml_responses.py` (tekrar kısaca).

🎙️ **ANLAT — tutarlılık üzerine:**
- "Tüm etiketler camelCase, snake_case karışımı yok."
- "ID formatı her yerde aynı: `bk-XXX`, `mem-XXX`, `brw-XXX`, üç haneli sıfır dolgulu."
- "Duplicate ID hem şema hem kod seviyesinde engelleniyor."
- "Klasör yapısı da temiz — `data/`, `src/`, `src/routers/`, `tests/` net ayrılmış."

🎙️ **ANLAT — hata yönetimi üzerine:**
- "Malformed XML gelirse — yani XML bile değilse — `parse_book_xml` içindeki `XMLSyntaxError` yakalanıp 400 dönüyor."
- "Şema hatası olursa — `validate_or_raise` her yazmadan önce çalışıyor, hata yakalanıp 400 + XSD'nin ürettiği gerçek hata mesajının bir kısmı response'a ekleniyor."
- "Zorunlu bir alan eksikse — mesela `title` yoksa, yine aynı şema doğrulama yoluyla yakalanıyor."
- "Ve tüm hatalar aynı formatta dönüyor — `<error><code>...</code><message>...</message><detail>...</detail></error>`. 404, 400, 401, 406, 500 — hepsi bu tek kalıbı kullanıyor, kullanıcı hangi hatayı alırsa alsın aynı şekilde parse edebiliyor."

🖥️ **EKRANDA GÖSTER:** `README.md` içindeki örnek hata XML'i.

🎙️ **ANLAT — çalıştırılabilirlik üzerine:** "README'de kurulum adımları, çalıştırma komutları, örnek veri (zaten repo'da hazır geliyor), örnek istekler ve beklenen çıktılar var. Yani biri bu projeyi klonlayıp sıfırdan ayağa kaldırabilir, ekstra bir hazırlık yapmasına gerek yok."

---

# BÖLÜM 10 — Üstüne Kattığımız Ekstralar (1:39–1:49)

🎙️ **ANLAT (giriş):** "Temel akışı gösterdim, ama projeye birkaç şey daha ekledim, onlardan da bahsedeyim."

1. **API versiyonlama:** 🖥️ `main.py` satır 59 (`API_PREFIX = "/api/v1"`). "Az önce değindim ama tekrar hatırlatayım — tüm endpoint'ler `/api/v1/` altında, ileride kırmadan büyütebilirim."

2. **Kimlik doğrulama:** 🖥️ `auth.py` satır 17-20. "POST/PUT/DELETE'de `X-API-Key` zorunlu."

3. **Sayfalama ve filtreleme:** 🖥️ `routers/books.py` (`page`, `limit`, `genre`, `search`), `routers/members.py`, `routers/borrowings.py` (`status`, `memberRef`, `bookRef`). "Sadece basit bir liste değil, gerçek filtreleme ve sayfalama var."

4. **Gelişmiş XSD kısıtları:** 🖥️ `schema.xsd`. "Pattern, enumeration, ID/IDREF, minOccurs/maxOccurs, sayısal tip kısıtları — Bölüm 2'de detaylı gördük."

5. **Namespace kullanımı:** 🖥️ `backend/data/library.xml` satır 2 — `xmlns:xsi` ve `xsi:schemaLocation`. "Dokümanın hangi şemaya bağlı olduğunu XML Schema Instance namespace'iyle deklare ediyorum."

6. **Test paketi:** 🖥️ `backend/tests/test_validation.py` ve `test_circulation.py` aç.

💻 **ÇALIŞTIR:**
```bash
cd backend
pytest -v
```
🎙️ **ANLAT çıktı üzerinden:** "26 test var ve hepsi geçiyor. `TestValidation` şema doğrulamayı test ediyor, `TestXPathQueries` altı sorgumun her birini, `test_circulation.py`'deki `TestLibraryRules` ve `TestMemberCrud`/`TestCirculation` da iş kurallarını ve CRUD'u. Aynı dosyanın başındaki `temp_manager` fixture'ı (satır 17-21) her testte `library.xml`'in izole bir kopyasını kullanıyor, `tmp_path` ile — böylece testler gerçek veriyi bozmuyor. `conftest.py` de sadece testlerin `src` paketini bulabilmesi için `sys.path`'e proje kökünü ekliyor. Bu gerçek anlamda bir integration test — dosya I/O, şema doğrulama ve iş mantığı birlikte test ediliyor."

7. **Loglama:** 🖥️ `main.py` satır 17-21, `xml_manager.py` satır 186. "Her yazma işleminde ve sunucu açılışında (doğrulama sonucu, streaming sayacı) log üretiyorum."

🎙️ **ANLAT (kapanış):** "Yani temel akışın üstüne versiyonlama, kimlik doğrulama, filtreleme/sayfalama, gelişmiş şema kısıtları, namespace kullanımı, test paketi ve loglama ekledim — hepsi projeye gerçek katkı sağlayan, gösteri amaçlı olmayan özellikler."

---

# BÖLÜM 11 — Hadi Bozalım: Canlı Hata Senaryoları (1:49–1:57)

🎙️ **ANLAT (giriş):** "Şimdi biraz eğlenceli bir kısma geldik — sistemi bilerek bozmaya çalışacağım, hata yönetiminin gerçekten çalıştığını görelim."

### 11.1 Kapatılmamış Etiket

💻 **ÇALIŞTIR:**
```bash
curl -i -X POST \
  -H "Accept: application/xml" -H "Content-Type: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  -d '<book><title>Kapatilmamis' \
  "http://localhost:8000/api/v1/books"
```
🎙️ **ANLAT:** "Etiket kapatılmamış, bu geçerli bir XML bile değil. `parse_book_xml` içindeki `XMLSyntaxError` yakalanıp 400 + `Malformed XML: ...` mesajı dönüyor."

### 11.2 Zorunlu Alan Eksik

💻 **ÇALIŞTIR:**
```bash
curl -i -X POST \
  -H "Accept: application/xml" -H "Content-Type: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  -d '<?xml version="1.0"?><book isbn="978-0-99-111222-3"><author>Eksik Başlık</author></book>' \
  "http://localhost:8000/api/v1/books"
```
🎙️ **ANLAT:** "`title` elemanını hiç göndermedim, sadece `author` var. XSD `bookType`'ta elemanlar sıralı ve `title` zorunlu, sırada ilk gelmesi lazım. Gerçek hata mesajı şöyle: `Element 'author': This element is not expected. Expected is ( title ).` — yani validator `author`'ı görünce 'burada title bekliyordum' diyor."

### 11.3 Yanlış API Key

💻 **ÇALIŞTIR:**
```bash
curl -i -X POST \
  -H "Accept: application/xml" -H "Content-Type: application/xml" \
  -H "X-API-Key: wrong-key" \
  -d '<book isbn="978-0-99-111222-3"><title>Test</title></book>' \
  "http://localhost:8000/api/v1/books"
```
🎙️ **ANLAT:** "Bu sefer `X-API-Key` gönderdim ama değeri yanlış. `auth.py`'deki `require_api_key` gerçek anahtarla karşılaştırıp uymadığını görünce 401 fırlatıyor, bizim standart `<error>` formatımızda dönüyor."

⚠️ **Küçük bir not (sorulursa açıklayabilmen için):** "Eğer `X-API-Key` header'ı hiç gönderilmezse (yanlış değil, tamamen eksik), FastAPI'nin kendi zorunlu header kontrolü benim kodum çalışmadan devreye giriyor ve 422 + JSON döndürüyor — bu, XML-only tasarımımın dışında kalan tek küçük nokta. O yüzden burada 'yanlış key' senaryosunu gösteriyorum, çünkü asıl kendi yazdığım 401/XML mantığının kanıtı bu."

### 11.4 Olmayan Kayıt

💻 **ÇALIŞTIR:**
```bash
curl -i -H "Accept: application/xml" "http://localhost:8000/api/v1/books/bk-999"
```
🎙️ **ANLAT:** "Olmayan bir ID istedim, `BookNotFoundError` yakalanıp standart formatta 404 döndü."

### 11.5 İş Kuralı: Bağlı Kaydı Silmeye Çalışmak

🎙️ **Önce hangi kitabın aktif ödüncü olduğunu göster:**
```bash
curl -s -H "Accept: application/xml" "http://localhost:8000/api/v1/borrowings?status=active"
```
"Mesela `bk-003` (Dune) hem `brw-001` hem `brw-012` kaydında aktif görünüyor, onu silmeyi deneyelim."

💻 **ÇALIŞTIR:**
```bash
curl -i -X DELETE -H "Accept: application/xml" -H "X-API-Key: library-api-key-dev-2026" \
  "http://localhost:8000/api/v1/books/bk-003"
```
🎙️ **ANLAT:** "400 Bad Request, `Cannot delete book bk-003: active borrowings exist`. Veritabanı olmadan da referential integrity'yi nasıl koruduğumun kanıtı bu — `delete_book` fonksiyonu silmeden önce aktif ödünç var mı diye kontrol ediyor, varsa izin vermiyor." ⚠️ *Bu komut gerçekten çalışsa bile kitap silinmeyecek (hata dönüyor), `library.xml` bozulmaz, güvenle canlı gösterebilirsin.*

### 11.6 Frontend'de Hata Nasıl Görünüyor

🖥️ **EKRANDA GÖSTER:** `http://localhost:3000` üzerinde bilerek bir hata tetikle (örn. `/books/new` formunda geçersiz ISBN gir, submit et).

🎙️ **ANLAT:** "`components/XmlErrorBanner.tsx` bileşeni backend'den dönen XML hata gövdesini `lib/api.ts`'teki `handleResponse` fonksiyonuyla parse edip kullanıcıya gösteriyor — `DOMParser` ile `message`/`detail` elemanlarını okuyor. Yani hata yönetimi backend'den frontend'e kadar uçtan uca XML formatında akıyor."

---

# BÖLÜM 12 — Kapanış (1:57–2:00)

🎙️ **ANLAT:**
- "Toparlayalım: `library.xml`'de nested, tutarlı bir veri modeli kurdum; XSD ile bunu hem başarı hem farklı hata türleriyle canlı doğruladım; altı XPath sorgusuyla veride gezindim; bir XSLT dönüşümüyle bunu HTML dashboard'a çevirdim; DOM ve iterparse ile iki farklı teknikle kodda işledim; üç kaynak için tam CRUD sunan, XML-only, doğru HTTP kodlarıyla konuşan bir REST API kurdum; Swagger ve README ile belgeledim; Open Library'den gerçek veri çekip kendi şemamla doğruladım; ve üstüne versiyonlama, kimlik doğrulama, filtreleme, testler gibi bir dizi ekstra kattım."
- "Kod GitHub'da [repo linkini söyle], README'de kurulum adımları var, isteyen kendi makinesinde çalıştırıp deneyebilir."
- "Dinlediğiniz için teşekkürler."

---

## Ek: Kendi Kontrolün İçin — Nerede Neye Değindik

> Bu tablo videoda **okunmuyor**, sadece kayıttan önce/sonra hiçbir şeyi atlamadığından emin olmak için kendi notun.

| Konu | Nerede anlatıldı |
|---|---|
| Veri modeli / nested XML | Bölüm 1 — `backend/data/library.xml` (28 kitap, 9 üye, 12 ödünç) |
| Şema doğrulama (başarı + hata) | Bölüm 2 — `schema.xsd`, `validators.py`, `invalid_library.xml` |
| XPath sorguları | Bölüm 3 — `xpath_queries.py` (6 sorgu) |
| XSLT dönüşümü | Bölüm 4 — `report.xslt` + `xslt_transformer.py` → `/api/v1/reports/dashboard` |
| Kodda ayrıştırma (DOM + SAX benzeri) | Bölüm 5 — `xml_manager.py` (`load_tree`, `stream_books`) |
| REST API (tam CRUD) | Bölüm 6 — `routers/*.py` |
| API dokümantasyonu | Bölüm 7 — Swagger + README |
| Harici servis entegrasyonu | Bölüm 8 — `external_service.py`, `routers/external.py` |
| Kalite / hata yönetimi | Bölüm 9 |
| Versiyonlama, auth, filtreleme, testler, namespace | Bölüm 10 |
| Canlı hata senaryoları | Bölüm 11 |

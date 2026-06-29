# XML Tabanlı Kütüphane Yönetim Sistemi — Proje Raporu

> **Ders:** XML ve Web Servisleri  
> **Üniversite:** Mersin Üniversitesi  
> **Proje Adı:** XML-Based Library Management System  
> **Teknoloji Yığını:** Backend — Python 3.12 + FastAPI + lxml | Frontend — Next.js 15 + React | Veri Deposu — `library.xml`  
> **Tarih:** Haziran 2026

---

## İçindekiler

1. [Proje Genel Bakışı ve Mimari](#1-proje-genel-bakışı-ve-mimari)
2. [XML Veri Yapısı ve Şema Tasarımı](#2-xml-veri-yapısı-ve-şema-tasarımı)
3. [XSD ile Şema Doğrulama](#3-xsd-ile-şema-doğrulama)
4. [XPath Sorguları](#4-xpath-sorguları)
5. [XSLT Dönüşümü ve Dashboard Raporu](#5-xslt-dönüşümü-ve-dashboard-raporu)
6. [XML Parsing — DOM ve iterparse (SAX-like)](#6-xml-parsing--dom-ve-iterparse-sax-like)
7. [REST API Endpoint Kataloğu](#7-rest-api-endpoint-kataloğu)
8. [Harici Servis Entegrasyonu — Open Library](#8-harici-servis-entegrasyonu--open-library)
9. [Modül ve Sınıf Mimarisi](#9-modül-ve-sınıf-mimarisi)
10. [Hata Yönetimi](#10-hata-yönetimi)
11. [Frontend XML Akışı](#11-frontend-xml-akışı)
12. [Test ve Doğrulama Senaryoları](#12-test-ve-doğrulama-senaryoları)
13. [Sonuç ve Değerlendirme](#13-sonuç-ve-değerlendirme)

---

## 1. Proje Genel Bakışı ve Mimari

### 1.1 Amaç ve Kapsam

Bu proje, XML teknolojileri merkezli bir kütüphane yönetim sistemi geliştirmeyi amaçlamaktadır. Geleneksel ilişkisel veritabanı (MySQL, PostgreSQL) yerine tüm kütüphane verisi — kitaplar, üyeler ve ödünç kayıtları — tek bir `library.xml` dosyasında tutulmaktadır. Bu tercih kasıtlıdır: **XSD, XPath, XSLT ve XML Parsing** teknolojilerini uçtan uca, gerçek bir uygulama bağlamında göstermek için yapılmıştır.

Sistem üç temel katmandan oluşur:

| Katman | Teknoloji | Sorumluluk |
|--------|-----------|------------|
| Backend | Python 3.12 + FastAPI + lxml | HTTP API, XML CRUD, XSD doğrulama, XSLT dönüşümü |
| Frontend | Next.js 15 + React + TypeScript | Kullanıcı arayüzü, XML serialize/parse |
| Veri | `backend/data/library.xml` | Tek gerçeklik kaynağı (single source of truth) |

### 1.2 Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  app/ pages  │  │   lib/api.ts    │  │xmlParser.ts   │  │
│  │  (React)     │→ │  (HTTP client)  │→ │(DOMParser)    │  │
│  └──────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ Accept: application/xml
                              │ Content-Type: application/xml
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌───────────┐  ┌────────────┐  ┌──────────┐  ┌─────────┐  │
│  │ routers/  │→ │XmlManager  │→ │validators│→ │xpath_   │  │
│  │books.py   │  │(xml_mgr.py)│  │.py (XSD) │  │queries  │  │
│  │members.py │  └────────────┘  └──────────┘  └─────────┘  │
│  │borrowings │         │                                     │
│  │reports.py │  ┌──────↓──────┐  ┌──────────────────────┐  │
│  │external.py│  │xslt_trans   │  │external_service.py   │  │
│  └───────────┘  │former.py    │  │(Open Library API)    │  │
│                 └─────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────↓───────────────────────────────┐
│                    backend/data/                              │
│  library.xml  │  schema.xsd  │  report.xslt  │  invalid.xml │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Temel Tasarım Kararları

**Neden XML-only API?**  
Tüm CRUD endpoint'leri `Accept: application/xml` ve `Content-Type: application/xml` gerektirir. Bu, sistemin XML teknolojilerini end-to-end kullandığını kanıtlar; gelen istek XML, giden yanıt XML, hata mesajları da XML.

**Neden dosya tabanlı depo?**  
`library.xml` hem veri deposu hem de XML teknolojilerinin sergilendiği platform. XSD doğrulama, XPath sorgulama ve XSLT dönüşümü hepsi aynı dosya üzerinde çalışır.

**Neden iki ayrı parsing yaklaşımı?**  
CRUD işlemleri için lxml DOM (rastgele erişim), büyük dosya senaryoları için `iterparse` (SAX-benzeri streaming). Her ikisi de projenin farklı bölümlerinde açıkça kullanılmaktadır.

---

## 2. XML Veri Yapısı ve Şema Tasarımı

### 2.1 `library.xml` Genel Yapısı

Dosya konumu: `backend/data/library.xml`

Veri büyüklüğü:

| Koleksiyon | Kayıt Sayısı | ID Formatı |
|------------|-------------|------------|
| Kitaplar (`book`) | **28** | `bk-001` … `bk-028` |
| Üyeler (`member`) | **9** | `mem-001` … `mem-009` |
| Ödünçler (`borrowing`) | **12** | `brw-001` … `brw-012` |

Kök eleman yapısı:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<library id="lib-001"
         name="Mersin University Digital Library"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <books>
    <!-- 28 kitap -->
  </books>
  <members>
    <!-- 9 üye -->
  </members>
  <borrowings>
    <!-- 12 ödünç kaydı -->
  </borrowings>
</library>
```

### 2.2 Kitap Elementi Yapısı

```xml
<book id="bk-001" isbn="978-0-13-468599-1">
  <title>Effective Java</title>
  <author>Joshua Bloch</author>
  <publisher>Addison-Wesley</publisher>
  <categories>
    <category>Technology</category>
  </categories>
  <publicationYear>2018</publicationYear>
  <availableCopies>5</availableCopies>
  <description>Best practices for the Java programming language.</description>
</book>
```

**Yapısal özellikler:**

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `@id` | `xs:ID` attribute | Belge genelinde benzersiz — XSD tarafından zorunlu kılınır |
| `@isbn` | `isbnType` attribute | `978-X-XX-XXXXX-X` pattern ile doğrulanır |
| `title`, `author`, `publisher` | Child element | Zorunlu text içerik |
| `categories/category` | Tekrarlanabilir child | Enum değerleri: Sci-Fi, Fantasy, Technology, Classic, … |
| `publicationYear` | Child element | Tam sayı, makul üst sınır XSD'de tanımlı |
| `availableCopies` | Child element | `xs:nonNegativeInteger` — negatif olamaz |
| `description` | Child element | İsteğe bağlı, serbest metin |

Bir kitabın birden fazla kategorisi olabilir (örn. `bk-005` hem Classic hem Sci-Fi):

```xml
<categories>
  <category>Classic</category>
  <category>Sci-Fi</category>
</categories>
```

### 2.3 Üye Elementi Yapısı

```xml
<member id="mem-001">
  <firstName>Ahmet</firstName>
  <lastName>Yılmaz</lastName>
  <email>ahmet@mersin.edu.tr</email>
  <membershipType>student</membershipType>
  <joinDate>2024-09-01</joinDate>
</member>
```

**Adlandırma kuralı:** Tüm element isimleri `camelCase` — `firstName`, `lastName`, `membershipType`, `joinDate`. XSD bu formatı zorunlu kılar; `first_name` gibi snake_case doğrulamayı geçemez.

**Üyelik tipleri (enum):**

| Tip | Ödünç Limiti | Ödünç Süresi |
|-----|-------------|-------------|
| `student` | 5 kitap | 14 gün |
| `faculty` | 10 kitap | 30 gün |
| `public` | 3 kitap | 21 gün |

### 2.4 Ödünç (Borrowing) Elementi ve IDREF Sistemi

```xml
<borrowing id="brw-001" bookRef="bk-003" memberRef="mem-001">
  <borrowDate>2026-06-01</borrowDate>
  <dueDate>2026-07-01</dueDate>
  <status>active</status>
</borrowing>
```

**IDREF ilişki sistemi — relational DB'deki foreign key analojisi:**

| Attribute | XSD Tipi | Görevi |
|-----------|----------|--------|
| `book/@id` | `xs:ID` | Benzersiz kitap kimliği tanımlar |
| `member/@id` | `xs:ID` | Benzersiz üye kimliği tanımlar |
| `borrowing/@id` | `xs:ID` | Benzersiz ödünç kaydı kimliği |
| `borrowing/@bookRef` | `xs:IDREF` | Var olan bir `book/@id`'ye işaret eder |
| `borrowing/@memberRef` | `xs:IDREF` | Var olan bir `member/@id`'ye işaret eder |

XSD'nin `xs:IDREF` tipi sayesinde olmayan bir kitap ID'sine referans vermek mümkün değildir — şema doğrulama bunu yazmadan önce yakalar.

**Ödünç durum değerleri (enum):**

| Durum | Anlam |
|-------|-------|
| `active` | Kitap ödünçte, vade dolmamış |
| `returned` | Kitap iade edilmiş |
| `overdue` | Vade geçmiş, henüz iade edilmemiş |

### 2.5 Adlandırma Kuralları Özeti

| Kural | Örnek |
|-------|-------|
| Kitap ID | `bk-001`, `bk-028` |
| Üye ID | `mem-001`, `mem-009` |
| Ödünç ID | `brw-001`, `brw-012` |
| ISBN formatı | `978-0-13-468599-1` (`isbnType` pattern) |
| Kategori enum | Sci-Fi, Fantasy, Technology, Classic, Mystery, History, Philosophy |
| Üyelik tipi | student, faculty, public |
| Ödünç durumu | active, returned, overdue |

---

## 3. XSD ile Şema Doğrulama

### 3.1 Neden XSD?

XSD (XML Schema Definition) bir XML belgesi için kural kitabıdır. `backend/data/schema.xsd` aşağıdaki soruları yanıtlar:

- Hangi elementler ve attribute'lar var?
- Hangi sırayla gelmeli?
- ISBN formatı doğru mu?
- `bookRef` gerçekten var olan bir kitap ID'sine işaret ediyor mu?
- `availableCopies` negatif olabilir mi?

XSD olmadan bir kullanıcı `<category>Horror</category>` yazabilir, `-5` kopya girebilir ya da olmayan bir kitaba referans verebilir. Şema bunları diske yazmadan önce yakalar.

### 3.2 `validators.py` Modülü

**Dosya:** `backend/src/validators.py`

| Sınıf / Fonksiyon | Satır Aralığı | Görevi |
|-------------------|---------------|--------|
| `ValidationError` | 11–16 | XSD başarısız olduğunda fırlatılan exception; `.log` alanında hata detayı |
| `_load_schema()` | 19–21 | `schema.xsd` dosyasını `etree.XMLSchema` nesnesine dönüştürür |
| `get_schema()` | 27–31 | Şemayı tek seferlik yükler, sonrasını önbellekten (global `_SCHEMA`) döner |
| `validate_xml()` | 34–64 | `(True, "")` veya `(False, error_log)` döner — yumuşak kontrol |
| `validate_or_raise()` | 67–70 | Geçmezse `ValidationError` fırlatır — sert kontrol |
| `validate_file_pair()` | 73–84 | Geçerli + geçersiz dosyayı demo amaçlı karşılaştırır |

**`validate_xml()` iç akışı:**

```python
def validate_xml(xml_source) -> Tuple[bool, str]:
    schema = get_schema()
    try:
        # Girdi tipine göre parse
        if isinstance(xml_source, etree._Element):
            element = xml_source
        elif isinstance(xml_source, Path):
            element = etree.parse(str(xml_source)).getroot()
        elif isinstance(xml_source, bytes):
            element = etree.fromstring(xml_source)
        else:
            element = etree.fromstring(xml_source.encode("utf-8"))

        is_valid = schema.validate(element)
        if is_valid:
            return True, ""
        return False, str(schema.error_log)
    except etree.XMLSyntaxError as exc:
        return False, f"Malformed XML: {exc}"
```

**İki önemli kontrol katmanı:**

1. `etree.XMLSyntaxError` — XML sözdizimi bozuksa şemaya gerek yok; "Malformed XML" mesajı döner.
2. `schema.validate(element)` — sözdizim doğruysa içerik kurallara uygun mu kontrol edilir.

### 3.3 Doğrulama Akış Diyagramı

```
İstemci (POST /api/v1/books)
        │
        ↓
books.py:create_book()
        │
        ↓ await request.body()
manager.parse_book_xml(body)
        │ etree.fromstring()
        │ XMLSyntaxError → ValueError → 400
        ↓
manager.add_book(book_element)
        │
        ↓ validate_or_raise(book_element)
validators.py
        │ get_schema() → önbellekten
        │ schema.validate(element)
        │ FAIL → ValidationError → 400 XML error
        ↓ PASS
_save_tree(tree)
        │ validate_or_raise(tree.getroot())  ← ikinci kontrol
        │ tree.write(library.xml)
        ↓
201 Created + XML yanıt
```

### 3.4 Doğrulama Tetiklenme Noktaları

| Ne zaman | Dosya | Fonksiyon |
|----------|-------|-----------|
| Uygulama başlangıcı | `main.py` | `lifespan` → `validate_xml(LIBRARY_XML)` |
| Başlangıç demo | `main.py` | `validate_file_pair(LIBRARY_XML, INVALID_LIBRARY_XML)` |
| Demo endpoint | `main.py` | `GET /api/v1/validation/demo` |
| Diske yazmadan önce | `xml_manager.py` | `_save_tree()` → `validate_or_raise(tree.getroot())` |
| Kitap ekleme | `xml_manager.py` | `add_book()` → `validate_or_raise(book_element)` |
| Kitap güncelleme | `xml_manager.py` | `update_book()` → `validate_or_raise(updated)` |
| Üye ekleme/güncelleme | `xml_manager.py` | `add_member()`, `update_member()` |
| Open Library zenginleştirme | `external_service.py` | `json_to_enriched_xml()` → `validate_or_raise(root)` |

`_save_tree` içindeki ikinci doğrulama kritiktir: tek bir hatalı `<book>` elemanı tüm `library.xml` dosyasını bozamasın diye diske yazmadan hemen önce tüm belge tekrar kontrol edilir.

### 3.5 Kasıtlı Hatalı Dosya: `invalid_library.xml`

**Dosya:** `backend/data/invalid_library.xml`

XSD demo için bilerek hatalı hazırlanmış dosya. `GET /api/v1/validation/demo` endpoint'i geçerli ve geçersiz dosyayı karşılaştırarak JSON sonuç döner.

| # | Hata | Dosyada Ne Var | İhlal Edilen XSD Kuralı |
|---|------|----------------|------------------------|
| 1 | Geçersiz ISBN | `isbn="NOT-A-VALID-ISBN"` | `isbnType` regex pattern |
| 2 | Geçersiz kategori | `<category>Horror</category>` | `genreType` enum listesi |
| 3 | Absürt yıl | `<publicationYear>99999</publicationYear>` | `xs:integer` üst sınırı |
| 4 | Geçersiz e-posta | `not-an-email` | `emailType` pattern |
| 5 | Çift ID | `id="bk-dup"` iki kez | `xs:ID` benzersizlik kuralı |
| 6 | Var olmayan referans | `bookRef="bk-missing"` | `xs:IDREF` kısıtı |
| 7 | Negatif kopya | `availableCopies=-5` | `xs:nonNegativeInteger` |
| 8 | Geçersiz üyelik tipi | `membershipType=vip` | `membershipTypeEnum` |
| 9 | Geçersiz ödünç durumu | `status=cancelled` | `borrowingStatusType` |

**Demo yanıtı:**

```json
{
  "valid_file": "backend/data/library.xml",
  "valid_result": true,
  "valid_log": "",
  "invalid_file": "backend/data/invalid_library.xml",
  "invalid_result": false,
  "invalid_log": "Element 'category': [facet 'enumeration'] ..."
}
```

### 3.6 API Hata Yanıtı Formatı

Geçersiz XML POST edildiğinde HTTP 400 + XML body:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<error>
  <code>400</code>
  <message>Schema validation failed</message>
  <detail>Element 'availableCopies': '-5' is not a valid
          value of the atomic type 'xs:nonNegativeInteger'.</detail>
</error>
```

**Üreten kod zinciri:**

```
ValidationError
    └→ xml_responses.build_error_xml(400, message, detail)
        └→ responses.xml_error_response(...)
            └→ FastAPI Response(media_type="application/xml")
```

---

## 4. XPath Sorguları

### 4.1 Genel Bakış

XPath, XML belgeleri içinde veri aramak için kullanılan bir sorgu dilidir; SQL'deki `SELECT` ifadesine benzer. Projede `backend/src/xpath_queries.py` modülünde 6 farklı XPath sorgusu uygulanmıştır. Endpoint: `GET /api/v1/reports/xpath`.

Her sorgu `etree.parse(LIBRARY_XML)` ile DOM ağacı yükler, ardından `tree.xpath(...)` ile çalışır.

### 4.2 Sorgu 1 — Sci-Fi Kitapları Yazara Göre Sıralama

**Amaç:** Sci-Fi kategorisindeki kitapları bul, yazara göre alfabetik sırala.

**XPath ifadesi:**
```xpath
/library/books/book[categories/category='Sci-Fi']
```

**Python implementasyonu:**
```python
def query_scifi_books_by_author() -> list[dict]:
    tree = _load_tree()
    xpath = "/library/books/book[categories/category='Sci-Fi']"
    books = tree.xpath(xpath)
    results = []
    for book in sorted(books, key=lambda b: b.findtext("author", "")):
        results.append({
            "id": book.get("id"),
            "title": book.findtext("title"),
            "author": book.findtext("author"),
            "genre": "Sci-Fi",
        })
    return results
```

**Teknik notlar:**
- `[categories/category='Sci-Fi']` → predicate filtresi; SQL'deki `WHERE` karşılığı
- `sorted(...)` Python tarafında ek sıralama uygular; XPath 1.0'da `xsl:sort` XSLT'ye özgüdür

### 4.3 Sorgu 2 — Kategori Bazında Kitap Sayısı

**Amaç:** Her genre kaç kitapta görünüyor? (`count()` fonksiyonu kullanımı)

**XPath ifadeleri:**
```xpath
/library/books/book/categories/category/text()          <!-- tüm kategorileri al -->
count(/library/books/book[categories/category='Sci-Fi']) <!-- Sci-Fi sayısı -->
```

**Python implementasyonu:**
```python
def query_category_counts() -> list[dict]:
    tree = _load_tree()
    categories = tree.xpath("/library/books/book/categories/category/text()")
    unique_categories = sorted(set(categories))
    results = []
    for cat in unique_categories:
        count = tree.xpath(
            f"count(/library/books/book[categories/category='{cat}'])"
        )
        results.append({"category": cat, "count": int(count)})
    return sorted(results, key=lambda x: x["count"], reverse=True)
```

**Teknik notlar:**
- `count()` XPath'in yerleşik sayma fonksiyonu; SQL `COUNT(*)` karşılığı
- `set(categories)` tekrar eden değerleri Python tarafında eleyerek unique set oluşturur

### 4.4 Sorgu 3 — Başlıkta Anahtar Kelime Arama (Case-Insensitive)

**Amaç:** `contains()` ve `translate()` fonksiyonlarını birleştirerek büyük/küçük harf duyarsız başlık araması.

**XPath ifadesi:**
```xpath
/library/books/book[
  contains(
    translate(title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),
    'the'
  )
]
```

**Python implementasyonu:**
```python
def query_title_search(keyword: str) -> list[dict]:
    tree = _load_tree()
    books = tree.xpath(
        f"/library/books/book[contains(translate(title, "
        f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
        f"'{keyword.lower()}')]"
    )
    return [
        {"id": b.get("id"), "title": b.findtext("title"), "author": b.findtext("author")}
        for b in books
    ]
```

**Teknik notlar:**
- XPath 1.0'da `lower-case()` fonksiyonu yoktur; `translate()` manuel karakter eşleme ile büyük harfleri küçüğe çevirir
- `contains()` alt dize arama; SQL'deki `LIKE '%the%'` karşılığı

### 4.5 Sorgu 4 — Aktif Ödünçler ve IDREF Join

**Amaç:** Aktif ödünç kayıtlarını kitap başlığı ve üye adıyla eşleştir. SQL'deki JOIN'in XPath karşılığı.

**XPath ifadeleri:**
```xpath
/library/borrowings/borrowing[status='active']             <!-- aktif ödünçler -->
/library/books/book[@id='bk-003']                          <!-- kitap join -->
/library/members/member[@id='mem-001']                     <!-- üye join -->
```

**ÖNEMLİ NOT:** `status` bir **child element** (`<status>active</status>`), **attribute değil**. Bu nedenle `status='active'` kullanılır, `@status='active'` değil. Bu karışıklık projenin önceki bir sürümünde XSLT dashboard'unda Active Loans sayısının yanlış (0) görünmesine neden olmuş ve düzeltilmiştir.

**Python implementasyonu:**
```python
def query_active_borrowed_books() -> list[dict]:
    tree = _load_tree()
    borrowings = tree.xpath("/library/borrowings/borrowing[status='active']")
    results = []
    for brw in borrowings:
        book_ref = brw.get("bookRef")
        member_ref = brw.get("memberRef")
        book = tree.xpath(f"/library/books/book[@id='{book_ref}']")
        member = tree.xpath(f"/library/members/member[@id='{member_ref}']")
        results.append({
            "borrowingId": brw.get("id"),
            "bookTitle": book[0].findtext("title") if book else "Unknown",
            "memberName": (
                f"{member[0].findtext('firstName')} {member[0].findtext('lastName')}"
                if member else "Unknown"
            ),
            "dueDate": brw.findtext("dueDate"),
        })
    return results
```

### 4.6 Sorgu 5 — Yayınevi ve Yıl Filtresi (Zincirleme Predicates)

**Amaç:** Belirli bir yayınevine ait ve belirli yıldan sonra yayımlanan kitapları bul.

**XPath ifadesi:**
```xpath
/library/books/book[publisher='Penguin Classics' and publicationYear > 1900]
```

**Python implementasyonu:**
```python
def query_publisher_books_after_year(publisher: str, year: int) -> list[dict]:
    tree = _load_tree()
    books = tree.xpath(
        f"/library/books/book[publisher='{publisher}' and publicationYear > {year}]"
    )
    return [
        {
            "id": b.get("id"),
            "title": b.findtext("title"),
            "publisher": b.findtext("publisher"),
            "year": b.findtext("publicationYear"),
        }
        for b in books
    ]
```

**Teknik notlar:**
- `and` operatörü ile iki predicate zincirlenir
- Sayısal karşılaştırma (`> 1900`) XPath 1.0'da otomatik tip dönüşümü yapar

### 4.7 Sorgu 6 — Gecikmiş Ödünç Kayıtları

**Amaç:** `status='overdue'` olan tüm ödünçleri kitap bilgisiyle listele.

**XPath ifadesi:**
```xpath
/library/borrowings/borrowing[status='overdue']
```

**Python implementasyonu:**
```python
def query_overdue_borrowings() -> list[dict]:
    tree = _load_tree()
    borrowings = tree.xpath("/library/borrowings/borrowing[status='overdue']")
    results = []
    for brw in borrowings:
        book_ref = brw.get("bookRef")
        book = tree.xpath(f"/library/books/book[@id='{book_ref}']")
        results.append({
            "borrowingId": brw.get("id"),
            "bookTitle": book[0].findtext("title") if book else "Unknown",
            "dueDate": brw.findtext("dueDate"),
            "status": "overdue",
        })
    return results
```

### 4.8 XPath Endpoint

`run_all_queries()` fonksiyonu altı sorguyu çalıştırır ve sonuçları bir dict'te toplar. Router bunu XML formatına sarar:

```
GET /api/v1/reports/xpath
Accept: application/xml
```

```xml
<?xml version='1.0' encoding='UTF-8'?>
<xpathResults>
  <scifiByAuthor>
    <book><id>bk-003</id><title>Dune</title><author>Frank Herbert</author></book>
    ...
  </scifiByAuthor>
  <categoryCounts>
    <category name="Technology" count="8"/>
    ...
  </categoryCounts>
  ...
</xpathResults>
```

---

## 5. XSLT Dönüşümü ve Dashboard Raporu

### 5.1 XSLT Nedir ve Neden Kullanıldı?

XSLT (XSL Transformations), XML belgelerini başka formatlara dönüştürmek için kullanılan bir dönüşüm dilidir. Bu projede `library.xml` → HTML dashboard dönüşümü için kullanılmaktadır.

**Seçim gerekçesi:** Ham XML'i kullanıcıya doğrudan göstermek yerine, tek bir XSL stylesheet ile otomatik olarak güzel görünümlü, istatistik içeren bir HTML rapor sayfası üretilmektedir. Bu, sunucu tarafında çalışır — istemciye hazır HTML gider.

### 5.2 Python Tarafı — `xslt_transformer.py`

**Dosya:** `backend/src/xslt_transformer.py`

```python
def transform_to_html() -> str:
    xml_doc = etree.parse(str(LIBRARY_XML))
    xslt_doc = etree.parse(str(REPORT_XSLT))
    transform = etree.XSLT(xslt_doc)
    result = transform(xml_doc)
    return str(result)
```

**Adım adım akış:**

1. `etree.parse(LIBRARY_XML)` — `library.xml` DOM ağacına yüklenir
2. `etree.parse(REPORT_XSLT)` — `report.xslt` stylesheet yüklenir
3. `etree.XSLT(xslt_doc)` — lxml'in XSLT motoru başlatılır
4. `transform(xml_doc)` — dönüşüm çalışır, HTML üretilir
5. `reports.py:dashboard_report()` → `HTMLResponse` ile tarayıcıya gönderilir

**Endpoint:**
```
GET /api/v1/reports/dashboard
```
`Accept: application/xml` **gerekmez** — yanıt `text/html`.

### 5.3 `report.xslt` İçeriği

**Dosya:** `backend/data/report.xslt`

Kök template `<xsl:template match="/">` tam bir HTML sayfası üretir.

**6 İstatistik Kartı:**

| Kart | XSLT / XPath İfadesi |
|------|---------------------|
| Total Books | `count(/library/books/book)` |
| Registered Members | `count(/library/members/member)` |
| Active Borrowings | `count(/library/borrowings/borrowing[status='active'])` |
| Overdue Items | `count(/library/borrowings/borrowing[status='overdue'])` |
| Sci-Fi Books | `count(/library/books/book[categories/category='Sci-Fi'])` |
| Total Available Copies | `sum(/library/books/book/availableCopies)` |

```xml
<div class="stat-card">
  <div class="value">
    <xsl:value-of select="count(/library/books/book)"/>
  </div>
  <div class="label">Total Books</div>
</div>
```

**3 Tablo:**

**Tablo 1 — Book Catalog:**
```xml
<xsl:for-each select="/library/books/book">
  <xsl:sort select="title"/>
  <tr>
    <td><xsl:value-of select="@id"/></td>
    <td><xsl:value-of select="title"/></td>
    <td><xsl:value-of select="author"/></td>
    ...
  </tr>
</xsl:for-each>
```

**Tablo 2 — Active & Overdue Borrowings** (IDREF join):
```xml
<xsl:for-each select="/library/borrowings/borrowing[status='active' or status='overdue']">
  <td>
    <xsl:value-of select="/library/books/book[@id=current()/@bookRef]/title"/>
  </td>
  <td>
    <xsl:value-of select="/library/members/member[@id=current()/@memberRef]/firstName"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="/library/members/member[@id=current()/@memberRef]/lastName"/>
  </td>
</xsl:for-each>
```

**Tablo 3 — Members Overview** (her üye için aktif ödünç sayısı):
```xml
<xsl:value-of select="count(/library/borrowings/borrowing[
  @memberRef=current()/@id and (status='active' or status='overdue')
])"/>
```

### 5.4 XSLT Akış Özeti

```
library.xml ──┐
               ├→ etree.XSLT(report.xslt) → HTML string → HTMLResponse
report.xslt ──┘
```

Frontend `app/reports/page.tsx` sayfası bu URL'yi `<iframe>` içinde render eder.

---

## 6. XML Parsing — DOM ve iterparse (SAX-like)

### 6.1 İki Parsing Yaklaşımı

Java ekosisteminde DOM, SAX ve StAX parsing yöntemleri bulunur. Bu projede Python'un lxml kütüphanesi kullanılmakta ve iki farklı yaklaşım sergilenmektedir:

| Yaklaşım | Java Karşılığı | Projede Kullanım Yeri | Özellik |
|----------|----------------|----------------------|---------|
| **DOM** (`etree.parse`) | DOM | CRUD işlemleri, XPath sorguları | Tüm belgeyi belleğe yükler; rastgele erişim |
| **Streaming** (`iterparse`) | SAX / StAX | Kitap sayımı, startup demo | Olay tabanlı; düşük bellek kullanımı |

### 6.2 Ana Sınıf: `XmlManager`

**Dosya:** `backend/src/xml_manager.py`

```python
class XmlManager:
    """Manages library.xml with DOM-based read/write and iterparse streaming."""

    def __init__(self, xml_path=LIBRARY_XML):
        self.xml_path = xml_path
```

### 6.3 DOM Parsing

#### `load_tree()` — Tam Belge Yükleme

```python
def load_tree(self) -> etree._ElementTree:
    """Load full XML document into DOM tree."""
    return etree.parse(str(self.xml_path))
```

Tüm `library.xml` belleğe alınır ve `etree._ElementTree` nesnesi döner. Bu nesne üzerinde XPath sorguları, element ekleme/silme gibi işlemler yapılabilir.

#### `get_book_by_id()` — Tekil Okuma

```python
def get_book_by_id(self, book_id: str) -> etree._Element:
    tree = self.load_tree()
    results = tree.xpath(f"/library/books/book[@id='{book_id}']")
    if not results:
        raise BookNotFoundError(f"Book not found: id={book_id}")
    return copy.deepcopy(results[0])
```

`copy.deepcopy()` kritiktir: orijinal DOM ağacı bozulmaz, yalnızca kopyası döner. Çağıran kod kopyayı değiştirse bile `library.xml`'deki veri güvendedir.

#### `add_book()` — Yazma İşlemi

```python
def add_book(self, book_element: etree._Element) -> etree._Element:
    tree = self.load_tree()
    books_container = tree.xpath("/library/books")[0]
    validate_or_raise(book_element)          # XSD kontrolü
    books_container.append(book_element)
    self._save_tree(tree)                    # diske yaz + ikinci XSD kontrolü
    return copy.deepcopy(book_element)
```

#### `_save_tree()` — Disk Yazma ve Çift Doğrulama

```python
def _save_tree(self, tree: etree._ElementTree) -> None:
    validate_or_raise(tree.getroot())        # tüm belge tekrar doğrulanır
    tree.write(
        str(self.xml_path),
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )
```

`_save_tree` içindeki ikinci `validate_or_raise` çağrısı savunma hattıdır: element bazında doğrulamayı geçen bir değişiklik, belge bütününde bir tutarsızlık yaratıyorsa bu noktada yakalanır.

### 6.4 Streaming Parsing — `iterparse`

#### `stream_books()` — SAX-like Olay Tabanlı Okuma

```python
def stream_books(self) -> Iterator[dict]:
    """
    Stream-parse books using iterparse for memory-efficient processing.
    Demonstrates SAX-like event-driven parsing.
    """
    context = etree.iterparse(
        str(self.xml_path),
        events=("end",),
        tag="book",
    )
    for _event, elem in context:
        yield {
            "id": elem.get("id"),
            "isbn": elem.get("isbn"),
            "title": elem.findtext("title"),
            "author": elem.findtext("author"),
            "publisher": elem.findtext("publisher"),
            "publicationYear": elem.findtext("publicationYear"),
            "availableCopies": elem.findtext("availableCopies"),
        }
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
```

**Teknik açıklama:**

- `events=("end",)` — her `</book>` kapanış etiketi işlendiğinde tetiklenir
- `tag="book"` — yalnızca `<book>` elementlerini filtreler, diğer eventler atlanır
- `elem.clear()` — işlenen element bellekten temizlenir
- `while elem.getprevious()...` — önceki kardeş elementler de temizlenir

Bu sayede 10.000 kitaplık bir dosyada bile tüm belgeyi belleğe almadan sayım yapılabilir.

#### `count_books_streaming()`

```python
def count_books_streaming(self) -> int:
    return sum(1 for _ in self.stream_books())
```

Bu fonksiyon `main.py` içindeki `lifespan` startup'ında çağrılır:

```python
count = manager.count_books_streaming()
logger.info("Streaming book count via iterparse: %d", count)
```

Uygulama açılışı log çıktısı:
```
[INFO] Streaming book count via iterparse: 28
```

### 6.5 HTTP Body Parse — `parse_book_xml()`

```python
def parse_book_xml(self, xml_bytes: bytes) -> etree._Element:
    try:
        element = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"Malformed XML: {exc}") from exc
    if element.tag != "book":
        raise ValueError(f"Expected <book>, got <{element.tag}>")
    return element
```

HTTP body'den gelen ham byte dizisi DOM elementine dönüştürülür. `XMLSyntaxError` yakalanır ve `ValueError` olarak yeniden fırlatılır — router katmanı bu hatayı 400 yanıtına çevirir.

### 6.6 XmlManager Metod Kataloğu

| Grup | Metodlar |
|------|----------|
| DOM yükleme/kaydetme | `load_tree`, `get_root`, `_save_tree` |
| Streaming | `stream_books`, `count_books_streaming` |
| Kitap okuma | `get_all_books`, `get_book_by_id` |
| Kitap yazma | `add_book`, `update_book`, `delete_book`, `parse_book_xml` |
| Üye | `get_all_members`, `get_member_by_id`, `add_member`, `update_member`, `delete_member`, `parse_member_xml` |
| Ödünç | `get_all_borrowings`, `get_borrowing_by_id`, `checkout_book`, `return_book`, `update_borrowing`, `delete_borrowing`, `parse_borrowing_xml` |
| İş kuralları | `sync_overdue_status`, `count_active_loans`, `_ensure_references_exist`, `_ensure_unique_email` |
| ID üretimi | `_next_id`, `_next_book_id`, `_next_member_id`, `_next_borrowing_id` |

---

## 7. REST API Endpoint Kataloğu

### 7.1 Genel Kurallar

**Base URL:** `http://localhost:8000/api/v1`

| Header | Zorunlu Olduğu Durum | Yoksa |
|--------|---------------------|-------|
| `Accept: application/xml` | GET, POST, PUT, DELETE (çoğu endpoint) | **406 Not Acceptable** |
| `X-API-Key: library-api-key-dev-2026` | POST, PUT, DELETE | **401 Unauthorized** |
| `Content-Type: application/xml` | POST, PUT body | Body ham XML okunur |

Doğrulama kodu `backend/src/auth.py`:

```python
def require_api_key(x_api_key: str = Header(None)) -> None:
    if x_api_key != API_KEY:
        raise XmlHttpException(401, "Invalid or missing API key", "")

def require_xml_accept(request: Request) -> None:
    accept = request.headers.get("accept", "")
    if "application/xml" not in accept and "*/*" not in accept:
        raise XmlHttpException(406, "Accept must include application/xml", "")
```

### 7.2 Kitap Endpoint'leri

#### GET /api/v1/books — Liste

```
GET /api/v1/books?genre=Sci-Fi&search=dune&page=1&limit=10
Accept: application/xml
```

Akış:
1. Query parametreleri okunur: `genre`, `search`, `page`, `limit`
2. `manager.get_all_books(genre, search, page, limit)` çağrılır
3. XPath ile filtreleme: genre için predicate, search için `contains(translate(...))`
4. Sayfalama uygulanır: `start = (page-1)*limit`, `end = start+limit`
5. `books_collection_xml(books, total=total)` ile XML sarmalanır

Yanıt:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<books count="10" totalCount="28">
  <book id="bk-003" isbn="978-0-44-101359-5">
    <title>Dune</title>
    <author>Frank Herbert</author>
    ...
  </book>
  ...
</books>
```

Response headers: `X-Total-Count: 28`, `X-Page: 1`, `X-Limit: 10`

#### GET /api/v1/books/{id} — Tekil Kayıt

```
GET /api/v1/books/bk-001
Accept: application/xml
```

Hata (bulunamadı):
```xml
<error>
  <code>404</code>
  <message>Book not found</message>
  <detail>id=bk-999</detail>
</error>
```

#### POST /api/v1/books — Oluşturma

```
POST /api/v1/books
Accept: application/xml
Content-Type: application/xml
X-API-Key: library-api-key-dev-2026
```

Body:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<book isbn="978-0-14-143951-8">
  <title>Pride and Prejudice</title>
  <author>Jane Austen</author>
  <publisher>Penguin Classics</publisher>
  <categories><category>Classic</category></categories>
  <publicationYear>1813</publicationYear>
  <availableCopies>4</availableCopies>
</book>
```

Router kodu pattern'i:
```python
@router.post("/books", ...)
async def create_book(request: Request, ...):
    body = await request.body()
    book_element = manager.parse_book_xml(body)     # syntax check
    try:
        created = manager.add_book(book_element)    # XSD + disk
        return xml_response(element_to_bytes(created), status_code=201)
    except ValidationError as exc:
        return xml_error_response(400, str(exc), exc.log[:500])
    except ValueError as exc:
        return xml_error_response(400, str(exc))
```

#### PUT /api/v1/books/{id} — Güncelleme

Eski `<book>` DOM'dan silinir, yeni element aynı konuma eklenir, `_save_tree` çalışır.

#### DELETE /api/v1/books/{id} — Silme

**İş kuralı:** Aktif veya gecikmiş ödünç varsa silme engellenir → 400 hatası.

Başarı yanıtı:
```xml
<result>
  <message>Book deleted successfully</message>
  <id>bk-001</id>
</result>
```

### 7.3 Üye Endpoint'leri

Kitap endpoint'leriyle aynı CRUD pattern'i; `parse_member_xml`, `add_member` gibi metod isimleri farklıdır.

**Ek iş kuralı:** `delete_member` — üyenin aktif ödüncü varsa silinmez.

**Üyelik tipi filtrelemesi:**
```
GET /api/v1/members?membershipType=student&search=ahmet
```

### 7.4 Ödünç Endpoint'leri

| Method | Path | Fonksiyon | Özel Not |
|--------|------|-----------|----------|
| GET | `/borrowings` | `list_borrowings` | `status`, `memberRef`, `bookRef` filtresi |
| POST | `/borrowings` | `checkout_book` | Ödünç alma akışı |
| PUT | `/borrowings/{id}/return` | `return_book` | Body gerekmez |
| PUT | `/borrowings/{id}` | `update_borrowing` | Genel güncelleme |
| DELETE | `/borrowings/{id}` | `delete_borrowing` | Yalnızca `returned` kayıtlar |

**`checkout_book()` iş akışı (xml_manager.py satır 390–450):**

```
1. bookRef, memberRef zorunlu — yoksa ValueError
2. _ensure_references_exist() — her ikisi de var mı?
3. book.availableCopies > 0 — stokta var mı?
4. count_active_loans(memberRef) vs loan_limit(membershipType)
   — limit aşılmış mı?
5. Yeni <borrowing> elementi XSD sırasına göre oluşturulur
6. availableCopies -= 1
7. _save_tree() — XSD + disk
```

**`return_book()` akışı:**

```
1. borrowing.status = 'returned'
2. returnDate elementi eklenir
3. book.availableCopies += 1
4. _save_tree()
```

### 7.5 Rapor ve Yardımcı Endpoint'ler

| Method | Path | Yanıt Tipi | Açıklama |
|--------|------|------------|----------|
| GET | `/reports/dashboard` | `text/html` | XSLT → HTML dashboard |
| GET | `/reports/xpath` | `application/xml` | 6 XPath sorgusu sonucu |
| GET | `/external/enrich/{isbn}` | `application/xml` | Open Library zenginleştirme |
| GET | `/health` | `application/json` | Sağlık kontrolü (JSON istisnası) |
| GET | `/validation/demo` | `application/json` | XSD demo (JSON istisnası) |

---

## 8. Harici Servis Entegrasyonu — Open Library

### 8.1 Genel Bakış

**Harici servis:** [Open Library API](https://openlibrary.org) — ISBN ile kitap metadata (JSON)  
**Modül:** `backend/src/external_service.py`  
**Router:** `backend/src/routers/external.py` → `enrich_book(isbn)`  
**Endpoint:** `GET /api/v1/external/enrich/{isbn}`

Entegrasyonun amacı: kullanıcı ISBN girdiğinde dış kaynaktan otomatik kitap bilgisi çekmek, JSON yanıtını XML'e dönüştürmek ve XSD ile doğrulamak. Kullanıcı bu zenginleştirilmiş veriyi onaylayarak kütüphaneye ekleyebilir.

### 8.2 Servis Akışı

```
Frontend (EnrichPanel.tsx)
    │ GET /api/v1/external/enrich/{isbn}
    ↓
external.py:enrich_book()
    │
    ↓ enrich_isbn(isbn)
external_service.py
    │
    ├→ normalize_isbn(isbn)
    │   └ rakam dışı temizle
    │   └ ISBN-10 → ISBN-13 dönüşümü (check digit hesabı)
    │
    ├→ fetch_open_library(isbn)  [async]
    │   ├ GET /api/books?bibkeys=ISBN:{clean}&format=json&jscmd=data
    │   └ 404 / boş → GET /isbn/{clean}.json  (fallback)
    │
    ├→ _parse_books_api_data() / _parse_isbn_edition()
    │   └ JSON → Python dict (title, authors, publisher, year, description)
    │
    ├→ json_to_enriched_xml(book_data)
    │   └ etree.Element("enrichedBook") oluştur
    │   └ validate_or_raise(root)  ← XSD kontrolü
    │
    └→ bytes döner
```

### 8.3 `normalize_isbn()`

```python
def normalize_isbn(isbn: str) -> str:
    digits = re.sub(r"[^0-9Xx]", "", isbn)
    if len(digits) == 13:
        return f"{digits[0:3]}-{digits[3:4]}-{digits[4:9]}-{digits[9:12]}-{digits[12]}"
    if len(digits) == 10:
        isbn13 = f"978{digits[:9]}"
        total = sum(
            int(d) * (1 if i % 2 else 3)
            for i, d in enumerate(isbn13)
        )
        check = (10 - (total % 10)) % 10
        full = isbn13 + str(check)
        return f"{full[0:3]}-{full[3:4]}-{full[4:9]}-{full[9:12]}-{full[12]}"
    return isbn
```

Kullanıcı ISBN'i tireli veya tiresiz girebilir; ISBN-10 ise ISBN-13'e dönüştürülür (check digit EAN-13 algoritması ile hesaplanır).

### 8.4 `fetch_open_library()` — Async HTTP

```python
async def fetch_open_library(isbn: str) -> dict:
    clean = re.sub(r"[^0-9Xx]", "", isbn)
    books_api_url = (
        f"https://openlibrary.org/api/books"
        f"?bibkeys=ISBN:{clean}&format=json&jscmd=data"
    )
    async with httpx.AsyncClient(timeout=15.0, headers=HTTP_HEADERS) as client:
        response = await client.get(books_api_url)
        response.raise_for_status()
        payload = response.json()
    
    if f"ISBN:{clean}" not in payload:
        # Fallback: /isbn/{clean}.json
        ...
```

**httpx.AsyncClient** — async/await uyumlu HTTP istemci; FastAPI'nin async yapısıyla entegre.

### 8.5 `json_to_enriched_xml()` — JSON → XML Dönüşümü

```python
def json_to_enriched_xml(book_data: dict) -> bytes:
    root = etree.Element("enrichedBook")
    root.set("isbn", book_data.get("isbn", ""))
    for field in ["title", "author", "publisher"]:
        el = etree.SubElement(root, field)
        el.text = book_data.get(field, "Unknown")
    # publicationYear, description, categories ...
    cats = etree.SubElement(root, "categories")
    cat = etree.SubElement(cats, "category")
    cat.text = book_data.get("genre", DEFAULT_GENRE)
    source = etree.SubElement(root, "source")
    source.text = "Open Library API"
    validate_or_raise(root)         # enrichedBookType XSD kontrolü
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")
```

Çıktı XML:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<enrichedBook isbn="978-0-14-143951-8">
  <title>Pride and Prejudice</title>
  <author>Jane Austen</author>
  <publisher>Penguin Classics</publisher>
  <publicationYear>1813</publicationYear>
  <description>A novel of manners...</description>
  <categories><category>Classic</category></categories>
  <source>Open Library API</source>
</enrichedBook>
```

### 8.6 Router Hata Yönetimi

```python
@router.get("/external/enrich/{isbn}")
async def enrich_book(isbn: str):
    try:
        xml_bytes = await enrich_isbn(isbn)
        return xml_response(xml_bytes)
    except ValueError as exc:
        return xml_error_response(404, str(exc), f"isbn={isbn}")
    except httpx.HTTPError as exc:
        return xml_error_response(502, "External service unavailable", str(exc))
    except ValidationError as exc:
        return xml_error_response(400, "Enriched data failed validation", exc.log[:500])
```

| Durum | HTTP Kodu | Mesaj |
|-------|-----------|-------|
| ISBN bulunamadı | 404 | ISBN not found in Open Library |
| Open Library erişilemez | 502 | External service unavailable |
| XSD doğrulama başarısız | 400 | Enriched data failed validation |

---

## 9. Modül ve Sınıf Mimarisi

### 9.1 Backend Modülleri

#### `config.py` — Yapılandırma Sabitleri

```python
LIBRARY_XML    = Path(__file__).parent.parent / "data" / "library.xml"
SCHEMA_XSD     = Path(__file__).parent.parent / "data" / "schema.xsd"
REPORT_XSLT    = Path(__file__).parent.parent / "data" / "report.xslt"
INVALID_LIBRARY_XML = Path(__file__).parent.parent / "data" / "invalid_library.xml"
API_KEY        = "library-api-key-dev-2026"
CORS_ORIGINS   = ["http://localhost:3000", "http://127.0.0.1:3000"]
```

Tüm dosya yolları tek noktadan yönetilir — dosya taşınırsa yalnızca bu modül güncellenir.

#### `main.py` — Uygulama Giriş Noktası

| Satır Aralığı | Kod | Açıklama |
|---------------|-----|----------|
| 24–36 | `lifespan()` | Startup: XSD doğrulama, invalid demo, iterparse sayım |
| 39–48 | `FastAPI(...)` | App metadata ve lifespan hook bağlantısı |
| 50–57 | `CORSMiddleware` | Frontend CORS izni + `expose_headers` (X-Total-Count) |
| 59–64 | `include_router(...)` | 5 router: books, members, borrowings, reports, external |
| 67–69 | `health()` | JSON health check (XML değil — kasıtlı istisna) |
| 72–76 | `validation_demo()` | XSD demo JSON endpoint |
| 79–81 | `xml_http_exception_handler` | 401/406 → XML error yanıtı |
| 84–90 | `global_exception_handler` | Yakalanmamış hatalar → 500 XML veya JSON |

Startup log örneği:
```
[INFO] library.xml validation: PASS
[INFO] Valid file check: True
[INFO] Invalid file check (expected fail): True
[INFO] Streaming book count via iterparse: 28
```

#### `auth.py` — Kimlik Doğrulama

```python
class XmlHttpException(Exception):
    def __init__(self, status_code: int, message: str, detail: str):
        self.status_code = status_code
        self.message = message
        self.detail = detail

def require_api_key(x_api_key: str = Header(None)) -> None:
    if x_api_key != API_KEY:
        raise XmlHttpException(401, "Invalid or missing API key", "")

def require_xml_accept(request: Request) -> None:
    accept = request.headers.get("accept", "")
    if "application/xml" not in accept and "*/*" not in accept:
        raise XmlHttpException(406, "Accept must include application/xml", "")
```

FastAPI router'larında `dependencies=[Depends(require_api_key), Depends(require_xml_accept)]` ile bağlanır.

#### `library_rules.py` — İş Kuralları

```python
LOAN_LIMITS: dict[str, int] = {
    "student": 5,
    "faculty": 10,
    "public": 3,
}

LOAN_PERIODS_DAYS: dict[str, int] = {
    "student": 14,
    "faculty": 30,
    "public": 21,
}

def loan_limit(membership_type: str) -> int:
    return LOAN_LIMITS.get(membership_type, 3)

def default_due_date(membership_type: str, from_date=None) -> date:
    start = from_date or date.today()
    return start + timedelta(days=loan_period_days(membership_type))
```

Kullanıldığı yer: `xml_manager.checkout_book()` — ödünç limiti ve vade tarihi hesabı.

Gerçek kütüphane sistemlerindeki (ILS — Integrated Library System) pratiklerini yansıtır: öğrenci 14 günde 5 kitap, akademisyen 30 günde 10 kitap alabilir.

#### `responses.py` + `xml_responses.py` — Yanıt Formatları

```python
# responses.py
def xml_response(content: bytes, status_code: int = 200) -> Response:
    return Response(content=content, media_type="application/xml",
                    status_code=status_code)

def xml_error_response(code: int, message: str, detail: str = "") -> Response:
    return xml_response(build_error_xml(code, message, detail), status_code=code)

# xml_responses.py
def build_error_xml(code: int, message: str, detail: str) -> bytes:
    root = etree.Element("error")
    etree.SubElement(root, "code").text = str(code)
    etree.SubElement(root, "message").text = message
    etree.SubElement(root, "detail").text = detail
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")

def books_collection_xml(books: list, total: int) -> bytes:
    root = etree.Element("books")
    root.set("count", str(len(books)))
    root.set("totalCount", str(total))
    for book in books:
        root.append(copy.deepcopy(book))
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")
```

### 9.2 Router Katmanı

| Router | Dosya | Endpoint Sayısı |
|--------|-------|----------------|
| Kitaplar | `routers/books.py` | 5 (list, get, create, update, delete) |
| Üyeler | `routers/members.py` | 5 |
| Ödünçler | `routers/borrowings.py` | 6 (list, checkout, return, update, delete, get) |
| Raporlar | `routers/reports.py` | 2 (dashboard, xpath) |
| Harici | `routers/external.py` | 1 (enrich) |

**Router'larda ortak POST/PUT pattern:**

```python
body = await request.body()
element = manager.parse_*_xml(body)   # syntax check
try:
    result = manager.add_*(element)   # XSD + business rules + disk
    return xml_response(element_to_bytes(result), status_code=201)
except ValidationError as exc:
    return xml_error_response(400, str(exc), exc.log[:500])
except ValueError as exc:
    return xml_error_response(400, str(exc))
except BookNotFoundError as exc:
    return xml_error_response(404, str(exc))
```

---

## 10. Hata Yönetimi

### 10.1 Hata Tipleri Tablosu

| Hata Tipi | Python Sınıfı | HTTP Kodu | Örnek Mesaj | Yakalandığı Yer |
|-----------|---------------|-----------|-------------|-----------------|
| Bozuk XML sözdizimi | `etree.XMLSyntaxError` → `ValueError` | 400 | Malformed XML: ... | `parse_*_xml`, router |
| XSD ihlali | `ValidationError` | 400 | Schema validation failed | Router `except ValidationError` |
| Kayıt bulunamadı | `BookNotFoundError` / `MemberNotFoundError` / `BorrowingNotFoundError` | 404 | Book not found | Router |
| Geçersiz API key | `XmlHttpException` | 401 | Invalid or missing API key | `main.py` handler |
| Yanlış Accept | `XmlHttpException` | 406 | Accept must include application/xml | `main.py` handler |
| İş kuralı | `ValueError` | 400 | No available copies / loan limit exceeded | Router |
| Dış servis hatası | `httpx.HTTPError` | 502 | External service unavailable | `external.py` |
| Yakalanmamış hata | `Exception` | 500 | Internal server error | Global handler |

### 10.2 Katmanlı Hata Akışı

#### Katman 1 — XML Sözdizimi Kontrolü

```python
# xml_manager.parse_book_xml()
try:
    element = etree.fromstring(xml_bytes)
except etree.XMLSyntaxError as exc:
    raise ValueError(f"Malformed XML: {exc}") from exc
```

XML tagları düzgün kapanmamışsa, karakter encoding hatalıysa ya da XML geçersiz unicode içeriyorsa bu katmanda yakalanır. XSD'ye gerek kalmadan 400 döner.

#### Katman 2 — XSD Şema Doğrulama

```python
# validators.validate_or_raise()
is_valid, log = validate_xml(xml_source)
if not is_valid:
    raise ValidationError("Schema validation failed", log)
```

Sözdizimi doğruysa içerik şemaya uygun mu kontrol edilir. Hata logu `exc.log` alanında saklanır.

#### Katman 3 — Router İstisna Yakalama

```python
# books.py:create_book()
except ValidationError as exc:
    return xml_error_response(400, str(exc), exc.log[:500])
except ValueError as exc:
    return xml_error_response(400, str(exc))
```

XSD hata logu 500 karakterle sınırlandırılmıştır — çok uzun log mesajları yanıtı şişirmesin diye.

#### Katman 4 — Global Exception Handler

```python
# main.py
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    accept = request.headers.get("accept", "")
    if "application/xml" in accept or request.url.path.startswith("/api/v1"):
        return xml_error_response(500, "Internal server error", str(exc))
    return JSONResponse(status_code=500, content={"detail": str(exc)})
```

API path'leri için XML, diğer path'ler için JSON 500 yanıtı döner.

### 10.3 Standart Hata XML Formatı

Her hata yanıtı tutarlı bir `<error>` yapısı döner:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<error>
  <code>400</code>
  <message>Schema validation failed</message>
  <detail>Element 'availableCopies': '-5' is not a valid value
          of the atomic type 'xs:nonNegativeInteger'.</detail>
</error>
```

Frontend `api.ts:handleResponse()` bu yapıyı `DOMParser` ile parse eder, `<message>` ve `<detail>` değerlerini alır ve `XmlErrorBanner` bileşenine iletir.

---

## 11. Frontend XML Akışı

### 11.1 Genel Yapı

Frontend Next.js 15 + React ile geliştirilmiş, TypeScript kullanılmaktadır. Backend ile iletişim tamamen XML üzerinden yürütülür.

**Ana dosyalar:**

| Dosya | Görevi |
|-------|--------|
| `lib/api.ts` | HTTP istemci; `fetch()` ile XML istek gönderme ve yanıt alma |
| `lib/xmlParser.ts` | Browser `DOMParser` ile XML parse; TypeScript nesnelerine dönüştürme |

### 11.2 `lib/api.ts` — HTTP İstemci

**Sabit header'lar:**
```typescript
const XML_HEADERS = {
  "Accept": "application/xml",
  "Content-Type": "application/xml",
};

const AUTH_HEADERS = {
  ...XML_HEADERS,
  "X-API-Key": "library-api-key-dev-2026",
};
```

**Örnek fonksiyon — `fetchBooks()`:**
```typescript
export async function fetchBooks(params?: {
  genre?: string; search?: string; page?: number; limit?: number;
}): Promise<{ books: Book[]; total: number }> {
  const url = buildUrl("/api/v1/books", params);
  const res = await fetch(url, { headers: XML_HEADERS });
  const xml = await handleResponse(res);
  const books = parseBooksXml(xml);
  const total = parseInt(res.headers.get("X-Total-Count") ?? "0");
  return { books, total };
}
```

**`handleResponse()` — Hata XML Parse:**
```typescript
async function handleResponse(res: Response): Promise<string> {
  const text = await res.text();
  if (!res.ok) {
    const doc = new DOMParser().parseFromString(text, "application/xml");
    const message = doc.querySelector("message")?.textContent ?? "Unknown error";
    const detail  = doc.querySelector("detail")?.textContent ?? "";
    throw new ApiError(res.status, message, detail);
  }
  return text;
}
```

### 11.3 `lib/xmlParser.ts` — XML Parse ve Serialize

**Parse — `parseBooksXml()`:**
```typescript
export function parseBooksXml(xml: string): Book[] {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  return Array.from(doc.querySelectorAll("book")).map((el) => ({
    id: el.getAttribute("id") ?? "",
    isbn: el.getAttribute("isbn") ?? "",
    title: el.querySelector("title")?.textContent ?? "",
    author: el.querySelector("author")?.textContent ?? "",
    publisher: el.querySelector("publisher")?.textContent ?? "",
    publicationYear: el.querySelector("publicationYear")?.textContent ?? "",
    availableCopies: parseInt(el.querySelector("availableCopies")?.textContent ?? "0"),
  }));
}
```

**Serialize — `serializeBookToXml()`:**
```typescript
export function serializeBookToXml(data: BookFormData): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<book isbn="${escape(data.isbn)}">
  <title>${escape(data.title)}</title>
  <author>${escape(data.author)}</author>
  <publisher>${escape(data.publisher)}</publisher>
  <categories><category>${escape(data.category)}</category></categories>
  <publicationYear>${data.publicationYear}</publicationYear>
  <availableCopies>${data.availableCopies}</availableCopies>
</book>`;
}
```

`escape()` fonksiyonu `&`, `<`, `>`, `"` karakterlerini XML entity olarak kodlar — XML injection'a karşı koruma.

### 11.4 Sayfa ve Bileşen Yapısı

| Dosya | Görevi |
|-------|--------|
| `app/page.tsx` | Dashboard — kitap/üye/ödünç listesi, silme |
| `app/books/new/page.tsx` | Yeni kitap ekleme formu |
| `app/members/page.tsx` | Üye CRUD — liste, form |
| `app/borrowings/page.tsx` | Ödünç listesi, iade işlemi, yeni ödünç formu |
| `app/enrich/page.tsx` | ISBN zenginleştirme sayfası |
| `app/reports/page.tsx` | XSLT dashboard (iframe) |
| `components/BookForm.tsx` | Form → `serializeBookToXml` → `createBook` |
| `components/MemberForm.tsx` | Üye form bileşeni |
| `components/CheckoutForm.tsx` | `bookRef` + `memberRef` seç → checkout |
| `components/BorrowingList.tsx` | Ödünç listesi ve iade butonu |
| `components/XmlErrorBanner.tsx` | `ApiError` → kullanıcıya hata mesajı gösterimi |
| `components/Navbar.tsx` | Navigasyon çubuğu |
| `components/EnrichPanel.tsx` | ISBN girişi → API çağrısı → form doldurma |

### 11.5 Frontend XML Döngüsü

```
Kullanıcı formu doldurur
    │
    ↓ serializeBookToXml(formData)
XML string (POST body)
    │
    ↓ createBook(xml)  →  POST /api/v1/books
                          X-API-Key header
    │
Backend response XML
    │
    ↓ parseBooksXml(responseXml)
TypeScript Book[] nesnesi
    │
    ↓ React state güncellenir → UI yenilenir
```

---

## 12. Test ve Doğrulama Senaryoları

### 12.1 Postman Koleksiyonu

**Dosya:** `postman/collection.json`

Tüm endpoint'ler için önceden hazırlanmış Postman istekleri mevcuttur. Koleksiyonu import ederek aşağıdaki senaryolar çalıştırılabilir.

### 12.2 Birim Testleri

**Dosya:** `backend/tests/`

| Dosya | Test Kapsamı |
|-------|-------------|
| `tests/conftest.py` | Test fixtures, geçici XML dosyası oluşturma |
| `tests/test_validation.py` | XSD doğrulama başarı/başarısızlık senaryoları |
| `tests/test_circulation.py` | Checkout, iade, limit kontrolleri |

Testleri çalıştırma:
```bash
cd backend
pytest tests/ -v
```

### 12.3 XSD Demo Senaryosu

```
GET http://localhost:8000/api/v1/validation/demo
```

Beklenen yanıt:
```json
{
  "valid_file": "...library.xml",
  "valid_result": true,
  "valid_log": "",
  "invalid_file": "...invalid_library.xml",
  "invalid_result": false,
  "invalid_log": "Element 'category': [facet 'enumeration'] ..."
}
```

### 12.4 API Hata Senaryoları

**Senaryo 1 — Geçersiz ISBN ile Kitap Ekleme:**

```
POST /api/v1/books
Body: <book isbn="BOZUK-ISBN">...</book>
```

Beklenen: HTTP 400 + XML `<error>` — `isbnType` pattern ihlali

---

**Senaryo 2 — API Key Eksik:**

```
POST /api/v1/books
(X-API-Key header yok)
```

Beklenen: HTTP 401 + XML `<error>` — "Invalid or missing API key"

---

**Senaryo 3 — Yanlış Accept Header:**

```
GET /api/v1/books
Accept: application/json
```

Beklenen: HTTP 406 + XML `<error>` — "Accept must include application/xml"

---

**Senaryo 4 — Var Olmayan Kayıt:**

```
GET /api/v1/books/bk-999
Accept: application/xml
```

Beklenen: HTTP 404 + XML `<error>` — "Book not found: id=bk-999"

---

**Senaryo 5 — Stok Bitti Checkout:**

Kalan kopyası 0 olan kitap için ödünç alma isteği.

Beklenen: HTTP 400 + XML `<error>` — "No available copies for book bk-XXX"

---

**Senaryo 6 — Ödünç Limiti Aşımı:**

`student` üye için 6. kitabı ödünç almaya çalışma.

Beklenen: HTTP 400 + XML `<error>` — "Loan limit exceeded: 5/5 for student"

---

**Senaryo 7 — XSLT Dashboard:**

```
GET http://localhost:8000/api/v1/reports/dashboard
```

Beklenen: HTML sayfa — 6 istatistik kartı, 3 tablo. Active Borrowings > 0.

---

**Senaryo 8 — XPath Demo:**

```
GET http://localhost:8000/api/v1/reports/xpath
Accept: application/xml
```

Beklenen: `<xpathResults>` XML — 6 sorgu sonucu.

---

**Senaryo 9 — Open Library Zenginleştirme:**

```
GET http://localhost:8000/api/v1/external/enrich/978-0-14-143951-8
Accept: application/xml
```

Beklenen: `<enrichedBook>` XML — Pride and Prejudice metadata.

---

## 13. Sonuç ve Değerlendirme

### 13.1 Uygulanan XML Teknolojileri

Bu proje, XML ekosisteminin birden fazla bileşenini gerçek bir uygulama bağlamında birbirine bağlayan bir örnek oluşturmaktadır:

| Teknoloji | Kullanım Yeri | Dosya |
|-----------|--------------|-------|
| **XML** | Veri deposu (28 kitap, 9 üye, 12 ödünç) | `library.xml` |
| **XSD** | Tüm yazma işlemlerinde şema doğrulama | `schema.xsd`, `validators.py` |
| **XPath** | Filtreleme, arama, join, sayım | `xpath_queries.py`, `xml_manager.py` |
| **XSLT** | XML → HTML dashboard dönüşümü | `report.xslt`, `xslt_transformer.py` |
| **DOM** | CRUD işlemleri için lxml ağacı | `xml_manager.py` |
| **SAX-like** | `iterparse` ile bellek verimli sayım | `xml_manager.py:stream_books` |
| **XML REST API** | Tüm endpoint'ler `application/xml` | `routers/` |
| **Frontend XML** | `DOMParser` parse + manual serialize | `xmlParser.ts`, `api.ts` |

### 13.2 Mimari Kararların Değerlendirmesi

**Tek gerçeklik kaynağı (`library.xml`):** Tüm teknolojiler aynı dosya üzerinde çalışır; XSD onu doğrular, XPath onu sorgular, XSLT onu dönüştürür, XmlManager onu okur/yazar. Bu tutarlı bir demo ortamı sağlar.

**Çift doğrulama (`validate_or_raise` + `_save_tree`):** Savunmacı programlama pratiği. Element düzeyinde geçen bir değişiklik, belge bütününde tutarsızlık yaratabilir; ikinci kontrol bunu engeller.

**XML-only API (JSON değil):** İçerik müzakeresi (`Accept` header) ve XML hata yanıtları gerçek bir XML servis tasarımını yansıtır. `/health` ve `/validation/demo` kasıtlı JSON istisnalarıdır — ikisinin de açıkça belgelenmiş gerekçeleri vardır.

**`copy.deepcopy` kullanımı:** DOM ağacının orijinali bozulmadan döndürülmesi, çok aşamalı işlemlerde veri güvenliğini sağlar.

### 13.3 Proje Dosya Haritası

```
LibraryManagement/
├── backend/
│   ├── data/
│   │   ├── library.xml           ← Ana veri (28 kitap, 9 üye, 12 ödünç)
│   │   ├── schema.xsd            ← XSD şema kuralları
│   │   ├── report.xslt           ← XSLT → HTML dönüşüm şablonu
│   │   └── invalid_library.xml   ← Bilerek hatalı, XSD demo
│   ├── src/
│   │   ├── main.py               ← FastAPI entry point, startup, global handlers
│   │   ├── config.py             ← Dosya yolları, API key, CORS origins
│   │   ├── auth.py               ← API key + Accept header doğrulama
│   │   ├── validators.py         ← XSD doğrulama (validate_xml, validate_or_raise)
│   │   ├── xml_manager.py        ← DOM + streaming, tüm CRUD
│   │   ├── xpath_queries.py      ← 6 XPath sorgusu + run_all_queries()
│   │   ├── xslt_transformer.py   ← transform_to_html() — lxml XSLT engine
│   │   ├── external_service.py   ← Open Library async entegrasyon
│   │   ├── library_rules.py      ← Ödünç limiti ve süre kuralları
│   │   ├── responses.py          ← xml_response, xml_error_response
│   │   ├── xml_responses.py      ← build_error_xml, collection wrappers
│   │   └── routers/
│   │       ├── books.py          ← 5 endpoint (CRUD)
│   │       ├── members.py        ← 5 endpoint (CRUD)
│   │       ├── borrowings.py     ← 6 endpoint (checkout, return, CRUD)
│   │       ├── reports.py        ← 2 endpoint (dashboard, xpath)
│   │       └── external.py       ← 1 endpoint (enrich)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_validation.py
│   │   └── test_circulation.py
│   └── requirements.txt
├── frontend/
│   ├── app/                      ← Next.js 15 App Router sayfaları
│   │   ├── page.tsx              ← Dashboard
│   │   ├── books/new/page.tsx    ← Yeni kitap
│   │   ├── members/page.tsx      ← Üye CRUD
│   │   ├── borrowings/page.tsx   ← Ödünç/iade
│   │   ├── enrich/page.tsx       ← ISBN zenginleştirme
│   │   └── reports/page.tsx      ← XSLT dashboard iframe
│   ├── components/               ← React bileşenleri
│   │   ├── BookForm.tsx
│   │   ├── MemberForm.tsx
│   │   ├── CheckoutForm.tsx
│   │   ├── BorrowingList.tsx
│   │   ├── EnrichPanel.tsx
│   │   ├── XmlErrorBanner.tsx
│   │   └── Navbar.tsx
│   └── lib/
│       ├── api.ts                ← HTTP istemci (XML)
│       └── xmlParser.ts          ← DOMParser + serialize
├── postman/
│   └── collection.json           ← Hazır API istekleri
├── örneközet.md
└── README.md
```

### 13.4 Çalıştırma Talimatları

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Erişim URL'leri:**

| Servis | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| API Dokümantasyonu (Swagger) | http://localhost:8000/docs |
| XSLT Dashboard | http://localhost:8000/api/v1/reports/dashboard |
| XPath Demo | http://localhost:8000/api/v1/reports/xpath |
| XSD Doğrulama Demo | http://localhost:8000/api/v1/validation/demo |
| Health Check | http://localhost:8000/health |

**API Key:** `library-api-key-dev-2026`

---

*Rapor, `library.xml`, `schema.xsd`, `report.xslt` ve tüm Python/TypeScript kaynak dosyaları analiz edilerek hazırlanmıştır. Belirtilen satır numaraları ve fonksiyon isimleri projenin mevcut kodunu yansıtmaktadır.*

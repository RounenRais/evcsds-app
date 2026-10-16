from pathlib import Path
from datetime import date

from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


OUTPUT = Path(__file__).resolve().parent / "ELEKTRIKLI_ARAC_VERITABANI_SABLONU_V3.xlsx"

NAVY = "17365D"
BLUE = "2F75B5"
TEAL = "168AAD"
GREEN = "548235"
PURPLE = "7030A0"
ORANGE = "C65911"
LIGHT_BLUE = "D9EAF7"
LIGHT_GREEN = "E2F0D9"
LIGHT_YELLOW = "FFF2CC"
LIGHT_GRAY = "F2F2F2"
LIGHT_ORANGE = "FCE4D6"
LIGHT_PURPLE = "E4DFEC"
LIGHT_TEAL = "DDEBF7"
WHITE = "FFFFFF"
THIN = Side(style="thin", color="D9E2F3")


# group, database field, visible Excel header, description, type, unit,
# requirement, decision importance, example
FIELDS = [
    ("Araç Kimliği", "vehicle_id", "Araç Kimliği", "Her araç varyantı için benzersiz ve değişmez kimlik.", "Metin", "", "Zorunlu", "Kritik", "TR_MARKA_MODEL_VERSIYON_2026"),
    ("Araç Kimliği", "marka", "Marka", "Aracın üretici/marka adı.", "Metin", "", "Zorunlu", "Kritik", "Örnek Marka"),
    ("Araç Kimliği", "model", "Model", "Aracın ticari model adı.", "Metin", "", "Zorunlu", "Kritik", "Örnek Model"),
    ("Araç Kimliği", "versiyon", "Versiyon", "Batarya, çekiş ve şarj donanımını ayıran tam versiyon.", "Metin", "", "Zorunlu", "Kritik", "Uzun Menzil AWD"),
    ("Araç Kimliği", "model_yili_baslangic", "Başlangıç Model Yılı", "Bu teknik özelliklerin geçerli olmaya başladığı model yılı.", "Tam sayı", "yıl", "Zorunlu", "Kritik", 2026),
    ("Araç Kimliği", "model_yili_bitis", "Bitiş Model Yılı", "Geçerliliğin bittiği model yılı; devam ediyorsa boş bırakılır.", "Tam sayı", "yıl", "İsteğe bağlı", "Destekleyici", ""),
    ("Araç Kimliği", "pazar", "Satış Pazarı", "Teknik özelliklerin geçerli olduğu pazar.", "Liste", "", "Zorunlu", "Kritik", "Türkiye"),
    ("Araç Kimliği", "arac_tipi", "Araç Tipi", "Bataryalı elektrikli veya şarj edilebilir hibrit ayrımı.", "Liste", "", "Zorunlu", "Kritik", "BEV"),
    ("Araç Kimliği", "uretim_durumu", "Üretim / Satış Durumu", "Varyantın güncel üretim ve satış durumu.", "Liste", "", "İsteğe bağlı", "Destekleyici", "Satışta"),
    ("Araç Kimliği", "varyant_notu", "Varyant Notu", "Paket, jant veya pazar farklılığı gibi açıklamalar.", "Metin", "", "İsteğe bağlı", "Destekleyici", ""),

    ("AC Şarj — Kritik", "ac_konnektor_tipi", "AC Konnektör", "Araç üzerindeki AC şarj bağlantı tipi.", "Liste", "", "Zorunlu", "Kritik", "Type 2"),
    ("AC Şarj — Kritik", "ac_azami_guc_kw", "Azami AC Güç", "Aracın kabul edebildiği en yüksek AC şarj gücü.", "Ondalık", "kW", "Zorunlu", "Kritik", 11.0),
    ("AC Şarj — Kritik", "ac_desteklenen_fazlar", "Desteklenen Fazlar", "Aracın AC şarjda desteklediği faz yapısı.", "Liste", "", "Zorunlu", "Kritik", "Tek ve üç faz"),
    ("AC Şarj — Kritik", "ac_tek_faz_destegi", "Tek Faz Desteği", "Aracın tek faz AC şarj desteği.", "Liste", "", "Zorunlu", "Kritik", "Evet"),
    ("AC Şarj — Kritik", "ac_tek_faz_azami_guc_kw", "Tek Faz Azami Güç", "Tek faz bağlantıda kabul edilen en yüksek güç.", "Ondalık", "kW", "Koşullu", "Kritik", 7.4),
    ("AC Şarj — Kritik", "ac_tek_faz_azami_akim_a", "Tek Faz Azami Akım", "Tek faz bağlantıda araç girişinin azami akımı.", "Ondalık", "A", "Koşullu", "Kritik", 32.0),
    ("AC Şarj — Kritik", "ac_uc_faz_destegi", "Üç Faz Desteği", "Aracın üç faz AC şarj desteği.", "Liste", "", "Zorunlu", "Kritik", "Evet"),
    ("AC Şarj — Kritik", "ac_uc_faz_azami_guc_kw", "Üç Faz Azami Güç", "Üç faz bağlantıda kabul edilen en yüksek güç.", "Ondalık", "kW", "Koşullu", "Kritik", 11.0),
    ("AC Şarj — Kritik", "ac_uc_faz_faz_basina_akim_a", "Faz Başına Azami Akım", "Üç fazda her bir faz için azami araç giriş akımı.", "Ondalık", "A/faz", "Koşullu", "Kritik", 16.0),
    ("AC Şarj — Kritik", "onboard_charger_opsiyonel_mi", "AC Şarj Donanımı Opsiyonel mi?", "Belirtilen dahili şarj cihazının opsiyon olup olmadığı.", "Liste", "", "Zorunlu", "Kritik", "Hayır"),
    ("AC Şarj — Kritik", "ac_sarj_notu", "AC Şarj Notu", "Paket, ülke veya yazılıma bağlı AC şarj istisnaları.", "Metin", "", "İsteğe bağlı", "Destekleyici", ""),

    ("Batarya ve Tüketim", "batarya_brut_kwh", "Brüt Batarya Kapasitesi", "Bataryanın açıklanan toplam enerji kapasitesi.", "Ondalık", "kWh", "Koşullu", "Destekleyici", 82.0),
    ("Batarya ve Tüketim", "batarya_kullanilabilir_kwh", "Kullanılabilir Batarya", "Şarj süresi hesabında kullanılacak net kapasite.", "Ondalık", "kWh", "Koşullu", "Kritik", 77.0),
    ("Batarya ve Tüketim", "wltp_tuketim_kwh_100km", "WLTP Tüketim", "Resmî birleşik elektrik tüketimi.", "Ondalık", "kWh/100 km", "Koşullu", "Kritik", 17.2),
    ("Batarya ve Tüketim", "wltp_menzil_km", "WLTP Menzil", "Resmî birleşik menzil.", "Ondalık", "km", "Koşullu", "Destekleyici", 520.0),
    ("Batarya ve Tüketim", "test_standardi", "Ölçüm Standardı", "Tüketim ve menzil ölçüm standardı.", "Liste", "", "Zorunlu", "Kritik", "WLTP"),
    ("Batarya ve Tüketim", "batarya_tuketim_notu", "Batarya / Tüketim Notu", "Değer aralığı, jant veya donanım etkisi.", "Metin", "", "İsteğe bağlı", "Destekleyici", ""),

    ("Diğer Şarj Özellikleri", "dc_konnektor_tipi", "DC Konnektör", "Araç üzerindeki DC hızlı şarj bağlantısı.", "Liste", "", "İsteğe bağlı", "İsteğe bağlı", "CCS Combo 2"),
    ("Diğer Şarj Özellikleri", "dc_azami_guc_kw", "Azami DC Güç", "Aracın kabul ettiği tepe DC şarj gücü.", "Ondalık", "kW", "İsteğe bağlı", "İsteğe bağlı", 175.0),
    ("Diğer Şarj Özellikleri", "dc_10_80_sure_dakika", "DC %10–80 Süresi", "Üreticinin belirttiği koşullarda yüzde 10-80 şarj süresi.", "Ondalık", "dakika", "İsteğe bağlı", "İsteğe bağlı", 28.0),
    ("Diğer Şarj Özellikleri", "zamanlanmis_sarj_destegi", "Zamanlanmış Şarj", "Araç üzerinden zamanlanmış şarj desteği.", "Liste", "", "İsteğe bağlı", "Destekleyici", "Evet"),
    ("Diğer Şarj Özellikleri", "v2l_destegi", "V2L Desteği", "Araçtan elektrikli cihaza enerji aktarımı.", "Liste", "", "İsteğe bağlı", "İsteğe bağlı", "Hayır"),
    ("Diğer Şarj Özellikleri", "v2h_destegi", "V2H Desteği", "Araçtan eve enerji aktarımı.", "Liste", "", "İsteğe bağlı", "İsteğe bağlı", "Bilinmiyor"),
    ("Diğer Şarj Özellikleri", "v2g_destegi", "V2G Desteği", "Araçtan şebekeye enerji aktarımı.", "Liste", "", "İsteğe bağlı", "İsteğe bağlı", "Bilinmiyor"),
    ("Diğer Şarj Özellikleri", "sarj_portu_konumu", "Şarj Portu Konumu", "Kablo erişimini etkileyen port konumu.", "Liste", "", "İsteğe bağlı", "Destekleyici", "Sol arka"),

    ("Kaynak ve Doğrulama", "kaynak_tipi", "Kaynak Tipi", "Verinin alındığı kaynağın güvenilirlik sınıfı.", "Liste", "", "Zorunlu", "Kritik", "Üretici teknik föyü"),
    ("Kaynak ve Doğrulama", "kaynak_basligi", "Kaynak Başlığı", "Belge veya web sayfasının adı.", "Metin", "", "Zorunlu", "Kritik", "Teknik Özellikler"),
    ("Kaynak ve Doğrulama", "kaynak_url", "Kaynak Bağlantısı", "Doğrudan üretici veya resmî kaynak bağlantısı.", "URL", "", "Zorunlu", "Kritik", "https://example.com/technical-data"),
    ("Kaynak ve Doğrulama", "erisim_tarihi", "Erişim Tarihi", "Kaynağın son kontrol edildiği tarih.", "Tarih", "", "Zorunlu", "Kritik", "18.07.2026"),
    ("Kaynak ve Doğrulama", "dogrulama_durumu", "Doğrulama Durumu", "Kaydın kaynak kontrol durumu.", "Liste", "", "Zorunlu", "Kritik", "Doğrulandı"),
    ("Kaynak ve Doğrulama", "veri_guven_duzeyi", "Veri Güven Düzeyi", "Kaynağa ve veri uyuşmasına göre güven sınıfı.", "Liste", "", "Zorunlu", "Kritik", "Yüksek"),
    ("Kaynak ve Doğrulama", "kaynak_notu", "Kaynak / Doğrulama Notu", "Çelişki, ikinci kaynak veya opsiyon açıklaması.", "Metin", "", "İsteğe bağlı", "Destekleyici", ""),
]


LISTS = {
    "Satış Pazarı": ["Türkiye", "Avrupa", "Küresel", "Diğer"],
    "Araç Tipi": ["BEV", "PHEV"],
    "Üretim / Satış Durumu": ["Satışta", "Türkiye'de satılmıyor", "Üretimi sona erdi", "Duyuruldu", "Bilinmiyor"],
    "AC Konnektör": ["Type 2", "Type 1", "NACS", "GB/T AC", "Diğer", "Bilinmiyor"],
    "Desteklenen Fazlar": ["Yalnızca tek faz", "Tek ve üç faz", "Bilinmiyor"],
    "Tek Faz Desteği": ["Evet", "Hayır", "Bilinmiyor"],
    "Üç Faz Desteği": ["Evet", "Hayır", "Bilinmiyor"],
    "AC Şarj Donanımı Opsiyonel mi?": ["Evet", "Hayır", "Bilinmiyor"],
    "Ölçüm Standardı": ["WLTP", "EPA", "NEDC", "CLTC", "Üretici beyanı", "Bilinmiyor"],
    "DC Konnektör": ["CCS Combo 2", "CCS Combo 1", "CHAdeMO", "NACS", "GB/T DC", "Diğer", "Yok", "Bilinmiyor"],
    "Zamanlanmış Şarj": ["Evet", "Hayır", "Bilinmiyor"],
    "V2L Desteği": ["Evet", "Hayır", "Bilinmiyor"],
    "V2H Desteği": ["Evet", "Hayır", "Bilinmiyor"],
    "V2G Desteği": ["Evet", "Hayır", "Bilinmiyor"],
    "Şarj Portu Konumu": ["Sol ön", "Sağ ön", "Sol arka", "Sağ arka", "Ön orta", "Arka orta", "Diğer", "Bilinmiyor"],
    "Kaynak Tipi": ["Üretici Türkiye sitesi", "Üretici teknik föyü", "Üretici kullanım kılavuzu", "Üretici uluslararası sitesi", "Resmî kamu verisi", "Tip onay belgesi", "Güvenilir ikincil kaynak"],
    "Doğrulama Durumu": ["Doğrulanmadı", "İkinci kaynak bekleniyor", "Doğrulandı", "Çelişkili"],
    "Veri Güven Düzeyi": ["Yüksek", "Orta", "Düşük"],
}


GROUP_COLORS = {
    "Araç Kimliği": BLUE,
    "AC Şarj — Kritik": ORANGE,
    "Batarya ve Tüketim": GREEN,
    "Diğer Şarj Özellikleri": PURPLE,
    "Kaynak ve Doğrulama": TEAL,
}

GROUP_LIGHT_COLORS = {
    "Araç Kimliği": LIGHT_BLUE,
    "AC Şarj — Kritik": LIGHT_ORANGE,
    "Batarya ve Tüketim": LIGHT_GREEN,
    "Diğer Şarj Özellikleri": LIGHT_PURPLE,
    "Kaynak ve Doğrulama": LIGHT_TEAL,
}

EXAMPLE_VEHICLE = {
    "vehicle_id": "EU_VW_ID3_PRO_S_MATCH_79_2024",
    "marka": "Volkswagen",
    "model": "ID.3",
    "versiyon": "Pro S Match 79 kWh 204 PS",
    "model_yili_baslangic": 2024,
    "model_yili_bitis": None,
    "pazar": "Avrupa",
    "arac_tipi": "BEV",
    "uretim_durumu": "Satışta",
    "varyant_notu": "Volkswagen UK/Avrupa varyantı; Türkiye donanımı olarak yorumlanmamalıdır.",
    "ac_konnektor_tipi": "Type 2",
    "ac_azami_guc_kw": 11.0,
    "ac_desteklenen_fazlar": "Tek ve üç faz",
    "ac_tek_faz_destegi": "Evet",
    "ac_tek_faz_azami_guc_kw": 7.2,
    "ac_tek_faz_azami_akim_a": 32.0,
    "ac_uc_faz_destegi": "Evet",
    "ac_uc_faz_azami_guc_kw": 11.0,
    "ac_uc_faz_faz_basina_akim_a": 16.0,
    "onboard_charger_opsiyonel_mi": "Hayır",
    "ac_sarj_notu": "Güncel varyant sayfası 11 kW AC belirtir; tek/üç faz değerleri Volkswagen ID.3 teknik dokümanlarıyla doğrulanmıştır.",
    "batarya_brut_kwh": None,
    "batarya_kullanilabilir_kwh": 79.0,
    "wltp_tuketim_kwh_100km": 15.7,
    "wltp_menzil_km": 563.0,
    "test_standardi": "WLTP",
    "batarya_tuketim_notu": "Brüt kapasite üretici sayfasında açıkça verilmediği için boş bırakılmıştır. Menzil 350 milden yaklaşık 563 km'ye çevrilmiştir.",
    "dc_konnektor_tipi": "CCS Combo 2",
    "dc_azami_guc_kw": 185.0,
    "dc_10_80_sure_dakika": 26.0,
    "zamanlanmis_sarj_destegi": "Evet",
    "v2l_destegi": "Bilinmiyor",
    "v2h_destegi": "Bilinmiyor",
    "v2g_destegi": "Bilinmiyor",
    "sarj_portu_konumu": "Sağ arka",
    "kaynak_tipi": "Üretici uluslararası sitesi",
    "kaynak_basligi": "Volkswagen ID.3 Technical Data / Pro S Match",
    "kaynak_url": "https://www.volkswagen.co.uk/en/electric-and-hybrid/electric-cars/id3.html/__ui/technical-data.app",
    "erisim_tarihi": date(2026, 7, 18),
    "dogrulama_durumu": "Doğrulandı",
    "veri_guven_duzeyi": "Yüksek",
    "kaynak_notu": "Birincil kaynak Volkswagen UK teknik veri ve donanım sayfalarıdır. Faz değerleri için ayrıca resmî Volkswagen ID.3 teknik dokümanları kontrol edilmiştir.",
}

# Plain-language guidance shown in Alan_Rehberi. Each item explains both what
# the person collecting data should enter and why the field exists.
FIELD_GUIDANCE = {
    "vehicle_id": (
        "Bu araç sürümüne özel, tekrar etmeyen sabit bir kod yazılır. Marka, model, versiyon, pazar ve başlangıç yılı birleştirilebilir; örneğin EU_VW_ID3_PRO_S_MATCH_79_2024. Aynı kod başka bir araçta kullanılmaz ve daha sonra değiştirilmez.",
        "İleride AC şarj, batarya ve kaynak bilgilerinin doğru araç sürümüne bağlanmasını sağlar. Görünen araç adı değişse bile sistem bu sabit kodla kaydı tanır.",
    ),
    "marka": (
        "Aracı üreten veya pazarlayan markanın resmî adı yazılır. Kısaltma veya bayi adı yerine Volkswagen, Renault, Togg gibi doğrudan marka adı kullanılmalıdır.",
        "Kullanıcının araç seçimini marka bazında filtrelemesini ve aynı isimli modellerin farklı üreticilerle karışmamasını sağlar.",
    ),
    "model": (
        "Üreticinin araç için kullandığı ticari model adı yazılır. Paket veya batarya bilgisi bu alana eklenmez; örneğin yalnızca ID.3 yazılır.",
        "Aynı markanın farklı araç ailelerini birbirinden ayırır. Versiyon bilgisiyle birlikte kullanıldığında kesin aracı tanımlar.",
    ),
    "versiyon": (
        "Aracın batarya, çekiş ve donanımını ayıran tam resmî sürüm adı yazılır. Örneğin Pro S Match 79 kWh 204 PS. Long Range, Standard Range, AWD veya RWD gibi farklar mutlaka belirtilmelidir.",
        "Aynı modelin farklı sürümleri farklı batarya ve AC şarj kapasitesine sahip olabilir. Yanlış versiyon seçimi yanlış wallbox gücü önerilmesine yol açabilir.",
    ),
    "model_yili_baslangic": (
        "Bu satırdaki teknik özelliklerin geçerli olmaya başladığı dört haneli model yılı yazılır. Takvim yılı ile model yılı farklıysa üreticinin belirttiği model yılı esas alınır.",
        "Üreticiler aynı modelin şarj donanımını sonraki yıllarda değiştirebilir. Sistem doğru teknik özelliği doğru üretim dönemiyle eşleştirir.",
    ),
    "model_yili_bitis": (
        "Bu özelliklere sahip sürümün son geçerli model yılı biliniyorsa yazılır. Araç hâlâ aynı özelliklerle satılıyorsa veya bitiş yılı bilinmiyorsa hücre boş bırakılır.",
        "Eski ve yeni kasa ya da teknik güncelleme öncesi/sonrası araçların birbirine karışmasını önler.",
    ),
    "pazar": (
        "Teknik özelliklerin geçerli olduğu ülke veya satış bölgesi seçilir. Türkiye verisi bulunuyorsa Türkiye; Avrupa genel verisiyse Avrupa yazılır.",
        "Aynı araç farklı ülkelerde farklı dahili şarj cihazı, batarya veya donanımla satılabilir. Pazar bilgisi bu farkı açıkça gösterir.",
    ),
    "arac_tipi": (
        "BEV, yalnızca batarya ve elektrik motoruyla çalışan tam elektrikli araç için; PHEV ise dışarıdan şarj edilebilen ve ayrıca içten yanmalı motoru bulunan araç için seçilir.",
        "PHEV ve tam elektrikli araçların batarya boyutları ve şarj ihtiyaçları farklıdır. Hesaplamaların doğru araç türüne göre yapılmasını sağlar.",
    ),
    "uretim_durumu": (
        "Aracın hâlen satışta olup olmadığı seçilir. Satışta, Türkiye'de satılmıyor, üretimi sona erdi veya duyuruldu seçeneklerinden uygun olanı kullanılır.",
        "Kullanıcıya güncel araçların gösterilmesini, eski kayıtların ise silinmeden arşivlenmesini sağlar.",
    ),
    "varyant_notu": (
        "Jant boyutu, opsiyon paketi, çekiş sistemi veya ülkeye özel donanım gibi satırdaki değerleri etkileyen açıklamalar yazılır. Normal alanlara sığmayan önemli istisnalar burada belirtilir.",
        "Tek bir sayının hangi koşullarda geçerli olduğunu açıklar ve veriyi inceleyen kişinin yanlış genelleme yapmasını önler.",
    ),
    "ac_konnektor_tipi": (
        "Aracın alternatif akım ile şarj olurken kullandığı fiziksel giriş tipi seçilir. Avrupa ve Türkiye araçlarında çoğunlukla Type 2 görülür. DC konnektörü bu alana yazılmaz.",
        "Wallbox kablosunun veya soketinin araca fiziksel olarak takılıp takılamayacağını belirler.",
    ),
    "ac_azami_guc_kw": (
        "Aracın dahili şarj cihazının kabul edebildiği en yüksek AC güç kW olarak yazılır. Bu değer motor gücü veya DC hızlı şarj gücü değildir; örneğin 11 kW.",
        "Wallbox daha güçlü olsa bile araç bu sınırdan fazlasını kullanamaz. Önerilecek istasyon gücünün araç tarafındaki üst sınırıdır.",
    ),
    "ac_desteklenen_fazlar": (
        "Aracın yalnızca tek faz mı, yoksa hem tek hem üç faz üzerinden mi AC şarj olabildiği seçilir. Sadece azami güç değerine bakılarak tahmin yapılmamalıdır.",
        "Evden çıkarılan faz bilgisiyle aracın elektrik giriş yeteneğini eşleştirmek için kullanılır.",
    ),
    "ac_tek_faz_destegi": (
        "Araç tek fazlı bir elektrik kaynağından AC şarj olabiliyorsa Evet, olamıyorsa Hayır seçilir. Resmî kaynak bulunamazsa Bilinmiyor seçilir.",
        "Tek fazlı bir konutta aracın şarj edilip edilemeyeceğini ve sonraki tek faz güç alanlarının doldurulup doldurulmayacağını belirler.",
    ),
    "ac_tek_faz_azami_guc_kw": (
        "Araç tek faza bağlandığında kabul edebildiği en yüksek AC güç kW olarak yazılır. Araç tek faz desteklemiyorsa veya değer bilinmiyorsa boş bırakılır.",
        "Tek fazlı evde gerçek şarj gücünün araç nedeniyle kaç kW ile sınırlanacağını gösterir; genel 11 kW veya 22 kW değerinden farklı olabilir.",
    ),
    "ac_tek_faz_azami_akim_a": (
        "Araç tek fazda en fazla kaç amper kabul ediyorsa A cinsinden yazılır; örneğin 32 A. Güç değerinden tahmin edildiyse kaynak notunda bunun hesaplandığı belirtilmelidir.",
        "Sayaç ve tesisatın akım kapasitesiyle doğrudan karşılaştırma yapılmasını ve wallbox akım ayarının sınırlandırılmasını sağlar.",
    ),
    "ac_uc_faz_destegi": (
        "Araç üç fazlı bir kaynaktan AC şarj olabiliyorsa Evet, olamıyorsa Hayır seçilir. Belge bulunamazsa Bilinmiyor seçilir.",
        "Üç fazlı altyapının araç tarafından gerçekten kullanılıp kullanılamayacağını belirler.",
    ),
    "ac_uc_faz_azami_guc_kw": (
        "Araç üç faza bağlandığında kabul edebildiği toplam en yüksek AC güç kW olarak yazılır; örneğin 11 kW. Üç faz desteği yoksa boş bırakılır.",
        "Üç fazlı evde önerilebilecek wallbox gücünün araç tarafındaki üst sınırını gösterir.",
    ),
    "ac_uc_faz_faz_basina_akim_a": (
        "Üç fazlı şarj sırasında aracın her bir fazdan kabul ettiği en yüksek akım A/faz olarak yazılır; örneğin 16 A/faz. Toplam üç faz akımı yazılmamalıdır.",
        "Faz başına sigorta, kablo ve yük hesabında doğru akım sınırının kullanılmasını sağlar.",
    ),
    "onboard_charger_opsiyonel_mi": (
        "Yazılan AC güce sahip dahili şarj cihazı araçta standart ise Hayır, ayrıca satın alınan bir donanımsa Evet seçilir. Durum belli değilse Bilinmiyor yazılır.",
        "Aynı isimdeki araçların opsiyon nedeniyle farklı AC güçlere sahip olabileceğini gösterir ve kullanıcıdan donanım doğrulaması istenmesini sağlar.",
    ),
    "ac_sarj_notu": (
        "AC şarj gücünün pakete, ülkeye, yazılıma veya üretim tarihine göre değiştiği durumlar açık bir cümleyle yazılır. Hesapla bulunan akım değerleri de burada belirtilir.",
        "Kritik şarj değerlerinin hangi koşullarda geçerli olduğunu açıklar ve yanlış kesinlik verilmesini önler.",
    ),
    "batarya_brut_kwh": (
        "Bataryanın üretici tarafından açıklanan toplam teorik enerji kapasitesi kWh olarak yazılır. Bu değer, sürücünün tamamını kullanabildiği enerji değildir.",
        "Bataryanın fiziksel toplam boyutunu kaydeder. Kullanılabilir kapasite açıklanmadığında karşılaştırma için yardımcı olur ancak şarj süresi hesabında ilk tercih değildir.",
    ),
    "batarya_kullanilabilir_kwh": (
        "Sürücünün normal kullanımda şarj edip boşaltabildiği net enerji kapasitesi kWh olarak yazılır. Üretici net veya usable capacity diyebilir.",
        "Belirli bir doluluk aralığının kaç kWh enerji gerektirdiğini ve yaklaşık evde şarj süresini hesaplamak için kullanılır.",
    ),
    "wltp_tuketim_kwh_100km": (
        "Aracın WLTP birleşik testinde 100 km'de tükettiği elektrik kWh/100 km olarak yazılır. Bir aralık verilmişse seçilen kesin varyanta uygun değer kullanılmalıdır.",
        "Kullanıcının günlük kilometresinden günlük enerji ihtiyacını ve evde ne kadar süre şarj gerekeceğini hesaplamaya yardımcı olur.",
    ),
    "wltp_menzil_km": (
        "Tam dolu bataryayla WLTP testine göre gidilebilen birleşik mesafe kilometre olarak yazılır. Mil cinsindeki değer kullanılıyorsa kilometreye çevrildiği not edilmelidir.",
        "Batarya ve tüketim verilerini kontrol etmeye, ayrıca sonucu kullanıcıya anlaşılır menzil bilgisiyle sunmaya yardımcı olur.",
    ),
    "test_standardi": (
        "Tüketim ve menzilin hangi ölçüm yöntemiyle elde edildiği seçilir; Avrupa için genellikle WLTP kullanılır. Farklı standartların sonuçları doğrudan karıştırılmamalıdır.",
        "Menzil ve tüketim değerlerinin aynı koşullarda karşılaştırılmasını sağlar.",
    ),
    "batarya_tuketim_notu": (
        "Jant, donanım, sıcaklık veya kaynakta verilen değer aralığı gibi batarya ve tüketim sonucunu etkileyen ayrıntılar yazılır.",
        "Resmî test değerinin gerçek kullanımda neden değişebileceğini ve seçilen sayının hangi varyanta ait olduğunu açıklar.",
    ),
    "dc_konnektor_tipi": (
        "Aracın hızlı doğru akım şarjında kullandığı bağlantı tipi seçilir; Avrupa araçlarında çoğunlukla CCS Combo 2 bulunur. Type 2 AC bilgisiyle karıştırılmamalıdır.",
        "Bu proje ev tipi AC şarja odaklandığı için ikincil bilgidir; ileride genel şarj uyumluluğu gösterilecekse kullanılır.",
    ),
    "dc_azami_guc_kw": (
        "Aracın hızlı DC istasyondan kısa süreli olarak kabul edebildiği en yüksek güç kW olarak yazılır. Ortalama DC hız veya AC güç bu alana yazılmaz.",
        "Ev tipi wallbox seçimini doğrudan belirlemez; aracın genel şarj profilini tamamlamak ve kullanıcıya bilgi vermek için tutulur.",
    ),
    "dc_10_80_sure_dakika": (
        "Üreticinin belirttiği uygun sıcaklık ve yeterli güçteki DC istasyon koşullarında bataryanın yüzde 10'dan yüzde 80'e çıkma süresi dakika olarak yazılır.",
        "Hızlı şarj yeteneğini karşılaştırmak için destekleyici bilgidir; evde AC şarj süresi yerine kullanılmaz.",
    ),
    "zamanlanmis_sarj_destegi": (
        "Araç veya üretici uygulaması üzerinden şarjın belirli saatte başlaması ayarlanabiliyorsa Evet seçilir.",
        "Gece tarifesi, düşük bina yükü ve kullanıcının hazır olma saatine göre planlı şarj önerileri geliştirilmesine yardımcı olur.",
    ),
    "v2l_destegi": (
        "Araç bataryasından priz veya adaptör aracılığıyla elektrikli cihaz çalıştırılabiliyorsa Evet seçilir. Bu özellik araçtan eve enerji verme anlamına gelmez.",
        "Gelecekte ek enerji kullanım senaryoları sunmak için tutulur; temel wallbox güç seçiminin zorunlu girdisi değildir.",
    ),
    "v2h_destegi": (
        "Araç bataryasının uygun çift yönlü donanımla bir eve enerji verebildiği üretici tarafından doğrulanıyorsa Evet seçilir.",
        "Gelecekte yedek enerji ve ev enerji yönetimi senaryolarını değerlendirmek için kullanılır; sıradan V2L ile karıştırılmamalıdır.",
    ),
    "v2g_destegi": (
        "Araç bataryasının uygun sistemle elektrik şebekesine enerji geri verebildiği doğrulanıyorsa Evet seçilir. Sadece donanım değil pazar ve yazılım desteği de aranmalıdır.",
        "Gelecekte şebeke destekli çift yönlü şarj önerilerini değerlendirmek için tutulur; mevcut temel öneri için isteğe bağlıdır.",
    ),
    "sarj_portu_konumu": (
        "Araca dışarıdan bakıldığında şarj kapağının bulunduğu yer seçilir; örneğin sağ arka veya sol ön.",
        "Park düzenine göre wallbox yerini ve gerekli kablo uzunluğunu belirlemeye yardımcı olur.",
    ),
    "kaynak_tipi": (
        "Bilginin alındığı kaynağın sınıfı seçilir. Üretici teknik föyü, kullanım kılavuzu veya resmî kamu verisi gibi birincil kaynaklara öncelik verilmelidir.",
        "Verinin ne kadar güvenilir olduğunun değerlendirilmesini ve internet sitesindeki doğrulanmamış bilgilerin resmî verilerden ayrılmasını sağlar.",
    ),
    "kaynak_basligi": (
        "Kullanılan web sayfası, teknik föy veya kılavuzun üzerinde yazan başlık girilir. Sadece üretici adı yazmak yeterli değildir.",
        "Bağlantı daha sonra değişse bile kullanılan belgenin hangisi olduğunun anlaşılmasını sağlar.",
    ),
    "kaynak_url": (
        "Bilginin bulunduğu doğrudan web sayfası veya PDF bağlantısı eksiksiz olarak yazılır. Arama sonucu sayfası yerine mümkün olduğunca asıl belge bağlantısı kullanılmalıdır.",
        "Verinin danışman, araştırmacı veya geliştirici tarafından tekrar kontrol edilebilmesini sağlar.",
    ),
    "erisim_tarihi": (
        "Kaynağın en son açılıp kontrol edildiği gün, ay ve yıl yazılır; örneğin 18.07.2026.",
        "Araç özellikleri ve web sayfaları zamanla değişebildiğinden verinin hangi tarihte geçerli olduğunu gösterir.",
    ),
    "dogrulama_durumu": (
        "Kaydın resmî kaynakla kontrol edilip edilmediği seçilir. Kontrol tamamlanmadıysa Doğrulanmadı veya İkinci kaynak bekleniyor kullanılmalıdır.",
        "Taslak bilgilerin doğrulanmış veri gibi öneri sistemine girmesini önler.",
    ),
    "veri_guven_duzeyi": (
        "Kaynağın resmîliği, varyantın kesin eşleşmesi ve farklı kaynakların uyumuna göre Yüksek, Orta veya Düşük seçilir.",
        "Karar sistemi ileride belirsiz araç verilerinde kesin öneri vermek yerine kullanıcıdan doğrulama isteyebilir.",
    ),
    "kaynak_notu": (
        "İki kaynak arasındaki fark, dönüştürülen birim, hesaplanan değer veya doğrulama sırasında görülen belirsizlik açıklanır.",
        "Veriyi kullanan kişinin sayının kaynağını ve yapılan işlemleri açık biçimde denetlemesini sağlar.",
    ),
}


def style_cell(cell, fill=None, font_color=None, bold=False, size=None):
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    cell.font = Font(color=font_color, bold=bold, size=size)
    cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    cell.alignment = Alignment(vertical="center", wrap_text=True)


def create_guide(wb):
    ws = wb.active
    ws.title = "Kullanim"
    ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:F1")
    ws["A1"] = "Elektrikli Araç Veritabanı – Veri Toplama Şablonu"
    ws["A1"].font = Font(size=18, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 34

    content = [
        ("Amaç", "Araçların ev tipi AC şarj istasyonu seçimini etkileyen özelliklerini, kaynaklarıyla birlikte düzenli biçimde toplamak."),
        ("Kayıt kuralı", "Her satır tek bir marka + model + versiyon + model yılı aralığı + satış pazarı kombinasyonudur."),
        ("En önemli bölüm", "Turuncu AC Şarj sütunlarıdır. Motor gücü ve DC hızlı şarj gücü ev tipi AC istasyon seçiminde temel sınır değildir."),
        ("Bilinmeyen değer", "Sayısal alanlara 0 yazmayın; hücreyi boş bırakın. Liste alanlarında Bilinmiyor seçilebilir."),
        ("Kaynak", "Önce üreticinin Türkiye sitesi, teknik föyü veya kullanım kılavuzu; sonra üreticinin uluslararası resmî kaynağı kullanılmalıdır."),
        ("Kapsam", "Bu dosya yalnızca araç veritabanı yapısı ve veri toplama içindir. Karar destek algoritması veya Supabase bağlantısı içermez."),
        ("Örnek kayıt", "Arac_Veritabani sayfasındaki ilk yeşil satır, görünümü göstermek için resmî kaynaklardan doldurulmuş Volkswagen ID.3 Pro S Match örneğidir."),
    ]
    ws["A3"] = "Konu"
    ws["B3"] = "Açıklama"
    for cell in ws[3]:
        if cell.column <= 2:
            style_cell(cell, NAVY, WHITE, True)
    for row_index, (topic, explanation) in enumerate(content, start=4):
        ws.cell(row_index, 1, topic)
        ws.cell(row_index, 2, explanation)
        style_cell(ws.cell(row_index, 1), LIGHT_BLUE, NAVY, True)
        style_cell(ws.cell(row_index, 2), WHITE)
        ws.row_dimensions[row_index].height = 42

    ws["A12"] = "Renk"
    ws["B12"] = "Anlam"
    style_cell(ws["A12"], NAVY, WHITE, True)
    style_cell(ws["B12"], NAVY, WHITE, True)
    legend = [
        ("Turuncu bölüm", "Şarj istasyonu eşleştirmesi için kritik AC araç özellikleri", ORANGE),
        ("* işareti", "Her araç kaydında doldurulması gereken zorunlu alan", LIGHT_YELLOW),
        ("(koşullu)", "Yalnızca ilgili özellik araçta destekleniyorsa doldurulacak alan", LIGHT_BLUE),
        ("İşaretsiz", "İsteğe bağlı veya destekleyici alan", LIGHT_GRAY),
    ]
    for row_index, (name, meaning, color) in enumerate(legend, start=13):
        ws.cell(row_index, 1, name)
        ws.cell(row_index, 2, meaning)
        style_cell(ws.cell(row_index, 1), color, NAVY, True)
        style_cell(ws.cell(row_index, 2), WHITE)
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 105
    ws.freeze_panes = "A3"


def create_data_sheet(wb):
    ws = wb.create_sheet("Arac_Veritabani")
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 80
    ws.freeze_panes = "E3"

    # Group headings in row 1.
    start = 1
    current_group = FIELDS[0][0]
    for index, field in enumerate(FIELDS, start=1):
        if field[0] != current_group:
            ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=index - 1)
            cell = ws.cell(1, start, current_group)
            style_cell(cell, GROUP_COLORS[current_group], WHITE, True, 12)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            start = index
            current_group = field[0]
    ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=len(FIELDS))
    cell = ws.cell(1, start, current_group)
    style_cell(cell, GROUP_COLORS[current_group], WHITE, True, 12)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # Human-readable headers in row 2. Database names are stored as comments.
    for column, field in enumerate(FIELDS, start=1):
        marker = " *" if field[6] == "Zorunlu" else " (koşullu)" if field[6] == "Koşullu" else ""
        header = ws.cell(2, column, field[2] + marker)
        fill = GROUP_LIGHT_COLORS[field[0]]
        style_cell(header, fill, NAVY, True)
        header.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        header.comment = Comment(
            f"Veritabanı alanı: {field[1]}\n\n{field[3]}\n"
            f"Tür: {field[4]} | Birim: {field[5] or '-'} | Zorunluluk: {field[6]}",
            "EVCSDS",
        )
        width = 18
        if field[1] in {"vehicle_id", "varyant_notu", "ac_sarj_notu", "batarya_tuketim_notu", "kaynak_basligi", "kaynak_url", "kaynak_notu"}:
            width = 28
        ws.column_dimensions[header.column_letter].width = width
    ws.row_dimensions[2].height = 58
    ws.auto_filter.ref = f"A2:{ws.cell(1000, len(FIELDS)).coordinate}"

    # Prepare blank input rows without Excel table objects.
    for row in range(3, 103):
        ws.row_dimensions[row].height = 22
        for column, field in enumerate(FIELDS, start=1):
            cell = ws.cell(row, column)
            cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
            if row % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="FAFCFE")
            if field[4] == "Ondalık":
                cell.number_format = "0.00"
            elif field[4] == "Tam sayı":
                cell.number_format = "0"
            elif field[4] == "Tarih":
                cell.number_format = "dd.mm.yyyy"

    # First row is a real, source-backed example so the intended use is clear.
    for column, field in enumerate(FIELDS, start=1):
        value = EXAMPLE_VEHICLE.get(field[1])
        ws.cell(3, column, value)
        ws.cell(3, column).fill = PatternFill("solid", fgColor=LIGHT_GREEN)
        ws.cell(3, column).alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[3].height = 72

    # Simple inline dropdowns; these do not depend on hidden sheets or named ranges.
    for column, field in enumerate(FIELDS, start=1):
        values = LISTS.get(field[2])
        if not values:
            continue
        formula = '"' + ",".join(values) + '"'
        if len(formula) > 255:
            continue
        validation = DataValidation(type="list", formula1=formula, allow_blank=True)
        validation.error = "Listede bulunan geçerli bir değer seçin."
        validation.errorTitle = "Geçersiz değer"
        ws.add_data_validation(validation)
        letter = ws.cell(2, column).column_letter
        validation.add(f"{letter}3:{letter}1000")

    # Keep optional groups compact when the file first opens.
    optional_start = next(i for i, f in enumerate(FIELDS, 1) if f[0] == "Diğer Şarj Özellikleri")
    optional_end = max(i for i, f in enumerate(FIELDS, 1) if f[0] == "Diğer Şarj Özellikleri")
    ws.column_dimensions.group(
        get_column_letter(optional_start),
        get_column_letter(optional_end),
        outline_level=1,
        hidden=False,
    )


def create_dictionary(wb):
    ws = wb.create_sheet("Alan_Rehberi")
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"
    headers = ["Grup", "Excel Başlığı", "Veritabanı Alanı", "Ne Girilmeli?", "Neden Gerekli?", "Tür", "Birim", "Zorunluluk", "Karar Önemi", "ID.3 Pro S Match Örneği"]
    ws.append(headers)
    for cell in ws[1]:
        style_cell(cell, NAVY, WHITE, True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for field in FIELDS:
        example = EXAMPLE_VEHICLE[field[1]] if field[1] in EXAMPLE_VEHICLE else field[8]
        if example is None or example == "":
            example = "Boş bırakıldı"
        what_to_enter, why_needed = FIELD_GUIDANCE[field[1]]
        ws.append([field[0], field[2], field[1], what_to_enter, why_needed, field[4], field[5], field[6], field[7], example])
    ws.auto_filter.ref = f"A1:J{ws.max_row}"
    widths = [24, 28, 34, 72, 65, 14, 14, 17, 17, 32]
    for column, width in enumerate(widths, start=1):
        ws.column_dimensions[ws.cell(1, column).column_letter].width = width
    for row in range(2, ws.max_row + 1):
        group = ws.cell(row, 1).value
        ws.cell(row, 1).fill = PatternFill("solid", fgColor=GROUP_COLORS[group])
        ws.cell(row, 1).font = Font(color=WHITE, bold=True)
        if ws.cell(row, 8).value == "Zorunlu":
            ws.cell(row, 8).fill = PatternFill("solid", fgColor=LIGHT_YELLOW)
        elif ws.cell(row, 8).value == "Koşullu":
            ws.cell(row, 8).fill = PatternFill("solid", fgColor=LIGHT_BLUE)
        if ws.cell(row, 9).value == "Kritik":
            ws.cell(row, 9).fill = PatternFill("solid", fgColor=LIGHT_GREEN)
        for column in range(1, 11):
            ws.cell(row, column).border = Border(bottom=THIN)
            ws.cell(row, column).alignment = Alignment(vertical="top", wrap_text=column in {1, 2, 3, 4, 5, 10})
        ws.row_dimensions[row].height = 82
    ws.row_dimensions[1].height = 32


def create_workbook():
    wb = Workbook()
    create_guide(wb)
    create_data_sheet(wb)
    create_dictionary(wb)
    wb.active = 1
    wb.save(OUTPUT)


def verify_workbook():
    wb = load_workbook(OUTPUT, read_only=False, data_only=False)
    expected = ["Kullanim", "Arac_Veritabani", "Alan_Rehberi"]
    if wb.sheetnames != expected:
        raise RuntimeError(f"Beklenmeyen sayfa yapısı: {wb.sheetnames}")
    if wb["Arac_Veritabani"].max_column != len(FIELDS):
        raise RuntimeError("Veri giriş sütun sayısı doğrulanamadı.")
    if wb["Alan_Rehberi"].max_row - 1 != len(FIELDS):
        raise RuntimeError("Alan rehberi doğrulanamadı.")
    # V2 intentionally contains no table objects; the previous repair warning
    # was caused by Excel removing incompatible table/autofilter definitions.
    if any(ws.tables for ws in wb.worksheets):
        raise RuntimeError("Çalışma kitabında beklenmeyen Excel tablo nesnesi var.")
    wb.close()


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    create_workbook()
    verify_workbook()
    print(OUTPUT)

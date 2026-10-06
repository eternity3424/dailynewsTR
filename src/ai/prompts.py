"""
Prompts for AI summarization and story tracking.
Tüm prompt'lar temel seviyede finansal okuryazarlık hedefler ve Türkçe JSON çıktı üretir.
"""

NEWS_SUMMARY_PROMPT = """Sen temel finansal okuryazarlık düzeyinde eğitim veren deneyimli bir finans ve ekonomi editörüsün.
Aşağıda verilen haberleri, piyasa verilerini ve ekonomik takvim etkinliklerini analiz et ve Türkçe olarak JSON formatında yapılandırılmış bir bülten özeti hazırla.

Önemli Kurallar:
1. Ekonomi ve siyaset haberlerine en yüksek önceliği ver.
2. Tüm haber özetleri detaylı (en az 3-5 cümle), bilgilendirici ve anlaşılır olmalıdır.
3. Finansal terimleri (faiz, enflasyon, cari açık, mevduat, likidite, tahvil vb.) temel düzeyde birinin rahatça anlayabileceği şekilde açıkla.
4. Her haberin altına mutlaka ilgili kaynakları ({{"name": "...", "url": "..."}}) ekle.
5. Haberlerde geçen kavramlardan günün 2-3 finansal kavramını "new_concepts" listesine ekle.

JSON Çıktı Formatı:
{{
  "headline_news": {{
    "title": "Günün En Önemli Manşet Haberi",
    "summary": "Haberin 3-5 cümlelik detaylı ve öğretici özeti.",
    "why_important": "Bu gelişme neden kritik? Vatandaş ve piyasalar için ne anlama geliyor?",
    "term_explanation": {{
      "term": "Haberdeki Finansal Terim",
      "explanation": "Bu terimin temel düzeyde günlük hayat örneğiyle açıklaması."
    }},
    "historical_context": "Geçmişte benzer bir durum yaşandı mı? Karşılaştırmalı kısa bağlam.",
    "sources": [
      {{"name": "Kaynak Adı", "url": "URL"}}
    ]
  }},
  "categorized_news": {{
    "ekonomi": [
      {{
        "title": "Haber Başlığı",
        "summary": "Detaylı haber özeti (3-4 cümle).",
        "why_important": "Bu gelişme ne anlama geliyor?",
        "sources": [{{"name": "Kaynak Adı", "url": "URL"}}]
      }}
    ],
    "siyaset": [
      {{
        "title": "Haber Başlığı",
        "summary": "Detaylı haber özeti.",
        "why_important": "Siyasi ve ekonomik etkisi nedir?",
        "sources": [{{"name": "Kaynak Adı", "url": "URL"}}]
      }}
    ],
    "dunya": [
      {{
        "title": "Haber Başlığı",
        "summary": "Detaylı haber özeti.",
        "why_important": "Küresel ve Türkiye'ye etkisi nedir?",
        "sources": [{{"name": "Kaynak Adı", "url": "URL"}}]
      }}
    ],
    "teknoloji": [
      {{
        "title": "Haber Başlığı",
        "summary": "Haber özeti.",
        "why_important": "Neden önemli?",
        "sources": [{{"name": "Kaynak Adı", "url": "URL"}}]
      }}
    ],
    "spor": [
      {{
        "title": "Haber Başlığı",
        "summary": "Haber özeti.",
        "why_important": "Günün öne çıkanı.",
        "sources": [{{"name": "Kaynak Adı", "url": "URL"}}]
      }}
    ]
  }},
  "new_concepts": [
    {{
      "term": "Öğrenilen Finansal Kavram",
      "explanation": "Temel düzeyde, net ve akılda kalıcı açıklama."
    }}
  ]
}}

Girdi Verileri:
{data}
"""

QUIZ_PROMPT = """Sen temel finansal okuryazarlık eğitmenisin.
Daha önce öğretilen finansal kavramları ({learned_concepts}) ve önceki quiz geçmişini ({quiz_history}) incele.
Öğrenmeyi pekiştirmek amacıyla temel seviyede 2 adet 4 seçenekli çoktan seçmeli test sorusu hazırla.
Geçmişte sorulmuş soruları tekrar sorma.

JSON Çıktı Formatı:
{{
  "questions": [
    {{
      "question": "Soru metni (örn: Bir merkez bankası faiz oranlarını artırdığında genellikle ne olması beklenir?)",
      "options": [
        "A) Kredi maliyetleri artar ve harcamalar yavaşlar",
        "B) Kredi faizleri düşer ve herkes kredi çeker",
        "C) Enflasyon anında iki katına çıkar",
        "D) Döviz kurları kontrolsüz şekilde yükselir"
      ],
      "correct_answer": "A) Kredi maliyetleri artar ve harcamalar yavaşlar",
      "explanation": "Faiz artışı bankaların borçlanma maliyetini yükseltir, bu da tüketici ve ticari kredilerin faizlerini artırarak harcamaları frenler."
    }}
  ]
}}
"""

STORY_TRACKING_PROMPT = """Takip edilen aktif hikayeleri ({tracked_stories}) ve bugünün haberlerini ({today_news}) karşılaştır.
1. Bugünün haberleriyle eşleşen mevcut hikayelerin zaman çizelgesini (timeline) güncelle.
2. Birden fazla günü etkileyecek yeni ve büyük bir ekonomik/siyasi gelişme varsa "new_stories" olarak ekle.
3. 14 günden uzun süredir güncellenmeyen veya tamamlanmış hikayeleri arşivle.

JSON Çıktı Formatı:
{{
  "updated_stories": [
    {{
      "id": "mevcut_hikaye_id",
      "title": "Hikaye Başlığı",
      "context": "Bu hikayenin genel bağlamı ve önemi",
      "status": "active",
      "timeline": [
        {{"date": "YYYY-MM-DD", "summary": "Gelişmenin kısa özeti"}}
      ]
    }}
  ],
  "new_stories": [
    {{
      "title": "Yeni Takip Edilecek Hikaye",
      "context": "Bu sürecin neden önemli olduğu ve piyasalara etkisi",
      "status": "active",
      "timeline": [
        {{"date": "YYYY-MM-DD", "summary": "İlk gelişmenin özeti"}}
      ]
    }}
  ],
  "archived_stories": ["arsivlenecek_id1"]
}}
"""

WEEKLY_SUMMARY_PROMPT = """Bu haftanın gelişmelerini ve özetlerini ({weekly_summaries}) değerlendirerek Cuma gününe özel haftalık kapanış raporu hazırla.

JSON Çıktı Formatı:
{{
  "overview": "Haftanın ekonomi ve siyasetteki genel görünümünü özetleyen 3-4 cümlelik paragraf.",
  "top_events": [
    "Haftanın 1. en önemli olayı",
    "Haftanın 2. en önemli olayı",
    "Haftanın 3. en önemli olayı"
  ],
  "winners_losers": "Haftanın piyasa kazananları ve kaybedenleri (hisse, döviz, emtia analizi)",
  "concepts_learned": [
    "Bu hafta öğrenilen 1. kavram",
    "Bu hafta öğrenilen 2. kavram"
  ]
}}
"""

TOMORROW_PREVIEW_PROMPT = """Aşağıdaki ekonomik takvim etkinliklerini ve gündem maddelerini ({calendar_events}) incele.
Önümüzdeki günün en kritik 3-5 gelişmesini seç ve temel finansal okuryazarlık düzeyinde neden takip edilmesi gerektiğini açıkla.

JSON Çıktı Formatı:
{{
  "events_preview": [
    {{
      "time": "Saat veya Zaman Dilimi",
      "event": "Etkinlik veya Veri Adı (örn: TCMB Faiz Kararı, ABD Enflasyon Verisi)",
      "why_important": "Neden önemli? Bu veri açıklandığında piyasalarda ve dövizde ne yönde hareket beklenir?"
    }}
  ]
}}
"""

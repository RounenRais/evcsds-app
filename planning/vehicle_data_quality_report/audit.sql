-- 100 araçlık JSON veri seti için raporda kullanılan özet denetim sorguları.
-- SQLite JSON1 ve CLI readfile() işleviyle çalıştırılmıştır.

WITH records AS (
  SELECT value AS r
  FROM json_each(
    CAST(
      readfile('C:/EVCSDS/planning/ELEKTRIKLI_ARAC_VERITABANI_100_ARAC.json')
      AS TEXT
    )
  )
)
SELECT
  COUNT(*) AS records,
  ROUND(
    AVG(
      CASE
        WHEN json_extract(r, '$.ac_azami_guc_kw') IS NOT NULL
         AND TRIM(CAST(json_extract(r, '$.ac_azami_guc_kw') AS TEXT))
             NOT IN ('', 'Bilinmiyor')
        THEN 1.0 ELSE 0
      END
    ),
    2
  ) AS ac_coverage,
  ROUND(
    AVG(
      CASE
        WHEN json_extract(r, '$.wltp_tuketim_kwh_100km') IS NOT NULL
         AND json_extract(r, '$.wltp_menzil_km') IS NOT NULL
        THEN 1.0 ELSE 0
      END
    ),
    2
  ) AS wltp_coverage,
  SUM(
    CASE
      WHEN CAST(json_extract(r, '$.ac_azami_guc_kw') AS REAL) + 0.1
           < MAX(
               COALESCE(
                 CAST(json_extract(r, '$.ac_tek_faz_azami_guc_kw') AS REAL),
                 -1
               ),
               COALESCE(
                 CAST(json_extract(r, '$.ac_uc_faz_azami_guc_kw') AS REAL),
                 -1
               )
             )
      THEN 1 ELSE 0
    END
  ) AS conflicts,
  ROUND(
    AVG(
      CASE
        WHEN json_extract(r, '$.kaynak_tipi') LIKE 'Birincil%'
         AND json_extract(r, '$.dogrulama_durumu')
             <> 'İkinci kaynak bekleniyor'
        THEN 1.0 ELSE 0
      END
    ),
    2
  ) AS verified_rate
FROM records;

WITH records AS (
  SELECT value AS r
  FROM json_each(
    CAST(
      readfile('C:/EVCSDS/planning/ELEKTRIKLI_ARAC_VERITABANI_100_ARAC.json')
      AS TEXT
    )
  )
),
fields(field, json_key, role) AS (
  VALUES
    ('AC azami güç', 'ac_azami_guc_kw', 'Teknik uyumluluk girdisi'),
    ('Tek faz AC güç', 'ac_tek_faz_azami_guc_kw', 'Teknik uyumluluk girdisi'),
    ('Üç faz AC güç', 'ac_uc_faz_azami_guc_kw', 'Teknik uyumluluk girdisi'),
    ('Desteklenen fazlar', 'ac_desteklenen_fazlar', 'Teknik uyumluluk girdisi'),
    ('Tek faz desteği', 'ac_tek_faz_destegi', 'Teknik uyumluluk girdisi'),
    ('Üç faz desteği', 'ac_uc_faz_destegi', 'Teknik uyumluluk girdisi'),
    ('Tek faz azami akım', 'ac_tek_faz_azami_akim_a', 'Teknik uyumluluk girdisi'),
    ('Üç faz faz başına akım', 'ac_uc_faz_faz_basina_akim_a', 'Teknik uyumluluk girdisi'),
    ('AC konektör', 'ac_konnektor_tipi', 'Teknik uyumluluk girdisi'),
    ('Kullanılabilir batarya', 'batarya_kullanilabilir_kwh', 'Kullanıcı ihtiyacı hesabı girdisi'),
    ('Brüt batarya', 'batarya_brut_kwh', 'Yardımcı bilgi'),
    ('WLTP tüketim', 'wltp_tuketim_kwh_100km', 'Kullanıcı ihtiyacı hesabı girdisi'),
    ('WLTP menzil', 'wltp_menzil_km', 'Yardımcı bilgi'),
    ('Zamanlanmış şarj', 'zamanlanmis_sarj_destegi', 'Yardımcı bilgi'),
    ('Araç üzeri AC şarj cihazı opsiyonel', 'onboard_charger_opsiyonel_mi', 'Teknik uyumluluk girdisi')
),
stats AS (
  SELECT
    f.field,
    f.role,
    SUM(
      CASE
        WHEN json_extract(r.r, '$.' || f.json_key) IS NOT NULL
         AND TRIM(CAST(json_extract(r.r, '$.' || f.json_key) AS TEXT))
             NOT IN ('', 'Bilinmiyor')
        THEN 1 ELSE 0
      END
    ) AS filled,
    COUNT(*) AS total
  FROM fields AS f
  CROSS JOIN records AS r
  GROUP BY f.field, f.role
)
SELECT
  field,
  ROUND(filled * 1.0 / total, 2) AS coverage,
  filled,
  total - filled AS missing,
  role
FROM stats
ORDER BY coverage DESC, field;

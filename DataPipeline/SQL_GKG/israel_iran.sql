WITH base AS (
  SELECT
   
    CASE
      WHEN LENGTH(CAST(DATE AS STRING)) = 8  THEN CONCAT(CAST(DATE AS STRING), '000000')
      WHEN LENGTH(CAST(DATE AS STRING)) = 12 THEN CONCAT(CAST(DATE AS STRING), '00')
      ELSE SUBSTR(CAST(DATE AS STRING), 1, 14)
    END AS event_datetime_str,
    
    DocumentIdentifier AS url,
    SourceCommonName AS source_domain,
    TranslationInfo AS translation_info,
    V2Tone,
    V2Themes AS themes,
    V2Persons AS persons,
    V2Organizations AS organizations,
    V2Locations AS locations
  FROM `gdelt-bq.gdeltv2.gkg_partitioned`
  WHERE
    _PARTITIONTIME >= TIMESTAMP('2024-01-04')
    AND _PARTITIONTIME < TIMESTAMP('2025-03-16') 
    
    AND TranslationInfo IS NULL
    AND DocumentIdentifier IS NOT NULL
    AND DocumentIdentifier LIKE 'http%'
),

parsed AS (
  SELECT
    PARSE_TIMESTAMP('%Y%m%d%H%M%S', event_datetime_str) AS event_timestamp,
    DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', event_datetime_str)) AS event_date,
    url,
    source_domain,
    translation_info,

    SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) AS tone_score,
    SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(1)] AS FLOAT64) AS positive_score,
    SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(2)] AS FLOAT64) AS negative_score,
    SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(3)] AS FLOAT64) AS polarity,

    IFNULL(themes, '') AS themes,
    IFNULL(persons, '') AS persons,
    IFNULL(organizations, '') AS organizations,
    IFNULL(locations, '') AS locations
  FROM base
),

filtered AS (
  SELECT 
    'israel_iran' AS event_label,
    *
  FROM parsed
  WHERE
    (
      themes LIKE '%TAX_FNCACT_MILITARY%'
      OR themes LIKE '%WB_635_PEACE_AND_SECURITY%'
      OR themes LIKE '%CRISISLEX_T03_ARMED-CONFLICT%'
      OR themes LIKE '%SANCTIONS%'
      OR themes LIKE '%ARMEDCONFLICT%'
      OR themes LIKE '%WB_2432_FRAGILITY_CONFLICT_AND_VIOLENCE%'
      OR themes LIKE '%EPU_CATS_NATIONAL_SECURITY%'
      OR themes LIKE '%KILL%'
      OR themes LIKE '%DRONES%'
    )
    AND (
          LOWER(persons) LIKE '%netanyahu%'
          OR LOWER(persons) LIKE '%khamenei%'
          OR LOWER(locations) LIKE '%iran%'
          OR LOWER(locations) LIKE '%israel%'
          OR LOWER(organizations) LIKE '%irgc%'
        )
        AND (
          themes LIKE '%DRONES%'
          OR themes LIKE '%KILL%'
          OR themes LIKE '%SANCTIONS%'
          OR themes LIKE '%EPU_CATS_NATIONAL_SECURITY%'
          OR themes LIKE '%TAX_FNCACT_MILITARY%'
        )
),

dedup AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY url
      ORDER BY event_timestamp DESC
    ) AS rn
  FROM filtered
)

SELECT
  event_timestamp,
  event_date,
  url,
  source_domain,
  translation_info,
  tone_score,
  positive_score,
  negative_score,
  polarity,
  themes,
  persons,
  organizations,
  locations
FROM dedup
WHERE rn = 1
ORDER BY event_timestamp ASC

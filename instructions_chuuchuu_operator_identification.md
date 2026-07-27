# Instructions: Chuuchuu operator identification

Reference notes for populating the `operator` (and related `routeType`/service-type) columns on `delay_records`, organized by service category / agency.

## Populate operator column

### For Highspeed services

```sql
UPDATE delay_records
SET operator = (
  CASE
    WHEN "routeType" = 'ICE' THEN 'Deutsche Bahn'
    WHEN "routeType" IN (
      'TGV', 'TGV INOUI', 'TGV Lyria', 'LYR', 'LYRIA', 'Ouigo', 'OUI'
    ) THEN 'SNCF'
    WHEN "routeType" IN ('RJX', 'rjx') THEN 'OEBB'
    WHEN "routeType" = 'FR' THEN 'Trenitalia'
    WHEN "routeType" IN ('EST', 'EUR', 'Eurostar') THEN 'Eurostar'
    WHEN "routeType" = 'Italo' THEN 'Italo'
  END
)
WHERE "routeType" IN (
  'ICE',
  'TGV', 'TGV INOUI', 'TGV Lyria', 'LYR', 'LYRIA', 'Ouigo', 'OUI',
  'RJX', 'rjx',
  'FR',
  'EST', 'EUR', 'Eurostar',
  'Italo'
);
```

### For night train services

- `NJ` or `Nightjet`: **OEBB**
- `ES` or `European Sleeper`: **European Sleeper**
- `EN`: depends on route number (see table below)

| Route number(s) | Operator | Route |
| --- | --- | --- |
| 344, 345, 346, 13471, 13472 | SJ | SJ Berlin - Malmö - Stockholm |
| 40465, 40414, 40237, 414, 415 | HZ | Euronight Zagreb - Stuttgart/Zurich |
| 406, 407, 40417, 40416, 40407, 1276, 1277 | PKP | Euronight Warsaw - Munich |
| 40458, 40459, 443, 442 | Ceske Drahy | Breclav - Vienna / Praha - Zurich |
| 40462, 40467, 50237, 50462, 40476, 40457, 40406, 462, 476, 477, 463 | MAV | Euronight (Budapest - Berlin/Zurich/Stuttgart)* |
| 294 (NJ), 295 (NJ), 13485 (NJ), 233 (NJ) | OEBB | |

Transform `EN` into `NJ` routes:

```sql
UPDATE delay_records
SET "routeType" = 'NJ'
WHERE UPPER(TRIM("routeType")) = 'EN'
  AND TRIM("routeNumber") IN ('294', '295', '13485', '233');
```

Set operator for all night trains:

```sql
UPDATE delay_records
SET operator = 'European Sleeper'
WHERE UPPER(TRIM("routeType")) IN ('ES', 'EUROPEAN SLEEPER');

UPDATE delay_records
SET operator = 'OEBB'
WHERE UPPER(TRIM("routeType")) IN ('NJ', 'NIGHTJET');
```

```sql
UPDATE delay_records SET operator = 'SJ'
WHERE UPPER(TRIM("routeType")) = 'EN'
  AND TRIM("routeNumber") IN ('344', '345', '346', '13471', '13472');

UPDATE delay_records SET operator = 'HZ'
WHERE UPPER(TRIM("routeType")) = 'EN'
  AND TRIM("routeNumber") IN ('40465', '40414', '40237', '414', '415');

UPDATE delay_records SET operator = 'PKP'
WHERE UPPER(TRIM("routeType")) = 'EN'
  AND TRIM("routeNumber") IN ('406', '407', '40417', '40416', '40407', '1276', '1277');

UPDATE delay_records SET operator = 'Ceske Drahy'
WHERE UPPER(TRIM("routeType")) = 'EN'
  AND TRIM("routeNumber") IN ('40458', '40459', '443', '442');

UPDATE delay_records SET operator = 'MAV'
WHERE UPPER(TRIM("routeType")) = 'EN'
  AND TRIM("routeNumber") IN (
    '40462', '40467', '50237', '50462', '40476', '40457',
    '40406', '462', '476', '477', '463'
  );
```

**No information on operator for these `EN` route numbers:**

```
1415
1153, 1152 (Bratislava – Vienna – Graz – Maribor – Split)
50476
323
13400, 13403, 13451, 13408, 13401, 13402, 13404, 13406, 13420, 13405, 13409, 13417
93701
319
580, 230, 320
34834, 91641, 91505, 32
277, 37501, 89843, 89962, 11799
28565, 28960, 370, 20159
```

### Railjet (ÖBB or CD?)

Based on this list: https://www.vagonweb.cz/razeni/razeni.php?zeme=ČD&kategorie=RJ&rok=2026

```sql
UPDATE delay_records
SET operator = CASE
  WHEN TRIM("routeNumber") IN (
    '50', '51', '52', '53', '54', '55', '56',
    '70', '71', '72', '73', '74', '75', '78', '79',
    '170', '171', '172', '173', '174', '175', '176', '177', '178', '179',
    '244', '250', '251', '252', '253', '254', '255', '256', '257', '258', '259',
    '270', '271', '272', '273', '274', '275', '276', '277',
    '284', '285',
    '370', '371', '372', '373', '374', '375',
    '382', '383', '384', '385', '386', '387',
    '478', '479',
    '512', '515',
    '548', '549',
    '576', '577', '578', '579',
    '644', '645'
  ) THEN 'Ceske Drahy'
  ELSE 'OEBB'
END
WHERE UPPER(TRIM("routeType")) = 'RJ';
```

### Easy operator cases

Agency = PL then operator = PKP Intercity

```sql
UPDATE delay_records
SET operator = 'PKP Intercity'
WHERE agency = 'PL';
```

Routetype = FLX then operator = Flixtrain

```sql
UPDATE delay_records
SET operator = 'Flixtrain'
WHERE UPPER(TRIM("routeType")) = 'FLX';
```

Agency = HU and routetype = EC, IC, Ex, EN, G, Gy, ER, H, IR, S, Sz, Z then operator = MAV

```sql
UPDATE delay_records
SET operator = 'MAV'
WHERE UPPER(TRIM(agency)) = 'HU'
  AND UPPER(TRIM("routeType")) IN (
    'EC', 'IC', 'EX', 'EN', 'G', 'GY', 'ER', 'H', 'IR', 'S', 'SZ', 'Z'
  );
```

Agency = IT and routetype = FR, FA, FB, IC, ICN, EXP, IR, REG, MET, EN, EXP, NCL then operator = Trenitalia

```sql
UPDATE delay_records
SET operator = 'Trenitalia'
WHERE UPPER(TRIM(agency)) = 'IT'
  AND UPPER(TRIM("routeType")) IN (
    'FR', 'FA', 'FB', 'IC', 'ICN', 'EXP', 'IR', 'REG', 'MET', 'EN', 'NCL'
  );
```

Agency = FR and routetype = IC, ICN, INTERCITES, INTERCITES DE NUIT, LYR, LYRIA, NAV, NAVETTE, OGO, OUI, OUIGO, TER, TGV INOUI, TRAIN TER then operator = SNCF

```sql
UPDATE delay_records
SET operator = 'SNCF'
WHERE UPPER(TRIM(agency)) = 'FR'
  AND UPPER(TRIM("routeType")) IN (
    'IC',
    'ICN',
    'INTERCITES',
    'INTERCITES DE NUIT',
    'LYR',
    'LYRIA',
    'NAV',
    'NAVETTE',
    'OGO',
    'OUI',
    'OUIGO',
    'TER',
    'TGV INOUI',
    'TRAIN TER'
  );
```

### SBB agency

List all routetypes per operator in current record collection:

```sql
SELECT TRIM("routeType") AS routetype,
       COALESCE(operator, '(NULL)') AS operator,
       COUNT(*) AS cnt
FROM delay_records
WHERE UPPER(TRIM(agency)) = 'SBB'
  AND date > '2026-05-04'
GROUP BY TRIM("routeType"), operator
ORDER BY cnt DESC, routetype, operator;
```

**IC, EC:** always if they're inside Switzerland

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE "routeType" IN ('IC', 'EC')
  AND stopcountry = 'CH';
```

**IR:** sometimes depending on routenumber

Analyse routenumber / operator connection in current delay records:

```sql
SELECT
  operator,
  STRING_AGG(DISTINCT "routeNumber", ',' ORDER BY "routeNumber") AS route_numbers
FROM delay_records
WHERE agency = 'SBB'
  AND "routeType" = 'IR'
  AND date >= '2026-05-05'
GROUP BY operator
ORDER BY operator;
```

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'SBB'
  AND "routeType" = 'IR'
  AND (
    -- 1651–1843 block
    "routeNumber" IN ('1651','1652','1653','1654','1656','1658','1662','1671','1673','1674','1675','1676','1677','1678')
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 1702 AND 1843)
    -- 1900–2292 block
    OR "routeNumber" IN ('1900','1902','1904','1910','1929','1943','1945')
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 1956 AND 1995)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2055 AND 2194)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2252 AND 2292)
    -- 2306–2394 block (excluding SOB overlaps)
    OR "routeNumber" IN ('2306','2344','2354','2357','2358','2361','2366','2370','2374','2379','2381','2388','2390','2392','2393','2394')
    -- 2456–2662 block
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2456 AND 2493)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2503 AND 2543)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2562 AND 2599)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2610 AND 2662)
    -- 3016–3293 block (excluding Zentralbahn)
    OR "routeNumber" IN ('3016','3017','3022','3024','3026','3029','3030','3110')
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 3251 AND 3293)
    -- Outliers
    OR "routeNumber" IN ('746','749')
  );
```

**R:** sometimes

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'SBB'
  AND "routeType" = 'R'
  AND (
    -- 14xxx block (unique to SBB)
    (CAST("routeNumber" AS INTEGER) BETWEEN 14402 AND 14693)
    -- 17xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 17400 AND 17497)
    -- 18xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 18940 AND 18999)
    -- 23xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 23000 AND 23535)
    -- 24xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 24004 AND 24999)
    -- 25xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 25850 AND 25864)
    -- 26xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 26101 AND 26370)
    -- 5xxx block excluding Chemins de fer du Jura overlaps (5185, 5186, 5190, 5191)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 5607 AND 5994)
    -- 6xxx block excluding BLS overlaps (6759–6845)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 6006 AND 6758)
    -- 7xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 7014 AND 7461)
    -- 9901–9940 block excluding Zentralbahn overlaps (9054–9160)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 9901 AND 9940)
  );
```

**RE:** sometimes

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'SBB'
  AND "routeType" = 'RE'
  AND (
    -- 18xxx block
    (CAST("routeNumber" AS INTEGER) BETWEEN 18122 AND 18495)
    -- 25xxx block
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 25500 AND 25843)
    -- Small SBB-specific numbers
    OR "routeNumber" IN ('2087','2089','2090','2092','2560')
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 2600 AND 2607)
    -- 3564–3685 block
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 3564 AND 3685)
    -- 3958–3995 block
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 3958 AND 3995)
    -- 4706–4842 block excluding Rhätische Bahn overlaps (4717–4761 range)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 4706 AND 4716)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 4762 AND 4842)
    -- 4908–4940 block (no overlaps)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 4908 AND 4940)
    -- Outliers
    OR "routeNumber" IN ('741','742','744')
  );
```

**S:** sometimes

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'SBB'
  AND "routeType" = 'S'
  AND (
    -- 14xxx block (unique to SBB)
    (CAST("routeNumber" AS INTEGER) BETWEEN 14303 AND 14398)
    -- 17xxx block (unique to SBB, excluding overlaps with BLS in 17xxx)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 17001 AND 17099)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 17113 AND 17394)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 17525 AND 17568)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 17906 AND 17943)
    -- 18xxx block (excluding SOB overlaps 18021-18066)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 18011 AND 18020)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 18087 AND 18093)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 18220 AND 18993)
    -- 19xxx block (excluding SBB GmbH 19700-19776 and SOB 19315-19394 and THURBO 19816-19895)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 19010 AND 19293)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 19416 AND 19693)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 19921 AND 19980)
    -- 20xxx block (excluding THURBO 20613-20698 and 20815-20996)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 20024 AND 20580)
    -- 21xxx block (excluding BLS 21613-21795 and Zentralbahn 21417-21594)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 21016 AND 21395)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 21912 AND 21997)
    -- 22xxx block (excluding BLS 22613-22792 and Zentralbahn 22401-22573)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 22015 AND 22175)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 22960 AND 22991)
    -- 24xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 24500 AND 24697)
    -- 25xxx block (excluding THURBO 25880-25897)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 25100 AND 25792)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 25905 AND 25993)
    -- 26xxx block (unique to SBB)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 26018 AND 26075)
    -- 7xxx block (excluding RBS 7052-7243 and Aargau Verkehr 7109-7683 and Appenzeller 7003-7238)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 7606 AND 7743)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 7819 AND 7892)
    -- 8xxx block (excluding RBS 8051-9210 and SOB 8015-8389 and THURBO 8015-8389)
    OR (CAST("routeNumber" AS INTEGER) BETWEEN 8416 AND 8999)
    -- 30xxx block (excluding BLS 30092-30872)
    OR "routeNumber" IN ('30392','30661','30698','30794','30821','30823','30825',
                         '30827','30829','30831','30833','30835','30837','30839',
                         '30841','30843','30845','30847','30849','30851','30853',
                         '30855','30857','30859','30861','30863','30865','30867',
                         '30869','30871','30873','30949','30967','30985')
  );
```

**SN:** sometimes

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'SBB'
  AND "routeType" = 'SN'
  AND (
    -- 13xxx block excluding THURBO overlaps
    "routeNumber" IN (
      '13702','13704','13707','13709','13710','13711','13712','13713','13714','13715',
      '13716','13717','13746','13748','13750','13751','13752','13753','13754','13755',
      '13756','13757','13760','13762','13763','13764','13765','13766','13767','13769',
      '13770','13771','13772','13773','13774','13775','13776','13777','13780','13781',
      '13782','13783','13784','13785','13786','13787','13790','13791','13792','13793',
      '13794','13795','13796','13797','13811','13812','13813','13814','13815','13816',
      '13818','13830','13831','13832','13834','13835','13836','13837','13838','13839',
      '13840','13841','13842','13843','13844','13845','13846','13847','13849'
    )
    -- SBB GmbH Grenzverkehr outliers
    OR "routeNumber" IN ('87795','87797')
  );
```

- **PE:** no
- **ICE:** no
- **RB:** no

### OEBB agency

```sql
SELECT TRIM("routeType") AS routetype,
       COALESCE(operator, '(NULL)') AS operator,
       COUNT(*) AS cnt
FROM delay_records
WHERE UPPER(TRIM(agency)) = 'OEBB'
  AND date > '2026-05-04'
GROUP BY TRIM("routeType"), operator
ORDER BY cnt DESC, routetype, operator;
```

'Nahreisezug' seems to be the wrong name for ÖBB as operator.

**CJX, D, ER, IR:** always ÖBB

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE "routeType" IN ('CJX', 'D', 'ER', 'IR')
  AND stopcountry = 'AT';
```

**EC** — counts observed: Nahreisezug 2232, DB Fernverkehr AG 788, PKP Intercity 581, Schweizerische Bundesbahnen SBB 560

Find routenumber/operator patterns for EC:

```sql
SELECT
  operator,
  STRING_AGG(DISTINCT "routeNumber", ',' ORDER BY "routeNumber") AS route_numbers
FROM delay_records
WHERE agency = 'OEBB'
  AND "routeType" = 'EC'
  AND date >= '2026-05-05'
GROUP BY operator
ORDER BY operator;
```

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '100','102','106','114','140','141','142','143','144','145',
    '146','147','148','149','164','202','204','206','212','214',
    '290','337','340','341','342','343','462','463','70','71','78','79'
  );

UPDATE delay_records
SET operator = 'DB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '80','81','94','96','98','115','190','192','194','196','198','213','1281'
  );

UPDATE delay_records
SET operator = 'SBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '95','97','99','163','191','193','195','197','199'
  );

UPDATE delay_records
SET operator = 'PKP Intercity'
WHERE stopcountry = 'AT'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '101','103','107','203','205','207'
  );

UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'EC'
  AND "routeNumber" NOT IN (
    '100','102','106','114','140','141','142','143','144','145',
    '146','147','148','149','164','202','204','206','212','214',
    '290','337','340','341','342','343','462','463','70','71','78','79',
    '80','81','94','96','98','115','190','192','194','196','198','213','1281',
    '95','97','99','163','191','193','195','197','199',
    '101','103','107','203','205','207'
  );
```

**EN:** already covered (see night train services section)

**IC** — counts observed: Nahreisezug 4887, DB Fernverkehr AG 295, PKP Intercity 159

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'IC'
  AND "routeNumber" IN ('406','416');

UPDATE delay_records
SET operator = 'PKP Intercity'
WHERE stopcountry = 'AT'
  AND "routeType" = 'IC'
  AND "routeNumber" IN ('207','417');

UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'IC'
  AND "routeNumber" NOT IN ('406','416','207','417');
```

**ICE:** already covered

**NJ:** already covered

**Os** — counts observed: Ceske Drahy 1161, Nahreisezug 99. Treating `Os` as Ceske Drahy exclusively.

**R** — counts observed: Nahreisezug 18105, Stern & Hafferl Verkehrsgesellschaft mbH 3793, SAD Nahverkehr AG/SAD Transporto locale 188, Raaberbahn AG | Raab-Oedenburg-Ebenfurter Eisenbahn AG 114

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'R'
  AND "routeNumber" NOT IN ('7807','1826','1828')
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 8000 AND 8200;
```

**RB** — counts observed: DB Regio AG Bayern 379, DB RegioNetz Verkehrs GmbH Südostbayernbahn 30

**REX** — counts observed: Nahreisezug 48555, Raaberbahn AG | Raab-Oedenburg-Ebenfurter Eisenbahn AG 4238, GKB - Graz-Köflacher Bahn und Busbetrieb GmbH 924, Montafonerbahn AG 56

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'REX'
  AND "routeNumber" != '5572'
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 8450 AND 8600
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 7600 AND 7900;
```

**RJ, RJX:** already covered

**S** — counts observed: Nahreisezug 126961, GKB - Graz-Köflacher Bahn und Busbetrieb GmbH 4935, Montafonerbahn AG 1885, Stern & Hafferl Verkehrsgesellschaft mbH 1615, THURBO 289

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'S'
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 4350 AND 4378
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 7350 AND 7388
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 8000 AND 8544
  AND "routeNumber" NOT IN (
    '5556','5562','5564','5568','5572','5574','5578','5580','5584','5586',
    '5590','5592','5596','5602','5606','5694','25844','25846',
    '25883','25885','25887','25889','25891','25893','25895','25897'
  );
```

**UEX** — counts observed: Urlaubs-Express 10

**WB:** always Westbahn

```sql
UPDATE delay_records
SET operator = 'Westbahn'
WHERE "routeType" IN ('WB')
```

### DB agency

```sql
SELECT TRIM("routeType") AS routetype,
       COALESCE(operator, '(NULL)') AS operator,
       COUNT(*) AS cnt
FROM delay_records
WHERE UPPER(TRIM(agency)) = 'DB'
  AND date > '2026-05-04'
GROUP BY TRIM("routeType"), operator
ORDER BY cnt DESC, routetype, operator;
```

**EC** — counts observed:
- PKP Intercity, DB Fernverkehr AG: 196
- DB Fernverkehr AG, PKP Intercity: 180
- Schweizerische Bundesbahnen, Österreichische Bundesbahnen, DB Fernverkehr AG: 173
- Österreichische Bundesbahnen, DB Fernverkehr AG: 66
- Schweizerische Bundesbahnen, DB Fernverkehr AG, Ceske Drahy: 60
- DB Fernverkehr AG: 54
- Ceske Drahy, DB Fernverkehr AG, Schweizerische Bundesbahnen: 37
- DB Fernverkehr AG, Österreichische Bundesbahnen, HZPP: 36
- DB Fernverkehr AG, Österreichische Bundesbahnen: 30
- Trenitalia, Schweizerische Bundesbahnen, DB Fernverkehr AG: 18
- Österreichische Bundesbahnen, Schweizerische Bundesbahnen: 5

```sql
UPDATE delay_records
SET operator = 'PKP Intercity'
WHERE agency = 'DB'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '231','247','249','41','43','431','45','47','49','55','57','59',
    '230','246','248','40','42','430','44','46','48','54','56','58'
  );

UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'DB'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '150','191','193','195','197','199','95','97','99','458','459'
  );

UPDATE delay_records
SET operator = 'OEBB'
WHERE agency = 'DB'
  AND "routeType" = 'EC'
  AND "routeNumber" IN ('213','115','114','212','290');

UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'DB'
  AND "routeType" = 'EC'
  AND "routeNumber" NOT IN (
    '231','247','249','41','43','431','45','47','49','55','57','59',
    '230','246','248','40','42','430','44','46','48','54','56','58',
    '150','191','193','195','197','199','95','97','99','458','459',
    '213','115','114','212','290'
  );
```

**ECE** — counts observed:
- DB Fernverkehr AG: 242
- DB Fernverkehr AG, Österreichische Bundesbahnen, Schweizerische Bundesbahnen: 164
- Dänische Staatsbahnen, DB Fernverkehr AG: 47
- DB Fernverkehr AG, Schweizerische Bundesbahnen: 24

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'DB'
  AND "routeType" = 'ECE'
  AND "routeNumber" IN ('190','192','194','196','198','94','96','98','151');

UPDATE delay_records
SET operator = 'DB Fernverkehr AG'
WHERE agency = 'DB'
  AND "routeType" = 'ECE'
  AND "routeNumber" NOT IN (
    '190','192','194','196','198','94','96','98','151'
  );
```

**EN, ES, EUR, EST, FLX:** already covered

**GV:** always Govolta

```sql
UPDATE delay_records
SET operator = 'Govolta'
WHERE "routeType" = 'GV';
```

**IC** — counts observed (no operator-assignment rule was provided for this breakdown yet — pending):
- DB Fernverkehr AG: 9143
- Schweizerische Bundesbahnen, DB Fernverkehr AG: 513
- DB Fernverkehr AG, Schweizerische Bundesbahnen: 292
- DB Regio AG Mitte SÜWEX: 80
- PKP Intercity, DB Fernverkehr AG: 55
- Dänische Staatsbahnen: 46
- DB Fernverkehr AG, Österreichische Bundesbahnen, Ceske Drahy, PKP Intercity: 30
- PKP Intercity, Ceske Drahy, Österreichische Bundesbahnen, DB Fernverkehr AG: 30
- Snälltåget: 10

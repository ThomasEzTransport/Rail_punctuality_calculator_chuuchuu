# Instructions: Chuuchuu operator identification

Reference notes for populating the `operator` (and related `routeType`/service-type) columns on `delay_records`, organized by service category / agency.

## Populate operator column

### For Highspeed services
Instructions on how to operator values and service type to records.


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

### **For night train services**

NJ or Nightjet: ‘OEBB’

ES or European Sleeper: ‘European Sleeper’

EN

| Routenumber | Operator | Route |
| --- | --- | --- |
| 344
345
346
13471
13472 | SJ | SJ Berlin - Malmö - Stockholm |
| 40465
40414
40237
414
415 | HZ | Euronight Zagreb - Stuttgart/Zurich |
| 406
407
40417
40416
40407
1276
1277 | PKP | Euronight Warsaw - Munich |
| 40458
40459
443
442 | Ceske Drahy | Breclav - Vienna / Praha - Zurich |
| 40462
40467
50237
50462
40476
40457
40406
462
476
477
463 | MAV | Euronight (Budapest - Berlin/Zurich/Stuttgart)* |
| 294 (NJ)
295 (NJ)
13485 (NJ)
233 (NJ) | OEBB |  |

Transform EN into NJ routes:

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

- No information on operator for these EN numbers:
    
    1415 
    
    1153 1152 Bratislava – Vienna – Graz – Maribor – Split
    50476
    323
    
    13400
    13403
    13451
    13408
    13401
    13402
    13404
    13406
    13420
    13405
    13409
    13417
    
    93701
    
    319
    
    580
    230
    320
    
    34834
    91641
    91505
    32
    
    277
    37501
    89843
    89962
    11799
    
    28565
    28960
    370
    20159
    

### **Railjet (ÖBB or CD?)**

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

### **Easy operator cases**

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

**T&E observation (not from the data provider):** agency FR also reports `CAR TER` (rail-replacement coach service under the TER brand) and `TRAMTRAIN` routeTypes, neither covered by the list above. T&E has confirmed both are SNCF services, so they're included in the operator assignment.

```sql
UPDATE delay_records
SET operator = 'SNCF'
WHERE UPPER(TRIM(agency)) = 'FR'
  AND UPPER(TRIM("routeType")) IN (
    'CAR TER',
    'TRAMTRAIN'
  );
```

### **SBB agency**

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

IC, EC: always if they’re inside Switzerland

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE "routeType" IN ('IC', 'EC')
  AND stopcountry = 'CH';
```

IR: sometimes depending on routenumber

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

R: sometimes

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

RE: sometimes

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

S: sometimes

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

SN: sometimes

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

PE: no

ICE: no

RB: no

### **OEBB agency**

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

‘Nahreisezug’ seems to be the wrong name for ÖBB as operator

CJX: always ÖBB
D: always ÖBB
ER: always ÖBB
IR: always ÖBB

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE "routeType" IN ('CJX', 'D', 'ER', 'IR')
  AND stopcountry = 'AT';
```

EC	Nahreisezug	2232
EC	DB Fernverkehr AG	788
EC	PKP Intercity	581
EC	Schweizerische Bundesbahnen SBB	560

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

EN: already covered

IC	Nahreisezug	4887
IC	DB Fernverkehr AG	295
IC	PKP Intercity	159

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

ICE: already covered

NJ: already covered

Os	Ceske Drahy	1161
Os	Nahreisezug	99

Treating Os as CD exclusively

R	Nahreisezug	18105
R	Stern & Hafferl Verkehrsgesellschaft mbH	3793
R	SAD Nahverkehr AG/SAD Transporto locale	188
R	Raaberbahn AG | Raab-Oedenburg-Ebenfurter Eisenbahn AG	114

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'R'
  AND "routeNumber" NOT IN ('7807','1826','1828')
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 8000 AND 8200;
```

RB	DB Regio AG Bayern	379
RB	DB RegioNetz Verkehrs GmbH Südostbayernbahn	30

REX	Nahreisezug	48555
REX	Raaberbahn AG | Raab-Oedenburg-Ebenfurter Eisenbahn AG	4238
REX	GKB - Graz-Köflacher Bahn und Busbetrieb GmbH	924
REX	Montafonerbahn AG	56

```sql
UPDATE delay_records
SET operator = 'OEBB'
WHERE stopcountry = 'AT'
  AND "routeType" = 'REX'
  AND "routeNumber" != '5572'
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 8450 AND 8600
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 7600 AND 7900;
```

RJ, RJX: already covered

S	Nahreisezug	126961
S	GKB - Graz-Köflacher Bahn und Busbetrieb GmbH	4935
S	Montafonerbahn AG	1885
S	Stern & Hafferl Verkehrsgesellschaft mbH	1615
S	THURBO	289

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

UEX	Urlaubs-Express	10

WB: always Westbahn

```sql
UPDATE delay_records
SET operator = 'Westbahn'
WHERE "routeType" IN ('WB')
```

### **DB agency**

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

EC	PKP Intercity, DB Fernverkehr AG	196
EC	DB Fernverkehr AG, PKP Intercity	180
EC	Schweizerische Bundesbahnen, Österreichische Bundesbahnen, DB Fernverkehr AG	173
EC	Österreichische Bundesbahnen, DB Fernverkehr AG	66
EC	Schweizerische Bundesbahnen, DB Fernverkehr AG, Ceske Drahy	60
EC	DB Fernverkehr AG	54
EC	Ceske Drahy, DB Fernverkehr AG, Schweizerische Bundesbahnen	37
EC	DB Fernverkehr AG, Österreichische Bundesbahnen, HZPP	36
EC	DB Fernverkehr AG, Österreichische Bundesbahnen	30
EC	Trenitalia, Schweizerische Bundesbahnen, DB Fernverkehr AG	18
EC	Österreichische Bundesbahnen, Schweizerische Bundesbahnen	5

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

ECE	DB Fernverkehr AG	242
ECE	DB Fernverkehr AG, Österreichische Bundesbahnen, Schweizerische Bundesbahnen	164
ECE	Dänische Staatsbahnen, DB Fernverkehr AG	47
ECE	DB Fernverkehr AG, Schweizerische Bundesbahnen	24

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

EN, ES, EUR, EST, FLX already covered

Always assign GV to Govolta

```sql
UPDATE delay_records
SET operator = 'Govolta'
WHERE "routeType" = 'GV';
```

IC	DB Fernverkehr AG	9143
IC	Schweizerische Bundesbahnen, DB Fernverkehr AG	513
IC	DB Fernverkehr AG, Schweizerische Bundesbahnen	292
IC	DB Regio AG Mitte SÜWEX	80
IC	PKP Intercity, DB Fernverkehr AG	55
IC	Dänische Staatsbahnen	46
IC	DB Fernverkehr AG, Österreichische Bundesbahnen, Ceske Drahy, PKP Intercity	30
IC	PKP Intercity, Ceske Drahy, Österreichische Bundesbahnen, DB Fernverkehr AG	30
IC	Snälltåget	10

```sql
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'DB'
  AND "routeType" = 'IC'
  AND "routeNumber" IN (
    '180','182','184','186','188','280','282','284','380','388','480','482','484','486','488',
    '1082','1180','181','183','185','187','281','283','285','389','1089'
  );

UPDATE delay_records
SET operator = 'PKP Intercity'
WHERE agency = 'DB'
  AND "routeType" = 'IC'
  AND "routeNumber" IN ('132','134','407','417');

UPDATE delay_records
SET operator = 'OEBB'
WHERE agency = 'DB'
  AND "routeType" = 'IC'
  AND "routeNumber" IN ('406','416');

UPDATE delay_records
SET operator = 'DSB'
WHERE agency = 'DB'
  AND "routeType" = 'IC'
  AND CAST("routeNumber" AS INTEGER) BETWEEN 5751 AND 5767;

UPDATE delay_records
SET operator = 'DB Fernverkehr AG'
WHERE agency = 'DB'
  AND "routeType" = 'IC'
  AND "routeNumber" NOT IN (
    '180','182','184','186','188','280','282','284','380','388','480','482','484','486','488',
    '1082','1180','181','183','185','187','281','283','285','389','1089',
    '132','134','407','417',
    '406','416'
  )
  AND CAST("routeNumber" AS INTEGER) NOT BETWEEN 5751 AND 5767;
```

ICE already covered

NJ already covered

RE	DB Regio AG Mitte SÜWEX	96

RJ, RJX, TGV, WB already covered

### **GTFSDE agency**

```sql
SELECT TRIM("routeType") AS routetype,
       COALESCE(operator, '(NULL)') AS operator,
       COUNT(*) AS cnt
FROM delay_records
WHERE UPPER(TRIM(agency)) = 'GTFSDE'
  AND date > '2026-05-04'
GROUP BY TRIM("routeType"), operator
ORDER BY cnt DESC, routetype, operator;
```

EC	(NULL)	286
EC	DB Fernverkehr AG	201
EC	Ceske Drahy	4
ECE	(NULL)	368
ECE	DB Fernverkehr AG	278
ECE	Dänische Staatsbahnen	5
EN	(NULL)	15
EN	ÖBB	15

EC, ECE, EN should be excluded from analysis (already covered by DB)

FEX	(NULL)	1609
FEX	800151 DB Regio AG Nordost	1473
FEX	Albtal-Verkehrs-Gesellschaft	52

Which FEX trains are DB?

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'FEX'
  AND CAST("routeNumber" AS INTEGER) BETWEEN 21800 AND 21969;
```

MEX	(NULL)	18259
MEX	DB Regio Stuttgart	6824
MEX	Arverio Baden-Württemberg GmbH	5745
MEX	8006D6 DB Regio AG Baden-Württemberg	1319
MEX	SWEG Bahn Stuttgart	138

Which MEX are DB and which are Arverio?

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'MEX'
  AND (
    CAST("routeNumber" AS INTEGER) BETWEEN 17500 AND 17570
    OR CAST("routeNumber" AS INTEGER) BETWEEN 19200 AND 19399
    OR CAST("routeNumber" AS INTEGER) BETWEEN 19500 AND 19699
  );

UPDATE delay_records
SET operator = 'Arverio'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'MEX'
  AND (
    CAST("routeNumber" AS INTEGER) BETWEEN 19100 AND 19199
    OR CAST("routeNumber" AS INTEGER) BETWEEN 19400 AND 19499
  );
```

NRB	(NULL)	90
NRB	DB RegioNetz Verkehrs GmbH Südostbayernbahn	83
NRB	800430 DB RegioNetz Verkehrs GmbH Erzgebirgsbahn	2

All NRB are DB RegioNetz

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'NRB';
```

Which RB are DB and which are Arverio?

```sql
UPDATE delay_records
SET operator = 'Arverio'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RB'
  AND (
    CAST("routeNumber" AS INTEGER) BETWEEN 57000 AND 57344
    OR CAST("routeNumber" AS INTEGER) BETWEEN 78901 AND 78975
  );
```

For DB Regio, assigning based on RB + Routenumber alone is not sufficient given the major range overlaps. Instead, per region, get the stopIds that are served by RB of the respective operator:

```sql
SELECT DISTINCT "deutscheBahnStopId"
FROM delay_records
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RB'
  AND operator LIKE '%DB Regio AG Nordost'
ORDER BY "deutscheBahnStopId";
```

Then together with the number ranges for RB trains for this operator, only assign DB to RB trains with those numbers at those stops:

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RB'
  AND "deutscheBahnStopId" IN (
    '331064','360304','5100082','5100083','5100096','5100222','5101281','5102886',
    '5189954','5193610','8010016','8010018','8010036','8010041','8010051','8010053',
    '8010066','8010069','8010072','8010073','8010079','8010089','8010093','8010099',
    '8010100','8010103','8010113','8010176','8010183','8010193','8010215','8010255',
    '8010279','8010280','8010285','8010300','8010304','8010308','8010322','8010324',
    '8010327','8010338','8010355','8010357','8010373','8010377','8010381','8010389',
    '8010392','8010395','8010396','8010403','8010404','8010405','8010406','8011031',
    '8011078','8011093','8011098','8011102','8011108','8011109','8011114','8011140',
    '8011155','8011160','8011162','8011167','8011179','8011188','8011201','8011270',
    '8011286','8011306','8011318','8011319','8011320','8011334','8011340','8011414',
    '8011419','8011421','8011425','8011471','8011540','8011542','8011563','8011667',
    '8011695','8011729','8011735','8011749','8011778','8011797','8011889','8011901',
    '8011944','8011945','8011991','8011992','8011995','8012006','8012065','8012084',
    '8012086','8012089','8012096','8012108','8012127','8012169','8012215','8012253',
    '8012315','8012316','8012329','8012341','8012377','8012445','8012469','8012479',
    '8012482','8012503','8012582','8012583','8012584','8012609','8012617','8012621',
    '8012650','8012666','8012681','8012713','8012729','8012785','8012806','8012818',
    '8012819','8012840','8012841','8012892','8012903','8012934','8012941','8012962',
    '8012963','8013021','8013040','8013105','8013106','8013132','8013133','8013160',
    '8013161','8013183','8013185','8013267','8013272','8013305','8013339','8013340',
    '8013341','8013350','8013368','8013385','8013406','8013470','8013475','8013481',
    '8013483','8013487','8013489','8013490','8017349','8079084','8079604','8079629',
    '8080170','8080190','8080260','8080370','8080710','8081220','8081688','8087026',
    '8087027','936003'
  )
  AND (
    -- 800151
    CAST("routeNumber" AS INTEGER) BETWEEN 5383 AND 5395
    OR CAST("routeNumber" AS INTEGER) BETWEEN 5830 AND 5841
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18100 AND 18166
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18238 AND 18275
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18300 AND 18341
    OR "routeNumber" IN ('18451','18480')
    OR CAST("routeNumber" AS INTEGER) BETWEEN 93250 AND 93252
    OR CAST("routeNumber" AS INTEGER) BETWEEN 93268 AND 93270
    OR CAST("routeNumber" AS INTEGER) BETWEEN 94740 AND 94775
    -- 800153
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18700 AND 18737
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18748 AND 18749
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18800 AND 18869
    -- 800156
    OR CAST("routeNumber" AS INTEGER) BETWEEN 13030 AND 13037
    -- 800159
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18000 AND 18048
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18080 AND 18084
    -- 800161
    OR "routeNumber" = '3648'
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18550 AND 18599
    -- 800163
    OR CAST("routeNumber" AS INTEGER) BETWEEN 13100 AND 13149
    OR CAST("routeNumber" AS INTEGER) BETWEEN 13221 AND 13269
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18740 AND 18745
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18870 AND 18899
    -- 800166
    OR "routeNumber" = '18086'
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18345 AND 18372
    OR CAST("routeNumber" AS INTEGER) BETWEEN 18420 AND 18445
  );
```

- [x]  DB Regio AG Nordost
- [x]  DB Regio AG Nord
- [x]  DB Regio AG NRW
- [x]  DB Regio AG Südost
- [x]  DB RegioNetz Verkehrs GmbH Erzgebirgsbahn
- [x]  DB Regio AG Oberweisbacher Berg+Schwa
- [x]  DB RegioNetz Mitte
- [x]  DB RegioNetz Verkehrs GmbH Kurhessenbahn
- [x]  DB Regio AG Mitte Region Hessen
- [x]  DB RegioNetz Verkehrs GmbH Westfrankenbahn
- [x]  DB Regio AG Baden-Württemberg
- [x]  DB Regio AG Bayern
- [x]  DB Regio AG Mitte Region Südwest
- [x]  DB Regio Stuttgart
- [x]  DB RegioNetz Verkehrs GmbH Südostbayernbahn

Which RE are DB and which are Arverio?

```sql
UPDATE delay_records
SET operator = 'Arverio'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RE'
  AND (
    CAST("routeNumber" AS INTEGER) BETWEEN 57006 AND 57347
    OR CAST("routeNumber" AS INTEGER) BETWEEN 78900 AND 78984
  );
```

For DB Regio, assigning based on RB + Routenumber alone is not sufficient given the major range overlaps. Instead, per region, get the stopIds that are served by RB of the respective operator:

```sql
SELECT DISTINCT "deutscheBahnStopId"
FROM delay_records
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RB'
  AND operator LIKE '%DB Regio AG Nordost'
ORDER BY "deutscheBahnStopId";
```

Then together with the number ranges for RB trains for this operator, only assign DB to RB trains with those numbers at those stops, for example:

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RE'
  AND "deutscheBahnStopId" IN (
    '8000042','8000124','8000131','8000156','8000189','8000191','8000218','8000229',
    '8000236','8000244','8000264','8000265','8000275','8000295','8000323','8000369',
    '8000373','8000383','8000423','8000471','8000599','8000649','8000668','8000681',
    '8000736','8001132','8001366','8001618','8001707','8001883','8002021','8002137',
    '8002342','8002380','8002632','8002685','8002883','8002931','8003101','8003235',
    '8003726','8003759','8003932','8004094','8004095','8004215','8004219','8004577',
    '8004658','8005013','8005077','8005229','8005494','8005578','8005592','8005714',
    '8005736','8006083','8006137','8006661','8070097','8700271','8700439'
  )
  AND (
    -- 801518
    "routeNumber" IN ('38632','38710')
    OR CAST("routeNumber" AS INTEGER) BETWEEN 38761 AND 38770
    OR CAST("routeNumber" AS INTEGER) BETWEEN 38784 AND 38799
    -- 801526
    OR CAST("routeNumber" AS INTEGER) BETWEEN 4280 AND 4299
    -- 801539
    OR "routeNumber" = '38112'
    -- 8015A6
    OR CAST("routeNumber" AS INTEGER) BETWEEN 13324 AND 13334
    -- 8015FR
    OR CAST("routeNumber" AS INTEGER) BETWEEN 86381 AND 86391
    OR CAST("routeNumber" AS INTEGER) BETWEEN 88824 AND 88873
  );
```

Tackled operator-stopid combinations for RE:

- [x]  DB Regio AG Nordost
- [x]  DB Regio AG Nord
- [x]  DB Regio AG NRW
- [x]  DB Regio AG Südost
- [x]  DB RegioNetz Verkehrs GmbH Kurhessenbahn
- [x]  DB Regio AG Mitte Region Hessen
- [x]  DB Regio AG Mitte
- [x]  DB RegioNetz Verkehrs GmbH Westfrankenbahn
- [x]  DB Regio AG Baden-Württemberg
- [x]  DB Regio AG Bayern
- [x]  DB Regio AG Mitte Region Südwest
- [x]  DB Regio AG NRW (second)
- [x]  Db Regio Südostbayernbahn
- [x]  DB Regio Stuttgart

RS	(NULL)	20941
RS	Südwestdeutsche Verkehrs-AG	7113
RS	NordWestBahn	5035
RS	8007DU DB Regio AG Bayern	1751
RS	800622 DB Regio AG Baden-Württemberg	584
RS	800622 DB ZugBus Regionalverkehr Alb-Bodensee	499
RS	SNCF	3

Which RS are DB?

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'RS'
  AND (
    CAST("routeNumber" AS INTEGER) BETWEEN 32600 AND 32677
    OR CAST("routeNumber" AS INTEGER) BETWEEN 57440 AND 57798
  );
```

Which S are DB?

Same exercise as for RB and S:

- [x]  DB Regio AG Nordost
- [x]  DB Regio AG NRW
- [x]  DB Regio AG Südost
- [x]  DB Regio AG Mitte Region Hessen
- [x]  DB Regio AG Baden-Württemberg
- [x]  DB Regio AG S-Bahn Stuttgart
- [x]  DB Regio AG Bayern
- [x]  DB Regio AG Mitte Region Südwest
- [x]  S Bahn Berlin GmbH
- [x]  S Bahn Hamburg

U	(NULL)	268
U	800417 DB Regio AG Südost	180

```sql
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'GTFSDE'
  AND "routeType" = 'U'
  AND (
    CAST("routeNumber" AS INTEGER) BETWEEN 28000 AND 28014
    OR CAST("routeNumber" AS INTEGER) = 28023
  );
```

### **Leftover train numbers without operator for EC, IC, ECE, EN**

```sql
SELECT
  agency,
  "routeType",
  "routeNumber",
  COUNT(*) AS cnt
FROM delay_records
WHERE operator IS NULL
  AND "routeType" IN ('EC', 'IC', 'ECE', 'EN')
  AND agency IN ('DB', 'OEBB', 'SBB', 'GTFSDE', 'IT', 'FR', 'HU', 'PL')
GROUP BY agency, "routeType", "routeNumber"
ORDER BY cnt DESC, agency, "routeType", "routeNumber";
```

```sql
SELECT
  "routeType",
  COALESCE(operator::text, '(NULL)') AS operator,
  STRING_AGG(DISTINCT "routeNumber", ', ' ORDER BY "routeNumber") AS route_numbers
FROM delay_records
WHERE agency = 'OEBB'
  AND "routeType" IN ('EC', 'IC', 'ECE', 'EN')
  AND date > '2026-05-04'
GROUP BY "routeType", operator
ORDER BY "routeType", operator;
```

**Update OEBB records:**

```sql
-- DB Fernverkehr AG → operator 'DB'
UPDATE delay_records
SET operator = 'DB'
WHERE agency = 'OEBB'
  AND (
    ("routeType" = 'EC' AND "routeNumber" IN (
      '115', '1281', '190', '192', '194', '196', '198', '213',
      '80', '81', '94', '96', '98'
    ))
    OR
    ("routeType" = 'IC' AND "routeNumber" IN ('406', '416'))
  );

-- Nahreisezug → operator 'OEBB'
UPDATE delay_records
SET operator = 'OEBB'
WHERE agency = 'OEBB'
  AND (
    ("routeType" = 'EC' AND "routeNumber" IN (
      '100', '102', '106', '114', '140', '141', '142', '143', '144', '145',
      '146', '147', '148', '149', '164', '202', '204', '206', '212', '214',
      '290', '337', '340', '341', '342', '343', '462', '463', '70', '71',
      '78', '79'
    ))
    OR
    ("routeType" = 'EN' AND "routeNumber" IN (
      '40237', '40414', '40462', '40465', '40467', '414', '50237'
    ))
    OR
    ("routeType" = 'IC' AND "routeNumber" IN (
      '1110', '1111', '1112', '1113', '1115', '1118', '1119', '1135', '1136',
      '1138', '1142', '1143', '1151', '1244', '1249', '350', '351', '354',
      '407', '460', '532', '533', '534', '535', '536', '537', '538', '540',
      '541', '542', '543', '544', '545', '546', '547', '548', '549', '558',
      '559', '640', '641', '642', '643', '644', '645', '646', '647', '648',
      '649', '651', '740', '741', '742', '743', '744', '745', '746', '747',
      '748', '749', '756', '759', '790', '791', '792', '793', '794', '795',
      '796', '797', '798', '799', '840', '841', '842', '843', '847', '848',
      '850', '890', '891', '896', '897', '898', '899'
    ))
  );

-- PKP Intercity → keep label 'PKP Intercity'
UPDATE delay_records
SET operator = 'PKP Intercity'
WHERE agency = 'OEBB'
  AND (
    ("routeType" = 'EC' AND "routeNumber" IN (
      '101', '103', '107', '203', '205', '207'
    ))
    OR
    ("routeType" = 'EN' AND "routeNumber" IN (
      '40406', '40407', '40416', '40417'
    ))
    OR
    ("routeType" = 'IC' AND "routeNumber" IN ('207', '417'))
  );

-- Schweizerische Bundesbahnen SBB → operator 'SBB'
UPDATE delay_records
SET operator = 'SBB'
WHERE agency = 'OEBB'
  AND "routeType" = 'EC'
  AND "routeNumber" IN (
    '163', '191', '193', '195', '197', '199', '95', '97', '99'
  );
```

Update EN trains for agency DB - assume local national operator per country:

```sql
UPDATE delay_records
SET operator = CASE UPPER(TRIM(stopcountry))
  WHEN 'DE' THEN 'DB'
  WHEN 'AT' THEN 'OEBB'
  WHEN 'CH' THEN 'SBB'
  WHEN 'PL' THEN 'PKP Intercity'
  WHEN 'CZ' THEN 'CD'
  ELSE operator
END
WHERE agency = 'DB'
  AND "routeType" = 'EN'
  AND operator IS NULL;
```

Same for trains in agency OEBB and SBB - assume local national operator per country: 

```sql
UPDATE delay_records
SET operator = CASE UPPER(TRIM(stopcountry))
  WHEN 'DE' THEN 'DB'
  WHEN 'AT' THEN 'OEBB'
  WHEN 'CH' THEN 'SBB'
  WHEN 'PL' THEN 'PKP Intercity'
  WHEN 'CZ' THEN 'CD'
  WHEN 'IT' THEN 'Trenitalia'
  ELSE operator
END
WHERE agency = 'OEBB'
  AND "routeType" IN ('EN', 'EC', 'IC', 'ECE')
  AND operator IS NULL;
```

Same for EC trains in Italy

```sql
UPDATE delay_records
SET operator = CASE UPPER(TRIM(stopcountry))
  WHEN 'IT' THEN 'Trenitalia'
  WHEN 'FR' THEN 'Trenitalia'
  ELSE operator
END
WHERE agency = 'IT'
  AND "routeType" IN ('EC')
  AND operator IS NULL;
```

# Populate longdistance column

For these operators, the routetypes that are long distance trains can be set with a hardcoded flag.

For other operators, a similar check can be done.

Similarly, we could break this down into more categories, like high speed, medium distance and commuter.

| Operator | Included routetypes |
| --- | --- |
| ÖBB | EC, ECE, RJ, RJX, IC, NJ, IR, D, Nightjet |
| DB | ICE, IC, EC, ECE, IR |
| SBB | EC, IC, IR |
| SNCF | TGV InOui, TGV Lyria, Ouigo, Intercités, Intercités de nuit, INTERCITES, INTERCITES DE NUIT, LYR, TGV, OUI, OUIGO, OGO, OTC, Ouigo Train Classic |
| Trenitalia | Frecciarossa, Frecciargento, Frecciabianca, Intercity, Intercity notte, EXP, IR, IC, ICN, FR, FB, FA |
| MAV | EC, IC, Ex, EN, G, Gy |
| PKP Intercity | EC, IC, EIC, EIP, TLK |
| Flixtrain | FLX |
| Westbahn | WB |
| NS | ECC, EC, EuroCity, Eurocity Direct, IC, Intercity, ICD, Intercity direct |
| NMBS | ECD, EuroCity, EuroCity Direct, IC |
| DSB | ECE, IC, ICL, IR |
| Other | EN, IC |
| European Sleeper | ES, European Sleeper |
| Eurostar | EST, EUR, Eurostar |
| GoVolta | GV, GoVolta GoVolta, GoVolta |
| Italo | Italo |

```sql
UPDATE delay_records
SET longdistance = 1
WHERE UPPER(TRIM("routeType")) IN (
  'D',
  'EC',
  'ECC',
  'ECD',
  'ECE',
  'EIC',
  'EIP',
  'EX',
  'EXP',
  'EN',
  'ES',
  'EST',
  'EUR',
  'EUROCITY',
  'EUROCITY DIRECT',
  'EUROPEAN SLEEPER',
  'EUROSTAR',
  'FA',
  'FB',
  'FLX',
  'FR',
  'G',
  'GV',
  'GOVOLTA GOVOLTA',
  'GY',
  'IC',
  'ICD',
  'ICE',
  'ICL',
  'ICN',
  'INTERCITES',
  'INTERCITES DE NUIT',
  'IR',
  'INTERCITY',
  'INTERCITY DIRECT',
  'ITALO',
  'LYR',
  'LYRIA',
  'NJ',
  'NACHTTREIN',
  'NIGHTJET',
  'OGO',
  'OTC',
  'OUI',
  'OUIGO',
  'OUIGO TRAIN CLASSIC',
  'RJ',
  'RJX',
  'TGV',
  'TGV INOUI',
  'TLK',
  'WB'
);
```

### 

## Populate stopcountry column

Ensure to check if dbID has 7 numbers

```sql
UPDATE delay_records
SET stopcountry = CASE SUBSTR(deutscheBahnStopId, 1, 2)
  WHEN '10' THEN 'FI' WHEN '20' THEN 'RU' WHEN '21' THEN 'BY' WHEN '22' THEN 'UA' WHEN '23' THEN 'MD'
  WHEN '24' THEN 'LT' WHEN '25' THEN 'LV' WHEN '26' THEN 'EE' WHEN '27' THEN 'KZ' WHEN '28' THEN 'GE'
  WHEN '41' THEN 'AL' WHEN '44' THEN 'BA' WHEN '49' THEN 'BA' WHEN '50' THEN 'BA' WHEN '51' THEN 'PL'
  WHEN '52' THEN 'BG' WHEN '53' THEN 'RO' WHEN '54' THEN 'CZ' WHEN '55' THEN 'HU' WHEN '56' THEN 'SK'
  WHEN '57' THEN 'AZ' WHEN '58' THEN 'AM' WHEN '60' THEN 'IE' WHEN '62' THEN 'ME' WHEN '65' THEN 'MK'
  WHEN '70' THEN 'GB' WHEN '71' THEN 'ES' WHEN '72' THEN 'RS' WHEN '73' THEN 'GR' WHEN '74' THEN 'SE'
  WHEN '75' THEN 'TR' WHEN '76' THEN 'NO' WHEN '78' THEN 'HR' WHEN '79' THEN 'SI' WHEN '80' THEN 'DE'
  WHEN '81' THEN 'AT' WHEN '82' THEN 'LU' WHEN '83' THEN 'IT' WHEN '84' THEN 'NL' WHEN '85' THEN 'CH'
  WHEN '86' THEN 'DK' WHEN '87' THEN 'FR' WHEN '88' THEN 'BE' WHEN '90' THEN 'EG' WHEN '91' THEN 'TN'
  WHEN '92' THEN 'DZ' WHEN '93' THEN 'MA' WHEN '94' THEN 'PT' WHEN '95' THEN 'IL' WHEN '96' THEN 'IR'
END
WHERE LENGTH(deutscheBahnStopId) = 7
  AND deutscheBahnStopId GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9]';
```
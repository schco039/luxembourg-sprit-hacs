# Luxembourg Spritpreise – HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant Integration für **Super 95 Spritpreise in Luxemburg**.  
Daten werden automatisch von **lesfrontaliers.lu** (RSS Feed) bezogen – typisch um ~18:00 Uhr, also **6 Stunden vor Mitternacht** wenn der neue Preis gilt.

---

## Features

- ✅ Automatischer RSS Feed Parser (lesfrontaliers.lu)
- ✅ Config Flow – Einrichtung komplett über die HA GUI
- ✅ Mehrere Fahrzeuge / Tankgrößen
- ✅ Sensoren: Preis, Differenz €, Differenz %, Tankkosten, Trend
- ✅ Custom Lovelace Card mit Trend-Anzeige und Tankkosten-Vergleich
- ✅ Push Notification via HA Automationen
- ✅ Keine API-Keys, keine externen Abhängigkeiten

---

## Installation via HACS

1. HACS öffnen → **Integrations** → ⋮ → **Custom repositories**
2. URL eingeben: `https://github.com/DEIN_USERNAME/luxembourg-sprit-hacs`
3. Kategorie: **Integration**
4. **Luxembourg Spritpreise** installieren
5. HA neu starten

### Lovelace Card installieren

1. HACS → **Frontend** → ⋮ → **Custom repositories**
2. URL: `https://github.com/DEIN_USERNAME/luxembourg-sprit-hacs`
3. Kategorie: **Lovelace**
4. **Luxembourg Spritpreise Card** installieren

---

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. "Luxembourg Spritpreise" suchen
3. Fahrzeugname und Tankgröße eingeben
4. Für jedes Fahrzeug wiederholen

---

## Lovelace Card

```yaml
type: custom:luxembourg-sprit-card
entity: sensor.sp95_preis   # Entity-ID deines Sensors
```

---

## Sensoren

Jedes eingerichtete Fahrzeug erstellt einen Sensor mit folgenden Attributen:

| Attribut | Beschreibung |
|---|---|
| `price` | Aktueller SP95 Preis in €/L |
| `previous_price` | Vorheriger Preis |
| `diff` | Differenz in €/L |
| `diff_pct` | Differenz in % |
| `tank_cost` | Kosten Volltank in € |
| `tank_diff` | Mehrkosten/-ersparnis Volltank |
| `trend` | `rising` / `falling` / `stable` |
| `article_title` | Titel des letzten Artikels |
| `article_link` | Link zum Artikel |
| `article_date` | Datum der Meldung |
| `last_check` | Letzter RSS-Abruf |

---

## Automationen (Beispiel)

```yaml
- alias: "SP95 wird teurer – Benachrichtigung"
  trigger:
    - platform: state
      entity_id: sensor.sp95_preis
      attribute: trend
      to: "rising"
  action:
    - service: notify.mobile_app_DEIN_GERAET
      data:
        title: "⛽ SP95 wird teurer!"
        message: >
          Neuer Preis: {{ state_attr('sensor.sp95_preis', 'price') }} €/L
          ({{ state_attr('sensor.sp95_preis', 'diff') }} €/L,
          Volltank: {{ state_attr('sensor.sp95_preis', 'tank_cost') }} €)
          👉 Heute noch tanken!
```

---

## Datenquelle

[lesfrontaliers.lu](https://www.lesfrontaliers.lu) veröffentlicht Preisänderungen  
typisch um **~18:00 Uhr am Vorabend** – deutlich früher als Carbu.com (nach Mitternacht).

---

## Lizenz

MIT License

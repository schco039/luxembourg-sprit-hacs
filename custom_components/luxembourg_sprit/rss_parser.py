"""
Price fetcher for Luxembourg Spritpreise.

Strategy:
  - On first load / init: fetch current price from Carbu.com (reliable HTML table)
  - Every poll interval: check lesfrontaliers.lu RSS for price change articles
  - If RSS finds a new price → use it; otherwise keep last known value
"""
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import aiohttp

from .const import (
    RSS_URL,
    CARBU_URL,
    FUEL_KEYWORDS,
    GENERAL_KEYWORDS,
    PRICE_PATTERNS,
    DEFAULT_FUEL_TYPE,
)

_LOGGER = logging.getLogger(__name__)

CARBU_FUEL_ROW = {
    "Super 95": r"super\s*95",
    "Super 98": r"super\s*98",
    "Diesel":   r"diesel(?!\s*\(b10\))",
    "LPG":      r"lpg",
}


class SpritPriceFetcher:
    """Fetches Luxembourg fuel prices: Carbu.com on init, RSS for updates."""

    def __init__(self, fuel_type: str = DEFAULT_FUEL_TYPE) -> None:
        self._fuel_type = fuel_type
        self._initialized = False
        self._last_price: float | None = None

    async def async_fetch(self) -> dict:
        """Called by DataUpdateCoordinator on every update cycle."""
        if not self._initialized:
            result = await self._fetch_carbu()
            if result.get("price"):
                self._initialized = True
                self._last_price = result["price"]
            return result

        rss_result = await self._fetch_rss()
        if rss_result.get("price"):
            self._last_price = rss_result["price"]
            return rss_result

        # No new price in RSS → return cached value
        return {
            "price": self._last_price,
            "title": None,
            "pub_date": None,
            "link": None,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "status": "ok_cached",
            "source": "cache",
        }

    # ------------------------------------------------------------------ #
    # Carbu.com – initial price                                            #
    # ------------------------------------------------------------------ #
    async def _fetch_carbu(self) -> dict:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; HomeAssistant/LuxembourgSprit/1.0)"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    CARBU_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    resp.raise_for_status()
                    html = await resp.text()

            price = self._parse_carbu_html(html)
            if price:
                _LOGGER.info("Carbu.com init: %s = %.3f €/L", self._fuel_type, price)
                return {
                    "price": price,
                    "title": f"Initialisierung via Carbu.com ({self._fuel_type})",
                    "pub_date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
                    "link": CARBU_URL,
                    "last_check": datetime.now(timezone.utc).isoformat(),
                    "status": "ok",
                    "source": "carbu.com",
                }
            return self._empty("carbu_no_price")

        except aiohttp.ClientError as err:
            _LOGGER.warning("Carbu.com error: %s", err)
            return self._empty(f"carbu_error")

    def _parse_carbu_html(self, html: str) -> float | None:
        pattern = CARBU_FUEL_ROW.get(self._fuel_type, r"super\s*95")
        # Match table row: "Super 95 | 1,567 €/l"
        m = re.search(
            pattern + r"[^<]*</td>\s*<td[^>]*>\s*(\d[,\.]\d{3})",
            html, re.IGNORECASE
        )
        if m:
            price = float(m.group(1).replace(",", "."))
            if 0.5 <= price <= 3.0:
                return round(price, 3)
        # Fallback
        m2 = re.search(pattern + r".{0,80}?(\d[,\.]\d{3})", html, re.IGNORECASE | re.DOTALL)
        if m2:
            price = float(m2.group(1).replace(",", "."))
            if 0.5 <= price <= 3.0:
                return round(price, 3)
        return None

    # ------------------------------------------------------------------ #
    # lesfrontaliers.lu RSS – change detection                             #
    # ------------------------------------------------------------------ #
    async def _fetch_rss(self) -> dict:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; HomeAssistant/LuxembourgSprit/1.0)"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    RSS_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    resp.raise_for_status()
                    raw = await resp.read()

            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            text = raw.decode("utf-8", errors="replace")
            for marker in ("<?xml", "<rss", "<feed"):
                idx = text.find(marker)
                if idx > 0:
                    text = text[idx:]
                    break

            results = self._parse_rss_xml(text)
            if results:
                item = results[0]
                return {
                    "price": item["price"],
                    "title": item["title"],
                    "pub_date": item["pub_date"],
                    "link": item["link"],
                    "last_check": datetime.now(timezone.utc).isoformat(),
                    "status": "ok",
                    "source": "lesfrontaliers.lu",
                }
            return {}

        except (aiohttp.ClientError, ET.ParseError) as err:
            _LOGGER.debug("RSS fetch skipped: %s", err)
            return {}

    def _parse_rss_xml(self, xml_content: str) -> list[dict]:
        root = ET.fromstring(xml_content)
        channel = root.find("channel")
        items = channel.findall("item") if channel else root.findall(".//item")

        results = []
        for item in items[:20]:
            title = item.findtext("title", "")
            description = item.findtext("description", "")
            pub_date = item.findtext("pubDate", "")
            link = item.findtext("link", "")

            if not self._is_relevant(title, description):
                continue
            price = self._parse_price(title + " " + description)
            if price:
                results.append({
                    "price": price,
                    "title": title.strip(),
                    "pub_date": pub_date.strip(),
                    "link": link.strip(),
                })
        return results

    def _is_relevant(self, title: str, description: str) -> bool:
        combined = (title + " " + description).lower()
        fuel_kws = FUEL_KEYWORDS.get(self._fuel_type, [])
        return any(kw in combined for kw in fuel_kws + GENERAL_KEYWORDS)

    def _parse_price(self, text: str) -> float | None:
        text_lower = text.lower()
        for pattern in PRICE_PATTERNS:
            m = re.search(pattern, text_lower)
            if m:
                try:
                    price = float(m.group(1).replace(",", "."))
                    if 0.5 <= price <= 3.0:
                        return round(price, 3)
                except ValueError:
                    continue
        return None

    def _empty(self, status: str) -> dict:
        return {
            "price": None,
            "title": None,
            "pub_date": None,
            "link": None,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "source": "none",
        }


# Alias for __init__.py compatibility
SpritRSSParser = SpritPriceFetcher

try:
    from homeassistant.helpers.update_coordinator import UpdateFailed
except ImportError:
    class UpdateFailed(Exception):
        pass

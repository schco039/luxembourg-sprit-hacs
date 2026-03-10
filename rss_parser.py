"""RSS Parser for lesfrontaliers.lu SP95 price data."""
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import aiohttp

from .const import RSS_URL, FUEL_KEYWORDS, PRICE_PATTERNS

_LOGGER = logging.getLogger(__name__)


class SpritRSSParser:
    """Fetches and parses SP95 price from lesfrontaliers.lu RSS feed."""

    async def async_fetch(self) -> dict:
        """Fetch RSS feed and return parsed price data."""
        try:
            xml_content = await self._fetch_rss()
            results = self._parse_rss(xml_content)

            if results:
                item = results[0]
                return {
                    "price": item["price"],
                    "title": item["title"],
                    "pub_date": item["pub_date"],
                    "link": item["link"],
                    "last_check": datetime.now(timezone.utc).isoformat(),
                    "status": "ok",
                }

            return self._empty_result("no_price_found")

        except aiohttp.ClientError as err:
            _LOGGER.warning("Network error fetching RSS: %s", err)
            raise UpdateFailed(f"Network error: {err}") from err  # noqa: F821
        except ET.ParseError as err:
            _LOGGER.warning("XML parse error: %s", err)
            raise UpdateFailed(f"Parse error: {err}") from err  # noqa: F821

    async def _fetch_rss(self) -> str:
        headers = {"User-Agent": "HomeAssistant/LuxembourgSprit/1.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(RSS_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                resp.raise_for_status()
                return await resp.text()

    def _parse_rss(self, xml_content: str) -> list[dict]:
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
        return any(kw in combined for kw in FUEL_KEYWORDS)

    def _parse_price(self, text: str) -> float | None:
        text_lower = text.lower()
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                raw = match.group(1).replace(",", ".")
                price = float(raw)
                if 1.0 <= price <= 2.5:
                    return round(price, 3)
        return None

    def _empty_result(self, status: str) -> dict:
        return {
            "price": None,
            "title": None,
            "pub_date": None,
            "link": None,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "status": status,
        }


# Make UpdateFailed available
try:
    from homeassistant.helpers.update_coordinator import UpdateFailed
except ImportError:
    class UpdateFailed(Exception):
        pass

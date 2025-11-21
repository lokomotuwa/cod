import json
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from urllib.request import urlopen


class _LdJsonParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.payloads: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "script":
            return
        attr_dict = {key: (value or "") for key, value in attrs}
        if attr_dict.get("type", "").lower() == "application/ld+json":
            self.capture = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.capture:
            self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.payloads.append(data)


class _ContentSnippets(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title: Optional[str] = None
        self.in_li = False
        self.in_p = False
        self.list_items: List[str] = []
        self.paragraphs: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "li":
            self.in_li = True
        if tag.lower() == "p":
            self.in_p = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        if tag.lower() == "li":
            self.in_li = False
        if tag.lower() == "p":
            self.in_p = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self.in_title and not self.title:
            self.title = text
        if self.in_li:
            self.list_items.append(text)
        if self.in_p:
            self.paragraphs.append(text)


class RecipeFetcher:
    """Fetch recipes from the internet by parsing schema.org Recipe data."""

    def fetch(self, url: str) -> Dict[str, Any]:
        with urlopen(url, timeout=15) as response:  # nosec: B310
            html = response.read().decode("utf-8", errors="ignore")
        ld_data = self._parse_json_ld(html) or {}
        snippets = self._extract_snippets(html)
        title = ld_data.get("name") or snippets.title or url
        ingredients = ld_data.get("recipeIngredient") or self._fallback_ingredients(snippets)
        instructions = self._parse_instructions(ld_data) or snippets.paragraphs[:5]
        return {
            "title": title,
            "url": url,
            "source": urlparse(url).netloc,
            "ingredients": ingredients,
            "instructions": instructions,
        }

    def _parse_json_ld(self, html: str) -> Optional[Dict[str, Any]]:
        parser = _LdJsonParser()
        parser.feed(html)
        for payload in parser.payloads:
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                continue
            nodes: List[Dict[str, Any]] = []
            if isinstance(data, list):
                nodes.extend([node for node in data if isinstance(node, dict)])
            elif isinstance(data, dict):
                nodes.append(data)
            for node in nodes:
                types = node.get("@type")
                if not types:
                    continue
                if (isinstance(types, str) and types.lower() == "recipe") or (
                    isinstance(types, list) and any(t.lower() == "recipe" for t in types if isinstance(t, str))
                ):
                    return node
        return None

    def _parse_instructions(self, data: Dict[str, Any]) -> List[str]:
        instructions = data.get("recipeInstructions")
        if not instructions:
            return []
        if isinstance(instructions, str):
            return [instructions]
        parsed: List[str] = []
        for item in instructions:
            if isinstance(item, str):
                parsed.append(item)
            elif isinstance(item, dict) and "text" in item:
                parsed.append(str(item["text"]))
        return parsed

    def _extract_snippets(self, html: str) -> _ContentSnippets:
        parser = _ContentSnippets()
        parser.feed(html)
        return parser

    def _fallback_ingredients(self, snippets: _ContentSnippets) -> List[str]:
        items = []
        for text in snippets.list_items:
            if text and re.search(r"\d", text):
                items.append(text)
        return items[:10]

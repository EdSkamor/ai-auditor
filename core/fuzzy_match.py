"""
Fuzzy matching module using RapidFuzz
Implementuje fuzzy-match z suwakiem czułości i wyjaśnieniami
"""

import re
from dataclasses import dataclass
from typing import List, Optional

import unidecode
from rapidfuzz import fuzz, process


@dataclass
class MatchResult:
    """Wynik dopasowania fuzzy."""

    query: str
    match: str
    score: float
    explanation: str
    match_type: str
    normalized_query: str
    normalized_match: str


class FuzzyMatcher:
    """Klasa do fuzzy matching z RapidFuzz."""

    def __init__(self, sensitivity: float = 0.8):
        """
        Inicjalizacja fuzzy matcher.

        Args:
            sensitivity: Próg czułości (0.0-1.0), domyślnie 0.8
        """
        self.sensitivity = sensitivity
        self.match_types = {
            "ratio": fuzz.ratio,
            "partial_ratio": fuzz.partial_ratio,
            "token_sort_ratio": fuzz.token_sort_ratio,
            "token_set_ratio": fuzz.token_set_ratio,
            "partial_token_sort_ratio": fuzz.partial_token_sort_ratio,
            "partial_token_set_ratio": fuzz.partial_token_set_ratio,
            "WRatio": fuzz.WRatio,
            "QRatio": fuzz.QRatio,
        }

    def normalize_text(self, text: str) -> str:
        """
        Normalizacja tekstu dla lepszego dopasowania.

        Args:
            text: Tekst do normalizacji

        Returns:
            Znormalizowany tekst
        """
        if not text:
            return ""

        # Usuń polskie znaki diakrytyczne
        normalized = unidecode.unidecode(text)

        # Konwertuj na małe litery
        normalized = normalized.lower()

        # Usuń znaki specjalne i zostaw tylko litery, cyfry i spacje
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)

        # Usuń wielokrotne spacje
        normalized = re.sub(r"\s+", " ", normalized)

        # Usuń spacje na początku i końcu
        normalized = normalized.strip()

        return normalized

    def explain_match(
        self, query: str, match: str, score: float, match_type: str
    ) -> str:
        """
        Wyjaśnienie dlaczego score ma daną wartość.

        Args:
            query: Zapytanie
            match: Dopasowanie
            score: Wynik dopasowania
            match_type: Typ dopasowania

        Returns:
            Wyjaśnienie dopasowania
        """
        normalized_query = self.normalize_text(query)
        normalized_match = self.normalize_text(match)

        explanations = []

        # Podstawowe informacje
        explanations.append(f"**Typ dopasowania:** {match_type}")
        explanations.append(f"**Wynik:** {score:.2f}%")

        # Analiza długości
        query_len = len(normalized_query)
        match_len = len(normalized_match)
        explanations.append(f"**Długość zapytania:** {query_len} znaków")
        explanations.append(f"**Długość dopasowania:** {match_len} znaków")

        # Analiza tokenów
        query_tokens = normalized_query.split()
        match_tokens = normalized_match.split()
        explanations.append(
            f"**Tokeny zapytania:** {len(query_tokens)} ({', '.join(query_tokens[:5])}{'...' if len(query_tokens) > 5 else ''})"
        )
        explanations.append(
            f"**Tokeny dopasowania:** {len(match_tokens)} ({', '.join(match_tokens[:5])}{'...' if len(match_tokens) > 5 else ''})"
        )

        # Wspólne tokeny
        common_tokens = set(query_tokens) & set(match_tokens)
        explanations.append(
            f"**Wspólne tokeny:** {len(common_tokens)} ({', '.join(list(common_tokens)[:5])}{'...' if len(common_tokens) > 5 else ''})"
        )

        # Analiza typu dopasowania
        if match_type == "ratio":
            explanations.append("**Ratio:** Porównanie całych stringów")
        elif match_type == "partial_ratio":
            explanations.append("**Partial Ratio:** Najlepsze dopasowanie podciągu")
        elif match_type == "token_sort_ratio":
            explanations.append(
                "**Token Sort Ratio:** Porównanie posortowanych tokenów"
            )
        elif match_type == "token_set_ratio":
            explanations.append("**Token Set Ratio:** Porównanie unikalnych tokenów")
        elif match_type == "WRatio":
            explanations.append("**WRatio:** Ważone dopasowanie z różnymi strategiami")
        elif match_type == "QRatio":
            explanations.append("**QRatio:** Szybkie dopasowanie")

        # Analiza jakości dopasowania
        if score >= 90:
            explanations.append("**Jakość:** Bardzo dobra (≥90%)")
        elif score >= 80:
            explanations.append("**Jakość:** Dobra (≥80%)")
        elif score >= 70:
            explanations.append("**Jakość:** Średnia (≥70%)")
        elif score >= 60:
            explanations.append("**Jakość:** Słaba (≥60%)")
        else:
            explanations.append("**Jakość:** Bardzo słaba (<60%)")

        # Sugestie
        if score < self.sensitivity * 100:
            explanations.append(
                f"**Sugestia:** Wynik poniżej progu czułości ({self.sensitivity * 100:.0f}%)"
            )

        return "\n".join(explanations)

    def find_best_match(
        self, query: str, choices: List[str], match_type: str = "WRatio"
    ) -> Optional[MatchResult]:
        """
        Znajdź najlepsze dopasowanie.

        Args:
            query: Zapytanie
            choices: Lista opcji do dopasowania
            match_type: Typ dopasowania

        Returns:
            Najlepsze dopasowanie lub None
        """
        if not query or not choices:
            return None

        # Normalizuj zapytanie
        normalized_query = self.normalize_text(query)

        # Znajdź najlepsze dopasowanie
        best_match = process.extractOne(
            normalized_query,
            [self.normalize_text(choice) for choice in choices],
            scorer=self.match_types.get(match_type, fuzz.WRatio),
        )

        if not best_match:
            return None

        # Znajdź oryginalny tekst
        original_match = (
            choices[best_match[2]] if len(best_match) > 2 else best_match[0]
        )

        # Sprawdź czy wynik przekracza próg czułości
        if best_match[1] < self.sensitivity * 100:
            return None

        # Wygeneruj wyjaśnienie
        explanation = self.explain_match(
            query, original_match, best_match[1], match_type
        )

        return MatchResult(
            query=query,
            match=original_match,
            score=best_match[1],
            explanation=explanation,
            match_type=match_type,
            normalized_query=normalized_query,
            normalized_match=self.normalize_text(original_match),
        )

    def find_all_matches(
        self,
        query: str,
        choices: List[str],
        match_type: str = "WRatio",
        limit: int = 10,
    ) -> List[MatchResult]:
        """
        Znajdź wszystkie dopasowania powyżej progu czułości.

        Args:
            query: Zapytanie
            choices: Lista opcji do dopasowania
            match_type: Typ dopasowania
            limit: Maksymalna liczba wyników

        Returns:
            Lista dopasowań
        """
        if not query or not choices:
            return []

        # Normalizuj zapytanie
        normalized_query = self.normalize_text(query)

        # Znajdź wszystkie dopasowania
        matches = process.extract(
            normalized_query,
            [self.normalize_text(choice) for choice in choices],
            scorer=self.match_types.get(match_type, fuzz.WRatio),
            limit=limit,
        )

        results = []
        for match in matches:
            # Znajdź oryginalny tekst
            original_match = choices[match[2]] if len(match) > 2 else match[0]

            # Sprawdź czy wynik przekracza próg czułości
            if match[1] >= self.sensitivity * 100:
                # Wygeneruj wyjaśnienie
                explanation = self.explain_match(
                    query, original_match, match[1], match_type
                )

                results.append(
                    MatchResult(
                        query=query,
                        match=original_match,
                        score=match[1],
                        explanation=explanation,
                        match_type=match_type,
                        normalized_query=normalized_query,
                        normalized_match=self.normalize_text(original_match),
                    )
                )

        return results

    def compare_strings(
        self, str1: str, str2: str, match_type: str = "WRatio"
    ) -> MatchResult:
        """
        Porównaj dwa stringi.

        Args:
            str1: Pierwszy string
            str2: Drugi string
            match_type: Typ dopasowania

        Returns:
            Wynik porównania
        """
        if not str1 or not str2:
            return MatchResult(
                query=str1,
                match=str2,
                score=0.0,
                explanation="Jeden z stringów jest pusty",
                match_type=match_type,
                normalized_query=self.normalize_text(str1),
                normalized_match=self.normalize_text(str2),
            )

        # Oblicz wynik dopasowania
        scorer = self.match_types.get(match_type, fuzz.WRatio)
        score = scorer(self.normalize_text(str1), self.normalize_text(str2))

        # Wygeneruj wyjaśnienie
        explanation = self.explain_match(str1, str2, score, match_type)

        return MatchResult(
            query=str1,
            match=str2,
            score=score,
            explanation=explanation,
            match_type=match_type,
            normalized_query=self.normalize_text(str1),
            normalized_match=self.normalize_text(str2),
        )

    def set_sensitivity(self, sensitivity: float):
        """
        Ustaw próg czułości.

        Args:
            sensitivity: Próg czułości (0.0-1.0)
        """
        self.sensitivity = max(0.0, min(1.0, sensitivity))

    def get_sensitivity(self) -> float:
        """
        Pobierz próg czułości.

        Returns:
            Próg czułości
        """
        return self.sensitivity

    def get_available_match_types(self) -> List[str]:
        """
        Pobierz dostępne typy dopasowania.

        Returns:
            Lista typów dopasowania
        """
        return list(self.match_types.keys())


class InvoiceMatcher:
    """Specjalizowany matcher dla faktur."""

    def __init__(self, sensitivity: float = 0.8):
        self.fuzzy_matcher = FuzzyMatcher(sensitivity)

    def match_invoice_numbers(
        self, query: str, invoice_numbers: List[str]
    ) -> List[MatchResult]:
        """
        Dopasuj numery faktur.

        Args:
            query: Numer faktury do wyszukania
            invoice_numbers: Lista numerów faktur

        Returns:
            Lista dopasowań
        """
        # Użyj token_sort_ratio dla numerów faktur
        return self.fuzzy_matcher.find_all_matches(
            query, invoice_numbers, match_type="token_sort_ratio"
        )

    def match_contractor_names(
        self, query: str, contractor_names: List[str]
    ) -> List[MatchResult]:
        """
        Dopasuj nazwy kontrahentów.

        Args:
            query: Nazwa kontrahenta do wyszukania
            contractor_names: Lista nazw kontrahentów

        Returns:
            Lista dopasowań
        """
        # Użyj WRatio dla nazw kontrahentów
        return self.fuzzy_matcher.find_all_matches(
            query, contractor_names, match_type="WRatio"
        )

    def match_nips(self, query: str, nips: List[str]) -> List[MatchResult]:
        """
        Dopasuj NIP-y.

        Args:
            query: NIP do wyszukania
            nips: Lista NIP-ów

        Returns:
            Lista dopasowań
        """
        # Normalizuj NIP-y (usuń spacje, myślniki)
        normalized_nips = [re.sub(r"[^\d]", "", nip) for nip in nips]
        normalized_query = re.sub(r"[^\d]", "", query)

        # Użyj ratio dla NIP-ów
        return self.fuzzy_matcher.find_all_matches(
            normalized_query, normalized_nips, match_type="ratio"
        )

    def match_addresses(self, query: str, addresses: List[str]) -> List[MatchResult]:
        """
        Dopasuj adresy.

        Args:
            query: Adres do wyszukania
            addresses: Lista adresów

        Returns:
            Lista dopasowań
        """
        # Użyj partial_token_sort_ratio dla adresów
        return self.fuzzy_matcher.find_all_matches(
            query, addresses, match_type="partial_token_sort_ratio"
        )


def create_fuzzy_matcher(sensitivity: float = 0.8) -> FuzzyMatcher:
    """
    Utwórz instancję FuzzyMatcher.

    Args:
        sensitivity: Próg czułości (0.0-1.0)

    Returns:
        Instancja FuzzyMatcher
    """
    return FuzzyMatcher(sensitivity)


def create_invoice_matcher(sensitivity: float = 0.8) -> InvoiceMatcher:
    """
    Utwórz instancję InvoiceMatcher.

    Args:
        sensitivity: Próg czułości (0.0-1.0)

    Returns:
        Instancja InvoiceMatcher
    """
    return InvoiceMatcher(sensitivity)

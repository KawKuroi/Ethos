"""Helpers del slice de Libros: export CSV de muestra (forma real de Goodreads)."""

from __future__ import annotations

from typing import Any

STORYGRAPH_CSV = (
    "Title,Authors,Contributors,ISBN/UID,Format,Read Status,Date Added,"
    "Last Date Read,Read Count,Star Rating,Review,Tags,Owned?\n"
    "Piranesi,Susanna Clarke,,9781635575637,hardcover,read,2026/01/02,"
    "2026/02/10,1,4.5,Enorme.,fantasia,Yes\n"
    "Berserk,Kentaro Miura,,,paperback,currently-reading,2026/03/01,,0,,,,No\n"
    "Monster,Naoki Urasawa,,,paperback,to-read,2026/03/02,,0,,,,No\n"
)


class FakeOpenLibraryApi:
    """Cliente falso de Open Library (un libro leído; el resto vacío)."""

    def __init__(self, *, status_code: int | None = None) -> None:
        self.status_code = status_code

    def get_shelf(self, user_name: str, shelf: str) -> list[dict[str, Any]]:
        if self.status_code is not None:
            from ethos_api.connectors.openlibrary.client import OpenLibraryApiError

            raise OpenLibraryApiError("privado", status_code=self.status_code)
        if shelf != "already-read":
            return []
        return [
            {
                "work": {
                    "title": "The Dispossessed",
                    "key": "/works/OL45804W",
                    "author_names": ["Ursula K. Le Guin"],
                    "first_publish_year": 1974,
                },
                "logged_date": "2026/03/23, 15:31:35",
            }
        ]


class FakeHardcoverApi:
    """Cliente falso de Hardcover (un libro leído)."""

    def __init__(self, *, status_code: int | None = None) -> None:
        self.status_code = status_code
        self.tokens: list[str] = []

    def get_user_books(self, token: str) -> list[dict[str, Any]]:
        self.tokens.append(token)
        if self.status_code is not None:
            from ethos_api.connectors.hardcover.client import HardcoverApiError

            raise HardcoverApiError("jwt", status_code=self.status_code)
        return [
            {
                "book_id": 101,
                "status_id": 3,
                "rating": 4.5,
                "last_read_date": "2026-02-10",
                "book": {
                    "title": "Piranesi",
                    "pages": 272,
                    "release_year": 2020,
                    "contributions": [{"author": {"name": "Susanna Clarke"}}],
                },
            }
        ]


GOODREADS_CSV = (
    "Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,"
    "Average Rating,Publisher,Binding,Number of Pages,Year Published,"
    "Original Publication Year,Date Read,Date Added,Bookshelves,"
    "Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,"
    "Private Notes,Read Count,Owned Copies\n"
    '1,El nombre del viento,Patrick Rothfuss,"Rothfuss, Patrick",,'
    '"=""0452286527""","=""9780452286528""",5,4.52,DAW,Paperback,662,2007,2007,'
    "2026/06/20,2026/01/02,fantasy,fantasy (#1),read,Una maravilla.,,,1,0\n"
    '2,Project Hail Mary,Andy Weir,"Weir, Andy",,,,0,4.50,Ballantine,Hardcover,'
    "476,2021,2021,,2026/03/10,,,currently-reading,,,,0,0\n"
    '3,Dune,Frank Herbert,"Herbert, Frank",,,,4,4.25,Ace,Paperback,412,1990,'
    "1965,2026/05/05,2025/12/01,sci-fi,sci-fi (#1),read,,,,2,1\n"
    '4,La paciente silenciosa,Alex Michaelides,"Michaelides, Alex",,,,0,4.18,'
    "Celadon,Hardcover,325,2019,2019,,2026/04/01,,,to-read,,,,0,0\n"
)

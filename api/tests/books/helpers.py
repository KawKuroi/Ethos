"""Helpers del slice de Libros: export CSV de muestra (forma real de Goodreads)."""

from __future__ import annotations

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

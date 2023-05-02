"""
tblio.py

This module contains classes for parsing and working with tables.
"""
from dataclasses import dataclass


class TableError(Exception):
    """ Errors related to table file formatting. """


def tbl_read(path: str, headers: list[str]) -> list[list[str]]:
    with open(path) as f:
        for i, line in enumerate(f):
            if line.startswith('#'): continue  # Skip comments

            # Split line into values
            row = line.split(maxsplit=len(headers)-1)
            if len(row) != len(headers):
                raise TableError(f"Expected {len(headers)} columns, got {len(row)} at line {i}")
            yield row


def tbl_write(headers: list[str], rows: list[list[str]], path: str):
    colwidths = {
        h: max(
            len(h) + (1 if i == 0 else 0),  # Add 1 to first column for # symbol
            *(len(str(getattr(row, h))) for row in rows)
            )
        for i, h in enumerate(headers)}
    with open(path, 'w') as f:
        f.write(' '.join(f'{("#" + h if i == 0 else h): <{colwidths[h]}}' for i, h in enumerate(headers)) + "\n")
        for row in rows:
            f.write(' '.join([f"{getattr(row, h):<{colwidths[h]}}" for h in headers]) + "\n")


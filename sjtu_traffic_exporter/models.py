from dataclasses import dataclass


@dataclass(frozen=True)
class Canteen:
    id: int
    name: str
    occupied: int
    overall: int


@dataclass(frozen=True)
class SubCanteen(Canteen):
    parent: Canteen


@dataclass(frozen=True)
class Library:
    name: str
    occupied: int
    overall: int

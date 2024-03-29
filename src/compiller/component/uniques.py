from typing import Dict


_count: int = 0


def _get_next() -> str:
    global _count
    next_unique = ''
    i = _count
    while i > 0:
        # for explanation see ascii table
        next_unique += chr(i % (ord('z') - ord('A')) + ord('A'))
        i //= ord('z') - ord('A')
    if next_unique == '':
        next_unique = 'A'
    _count += 1
    return next_unique


def restart_uniques_generator():
    global _count
    _count = 0


class UniquesPerComponent:
    _uniques_by_name: Dict[str, str]

    def __init__(self) -> None:
        self._uniques_by_name = dict()

    def get_by_id(self, name: str) -> str:
        v = self._uniques_by_name.get(name)
        if v is not None:
            return v
        self._uniques_by_name[name] = _get_next()
        return self._uniques_by_name[name]

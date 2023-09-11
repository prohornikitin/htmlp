from bs4 import BeautifulSoup


def htmlBeautifulSoup(data: str) -> BeautifulSoup:
    return BeautifulSoup(
        data,
        'html.parser',
        multi_valued_attributes=None,
    )

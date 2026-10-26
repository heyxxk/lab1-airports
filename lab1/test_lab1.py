"""Небольшие проверки для варианта title | fold | words-all | best"""

import unittest

import main


def airport(airport_id, title, country="US", scheduled=False, height=100.0):
    """Создать маленькую тестовую запись аэропорта"""
    return {
        "id": airport_id,
        "title": title,
        "city": "",
        "keywords": "",
        "country": country,
        "kind": "small_airport",
        "elevation_ft": height,
        "latitude": 1.0,
        "longitude": 2.0,
        "scheduled": scheduled,
        "url": ""
    }


class Lab1Tests(unittest.TestCase):
    def setUp(self):
        """Начать каждый тест с пустого состояния"""
        main.records = []
        main.loaded = False
        main.filters = []
        main.last_output = ""

    def test_fold_and_words_all(self):
        """Регистр и порядок слов не влияют на поиск"""
        main.records = [
            airport("1", "Boston Logan International Airport"),
            airport("2", "Boston Airport")
        ]

        best, count, _ = main.search_records("LOGAN boston")

        self.assertEqual(count, 1)
        self.assertEqual(best[1]["id"], "1")

    def test_best_shows_record_with_higher_relevance(self):
        """Более короткое название имеет большую релевантность"""
        main.records = [
            airport("1", "Boston Logan International Airport"),
            airport("2", "Boston Logan Airport")
        ]

        best, count, _ = main.search_records("Boston Logan")

        self.assertEqual(count, 2)
        self.assertEqual(best[1]["id"], "2")
        self.assertEqual(best[0], 2 / 3)

    def test_all_filters_must_pass(self):
        """Два фильтра соединяются через И"""
        main.records = [
            airport("1", "Boston Airport", "US", True),
            airport("2", "Boston Airport", "US", False),
            airport("3", "Boston Airport", "IT", True)
        ]
        main.filters = [
            ["country", "eq", "US"],
            ["scheduled", "eq", True]
        ]

        best, count, _ = main.search_records("Boston")

        self.assertEqual(count, 1)
        self.assertEqual(best[1]["id"], "1")

    def test_empty_query_only_uses_filters(self):
        """Пустой запрос не ищет текст"""
        main.records = [
            airport("1", "One Airport", "US"),
            airport("2", "Two Airport", "IT")
        ]
        main.filters = [["country", "eq", "IT"]]

        best, count, _ = main.search_records("")

        self.assertEqual(count, 1)
        self.assertEqual(best[1]["id"], "2")
        self.assertEqual(best[0], 0.0)


if __name__ == "__main__":
    unittest.main()

from white.lib.paginator import Paginator
import unittest


class PaginatorTest(unittest.TestCase):

    def setUp(self):
        result = [_ for _ in range(1, 10)]
        self.p = Paginator(result, 100, 10, 5, '/test')

    def test_next_link(self):
        self.assertEqual(str(self.p.next_link('next')), '<a href="/test/11">next</a>')
        self.p.page = 22
        self.assertEqual(str(self.p.next_link('next')), '')

    def test_pre_link(self):
        self.assertEqual(str(self.p.pre_link('pre')), '<a href="/test/9">pre</a>')
        self.p.page = 1
        self.assertEqual(str(self.p.pre_link('pre')), '')

    def test_iter(self):
        for _ in range(1, 9):
            next(self.p)
        self.assertEqual(next(self.p), 9)
        self.assertEqual(self.p._index, 9)
        self.assertRaises(StopIteration, lambda: next(self.p))

    def test_len(self):
        self.assertEqual(9, len(self.p))

    def test_links(self):

        self.assertTrue(self.p.links().startswith(
            '<a href="/test">First</a><a href="/test/9">Previous</a><a href="/test/7">7</a>'))
        self.p.page = 0
        self.assertEqual(
            self.p.links(), '<a href="/test/1">1</a><a href="/test/2">2</a><a href="/test/3">3</a><a href="/test/4">4</a><a href="/test/1">Next</a> <a href="/test/20">Last</a>')
        self.p.page = 22
        self.assertEqual(
            self.p.links(), '<a href="/test">First</a><a href="/test/21">Previous</a><a href="/test/19">19</a><a href="/test/20">20</a>')


if __name__ == '__main__':
    unittest.main(verbosity=2)
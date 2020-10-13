from cedict.main import split_string


def test_split_string():
    r = split_string(" a ,b， 词 ，c#d$e/f")
    assert r == ["a", "b", "词", "c", "d", "e", "f"]

def test() -> list[str]:
    ids = []
    for i in [1, 2, 3]:
        ids.append("test")
    return ids


ids = test()
print(ids)

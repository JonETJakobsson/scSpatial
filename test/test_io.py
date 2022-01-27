from scSpatial import io


def test_select_file():
    path = io.select_file()
    assert isinstance(path, str)


test_select_file()

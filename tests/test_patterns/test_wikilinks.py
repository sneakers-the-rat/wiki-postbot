from wiki_postbot.patterns.wikilink import Wikilink, NBack
import pytest
from faker import Faker
import typing
import pdb

class TestStr:
    base = (
        "[[My Basic Wikilink]]",
        Wikilink("My Basic Wikilink")
    )
    multi = (
        "[[Link1]] other text. [[Link2]]",
        [Wikilink("Link1"), Wikilink("Link2")]
    )
    nback_one = (
        "[[^My Wikilink]]",
        Wikilink("My Wikilink", nback=NBack(1,1))
    )
    nback_wildcard = (
        "[[^*My Wikilink]]",
        Wikilink("My Wikilink", nback=NBack(wildcard=True))
    )
    nback_range = (
        "[[^{1,3}Link]]",
        Wikilink("Link", nback=NBack(1,3))
    )
    nback_start = (
        "[[^{2,}Link]]",
        Wikilink("Link", nback=NBack(start=2))
    )
    nback_end = (
        "[[^{,3}Link]]",
        Wikilink("Link", nback=NBack(end=3))
    )
    nback_end_shorthand = (
        "[[^{3}Link]]",
        Wikilink("Link", nback=NBack(end=3))
    )
    section = (
        "[[^{1,3}Link#With section]]",
        Wikilink("Link", nback=NBack(1,3), section="With section")
    )


def pad_garbage(string:str) -> str:
    """Pad a string with garbage text"""
    fake = Faker()
    return fake.paragraph() + " " + string + " " + fake.paragraph()


@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.base])
def test_wikilink(test_string, expected):
    """
    Parse a string with a basic wikilink in it
    """
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    assert len(wl) == 1
    assert wl[0] == expected

@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.multi])
def test_wikilinks(test_string, expected):
    """
    Parse a string that has multiple wikilinks
    """
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    assert len(wl) == 2
    assert wl[0] == expected[0]
    assert wl[1] == expected[1]


@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.nback_one])
def test_nback_one(test_string, expected):
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    # pdb.set_trace()
    assert len(wl) == 1
    assert wl[0] == expected

@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.nback_wildcard])
def test_nback_all(test_string, expected):
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    # pdb.set_trace()
    assert len(wl) == 1
    assert wl[0] == expected

@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.nback_range])
def test_nback_range_full(test_string, expected):
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    # pdb.set_trace()
    assert len(wl) == 1
    assert wl[0] == expected

@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.nback_start])
def test_nback_range_start(test_string, expected):
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    # pdb.set_trace()
    assert len(wl) == 1
    assert wl[0] == expected

@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.nback_end, TestStr.nback_end_shorthand])
def test_nback_range_end(test_string, expected):
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    # pdb.set_trace()
    assert len(wl) == 1
    assert wl[0] == expected

@pytest.mark.parametrize(
    "test_string,expected",
     [TestStr.section])
def test_section(test_string, expected):
    test_string = pad_garbage(test_string)
    wl = Wikilink.parse(test_string)
    # pdb.set_trace()
    assert len(wl) == 1
    assert wl[0] == expected


def test_triplet_full():
    pass

def test_triplet_implicit_single():
    """Test an implicit triplet in a single message"""
    pass

def test_triplet_implicit_thread():
    """Test an implicit triplet where the subject is higher up in the thread"""
    pass

"""The till's alarm: does it reach a reader, and does it reach one only once.

Run with `python3 -m pytest tests/test_checkout_watch.py -q`.

`tools/checkout_watch.py` is the reader the checkout surface has not had since
it shipped on 2026-10-18. The judgement it carries is
`delivery_health.check_checkout`, which has its own suite, so what is new here
is the three things this file decides: what the card is keyed on, what it
says, and the dedupe that makes a daily schedule post one card per fault
instead of one a day.

`tools/board_alarm.py` is covered here too, because it is the mechanic this
watcher and the two older ones now share and it has no command of its own. A
module with no caller of its own is tested through the caller that needed it.

Nothing here touches the network or the board. The checkout surface is built
by calling the real `check_checkout` against a fake fetch, which is the same
double `tests/test_delivery_health.py` uses, and the board is a recording
double. A test that needed a credential would be a test nobody runs on a pull
request.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import board  # noqa: E402
from tools import board_alarm  # noqa: E402
from tools import checkout_watch as cw  # noqa: E402
from tools import delivery_health as dh  # noqa: E402

UTC = timezone.utc

#: The morning the surface was written, when both paid tiers rendered "Opens
#: shortly" with no link behind either one.
NOW = datetime(2026, 10, 23, 23, 30, tzinfo=UTC)

OTHER_COLUMN = "c-done"


# ----------------------------------------------------------- the fake shopfront


def pricing(*offers, note=None):
    """The pricing page's markup, carrying a checkout link per named offer."""
    page = "<html><body>"
    for offer in offers:
        page += f'<a class="pill" href="/api/checkout/{offer}">Buy</a>'
    if note:
        page += f"<span class='pill ghost'>{note}</span>"
    return page + "</body></html>"


def shopfront(page, hops, page_status=200):
    """A `fetch` double: the pricing page, then one answer per checkout route."""
    def fetch(url, timeout=25, follow=True):
        if url.endswith("/pricing"):
            return (page_status, page, {})
        for offer, answer in hops.items():
            if url.endswith(f"/api/checkout/{offer}"):
                return answer
        return (404, "", {})
    return fetch


def surface(page, hops, page_status=200, repo_root=None):
    real = dh.fetch
    try:
        dh.fetch = shopfront(page, hops, page_status)
        return dh.check_checkout(repo_root)
    finally:
        dh.fetch = real


#: The route's real answer to an anonymous caller, measured on 2026-10-18: an
#: account is asked for before a card is.
def sign_up(offer):
    return (303, "", {"location": f"/sign-up?redirect_url=%2Fapi%2Fcheckout%2F{offer}"})


#: The answer an unset offer gets, which is the route sending it home.
HOME = (303, "", {"location": "/pricing"})

ALL = ("trial", "monthly", "lifetime")


def board_payload(items):
    return {"columns": [{"id": "c-sprint", "name": "This sprint", "position": 2},
                        {"id": OTHER_COLUMN, "name": "Done", "position": 5}],
            "items": items}


class Recorder:
    def __init__(self, payload, created=None):
        self.payload, self.calls = payload, []
        self.created = created or {"id": "new-card"}

    def read_board(self, company, env=None, opener=None):
        self.calls.append(("read", company))
        return self.payload

    def api(self, path, method="GET", payload=None, env=None, opener=None):
        self.calls.append((method, path, payload))
        return self.created


@pytest.fixture
def recorder(monkeypatch):
    def install(payload, created=None):
        rec = Recorder(payload, created)
        monkeypatch.setattr(board, "read_board", rec.read_board)
        monkeypatch.setattr(board, "api", rec.api)
        return rec
    return install


# -------------------------------------------------- what the card is keyed on


def test_an_open_till_is_no_card_at_all():
    shop = surface(pricing(*ALL), {o: sign_up(o) for o in ALL})
    assert shop.state == dh.OK
    assert cw.fault(shop) is None


def test_a_page_with_no_link_at_all_is_one_fault_however_many_offers():
    """The live state on 2026-10-18 and still the live state five days later."""
    shop = surface(pricing(note="Opens shortly"), {})
    assert shop.state == dh.FAILING
    assert cw.fault(shop) == "no offer on the pricing page can be bought"


def test_a_half_open_till_is_a_different_fault_and_so_a_different_card():
    """Two tiers opening while the third stays shut is the owner halfway done.

    A key that did not move here would hide the second fact behind the first
    card, and that fact is the one that says the work is nearly finished.
    """
    shop = surface(pricing("trial"), {"trial": sign_up("trial")})
    assert shop.state == dh.FAILING
    key = cw.fault(shop)
    assert key == "lifetime and monthly advertised on the pricing page with no link behind it"
    assert key != cw.fault(surface(pricing(note="Opens shortly"), {}))


def test_a_link_that_leads_nowhere_is_its_own_fault():
    """A configured link the route will not open is not an unconfigured one."""
    hops = {o: sign_up(o) for o in ALL}
    hops["monthly"] = HOME
    shop = surface(pricing(*ALL), hops)
    assert shop.state == dh.FAILING
    assert cw.fault(shop) == "the link for monthly does not open a sale"


def test_a_page_that_errors_blames_the_page_and_not_the_shop():
    """A card saying nothing is for sale would send the owner to the wrong repo."""
    shop = surface("", {}, page_status=500)
    assert shop.state == dh.FAILING
    assert cw.fault(shop) == (
        "the pricing page answers HTTP 500, so no offer is reaching anybody")


def test_the_title_carries_the_fault_so_the_list_view_reads():
    shop = surface(pricing(note="Opens shortly"), {})
    assert cw.card_title(cw.fault(shop)) == (
        "Checkout: no offer on the pricing page can be bought")
    assert cw.card_title(cw.fault(shop)).startswith(cw.TITLE_PREFIX)


# ------------------------------------------------------------ what the card says


def test_the_card_names_the_variables_that_would_open_the_till():
    """A card that says the shop is shut and not what opens it is a complaint."""
    shop = surface(pricing(note="Opens shortly"), {})
    body = cw.card_body(shop, NOW)
    for name in ("POLAR_CHECKOUT_TRIAL", "POLAR_CHECKOUT_MONTHLY",
                 "POLAR_CHECKOUT_LIFETIME"):
        assert name in body
    assert "the site's environment" in body


def test_the_card_never_carries_a_checkout_url():
    """Only names. A checkout url is a secret this repository never sees."""
    shop = surface(pricing("trial"), {"trial": sign_up("trial")})
    body = cw.card_body(shop, NOW)
    assert "://" not in body, "a url reached a card that should carry only names"


def test_the_card_says_why_the_page_is_the_evidence_and_not_the_route():
    """The one thing a future reader is most likely to get wrong.

    `/api/checkout/[plan]` asks a stranger for an account before it looks up
    the link, so an anonymous probe of the route answers the same way whether
    the offer is configured or not. A card that did not say so invites the
    next person to replace the page fetch with a route probe.
    """
    shop = surface(pricing(note="Opens shortly"), {})
    body = cw.card_body(shop, NOW)
    assert "asks for an account before it looks up the link" in body


def test_every_block_of_the_card_is_short_enough_for_the_board():
    """The board refuses a block over 420 characters, in its own words."""
    for shop in (surface(pricing(note="Opens shortly"), {}),
                 surface(pricing("trial"), {"trial": sign_up("trial")})):
        for block in cw.card_body(shop, NOW).split("\n\n"):
            assert len(block) <= board.BODY_BLOCK_LIMIT, block


def test_the_card_does_not_name_the_variables_twice_in_four_sentences():
    """The surface names them because a terminal is its only reader.

    The card has a whole block for the action, so repeating them in the first
    sentence reads as a machine talking rather than as somebody telling you
    the shop is shut.
    """
    shop = surface(pricing(note="Opens shortly"), {})
    first = cw.card_body(shop, NOW).split("\n\n")[0]
    assert "POLAR_CHECKOUT_TRIAL" not in first
    assert "nothing on it a buyer can buy" in first


# --------------------------------------------------------------- the dedupe


def test_a_fault_with_no_card_gets_one_in_the_working_column(recorder):
    rec = recorder(board_payload([]))
    shop = surface(pricing(note="Opens shortly"), {})
    did = cw.post(shop, cw.fault(shop), NOW, company="alexandria")
    assert did["action"] == "created"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items")
    assert payload["title"] == "Checkout: no offer on the pricing page can be bought"
    assert payload["column_id"] == "c-sprint", "the card landed outside the working column"
    assert payload["seat"] == "engineer"
    assert payload["horizon"] == "now"


def test_a_fault_that_already_has_a_fresh_card_is_not_posted_again(recorder):
    card = {"id": "x", "title": "Checkout: no offer on the pricing page can be bought",
            "column_id": "c-sprint", "created_at": NOW.isoformat(), "comments": []}
    rec = recorder(board_payload([card]))
    shop = surface(pricing(note="Opens shortly"), {})
    did = cw.post(shop, cw.fault(shop), NOW, company="alexandria")
    assert did["action"] == "already on the board"
    assert not [c for c in rec.calls if c[0] == "POST"], (
        "a second run on the same fault wrote to the board, which is seven "
        "cards a week on a daily schedule"
    )


def test_a_till_that_stays_shut_gets_one_nudge_a_day(recorder):
    card = {"id": "x", "title": "Checkout: no offer on the pricing page can be bought",
            "column_id": "c-sprint", "created_at": NOW.isoformat(), "comments": []}
    rec = recorder(board_payload([card]))
    later = NOW + timedelta(hours=25)
    shop = surface(pricing(note="Opens shortly"), {})
    did = cw.post(shop, cw.fault(shop), later, company="alexandria")
    assert did["action"] == "nudged"
    (method, path, payload) = rec.calls[-1]
    assert (method, path) == ("POST", "/api/items/x/comments")
    assert "Still shut" in payload["body"]
    assert "25.0 hours" in payload["body"]


def test_a_card_in_done_still_counts_so_a_closed_fault_is_not_reopened(recorder):
    """Every column is searched, including Done."""
    card = {"id": "x", "title": "Checkout: no offer on the pricing page can be bought",
            "column_id": OTHER_COLUMN, "created_at": NOW.isoformat(), "comments": []}
    rec = recorder(board_payload([card]))
    shop = surface(pricing(note="Opens shortly"), {})
    did = cw.post(shop, cw.fault(shop), NOW, company="alexandria")
    assert did["action"] == "already on the board"


def test_a_card_somebody_else_wrote_about_the_till_is_not_mistaken_for_this_one():
    card = {"id": "x", "column_id": "c-sprint",
            "title": "Nothing watched whether a sale can happen at all, so the "
                     "delivery health tool grows a checkout probe"}
    assert board_alarm.find_card(board_payload([card]),
                                 ["no offer on the pricing page can be bought"],
                                 prefix=cw.TITLE_PREFIX) is None


def test_a_different_fault_does_not_match_the_first_faults_card():
    """The half-open till must not be silenced by the fully shut one's card."""
    card = {"id": "x", "column_id": "c-sprint",
            "title": "Checkout: no offer on the pricing page can be bought"}
    shut = surface(pricing("trial"), {"trial": sign_up("trial")})
    assert board_alarm.find_card(board_payload([card]), [cw.fault(shut)],
                                 prefix=cw.TITLE_PREFIX) is None


def test_a_dry_run_reaches_no_board_at_all(monkeypatch):
    def explode(*a, **k):
        raise AssertionError("a dry run called the board")
    monkeypatch.setattr(board, "read_board", explode)
    monkeypatch.setattr(board, "api", explode)
    shop = surface(pricing(note="Opens shortly"), {})
    did = cw.post(shop, cw.fault(shop), NOW, dry_run=True)
    assert did["action"] == "would create"
    assert did["title"] == "Checkout: no offer on the pricing page can be bought"


def test_an_unresolvable_column_still_gets_the_card_posted(recorder, capsys):
    """The card matters and its column does not."""
    rec = recorder({"columns": [{"id": "c-only", "name": "Inbox"}], "items": []})
    shop = surface(pricing(note="Opens shortly"), {})
    did = cw.post(shop, cw.fault(shop), NOW, company="alexandria")
    assert did["action"] == "created"
    (method, path, payload) = rec.calls[-1]
    assert "column_id" not in payload
    said = capsys.readouterr().err
    assert "no column named" in said
    assert "checkout_watch" in said, "a job log cannot tell which watcher warned"


# ---------------------------------------------------------------- the verdict


def _watch(page, hops, page_status=200, **kw):
    real = dh.fetch
    try:
        dh.fetch = shopfront(page, hops, page_status)
        return cw.watch(today=NOW, **kw)
    finally:
        dh.fetch = real


def test_an_open_till_exits_zero_and_posts_nothing(monkeypatch):
    def explode(*a, **k):
        raise AssertionError("a green run called the board")
    monkeypatch.setattr(board, "read_board", explode)
    monkeypatch.setattr(board, "api", explode)
    answer = _watch(pricing(*ALL), {o: sign_up(o) for o in ALL})
    assert answer["exit"] == 0
    assert answer["board"]["action"] == "nothing to post"


def test_a_shut_till_exits_one_and_the_board_carries_it(recorder):
    recorder(board_payload([]))
    answer = _watch(pricing(note="Opens shortly"), {}, company="alexandria")
    assert answer["exit"] == 1
    assert answer["board"]["action"] == "created"


def test_a_page_that_never_answered_posts_nothing_and_is_not_a_quiet_pass(monkeypatch):
    """The direction this guardrail must not go, and the surface had it backwards.

    A seat sandbox with no egress gets silence from the public site. Silence
    read as "there is nothing for sale" would post a card claiming the shop is
    shut on a morning it was open, and an alarm that cries wolf about its own
    network is one nobody reads the day it is right. So the run posts nothing
    and exits 2, which is red rather than green.
    """
    def explode(*a, **k):
        raise AssertionError("a blind run called the board")
    monkeypatch.setattr(board, "read_board", explode)
    monkeypatch.setattr(board, "api", explode)
    answer = _watch("nothing is listening", {}, page_status=0)
    assert answer["checkout"]["state"] == dh.UNKNOWN
    assert answer["exit"] == 2
    assert answer["board"]["action"] == "nothing posted"


def test_a_board_that_refuses_the_card_still_exits_one(recorder, monkeypatch):
    """The finding is real whether or not the board took it."""
    def refuse(*a, **k):
        raise board.BoardError("board said 422 to POST /api/items: nope", code=422)
    monkeypatch.setattr(board, "read_board", refuse)
    answer = _watch(pricing(note="Opens shortly"), {}, company="alexandria")
    assert answer["exit"] == 1
    assert answer["board"]["action"] == "not posted"
    assert "422" in answer["board"]["why"]


def test_the_render_reads_the_same_answer_the_json_does():
    answer = _watch(pricing(*ALL), {o: sign_up(o) for o in ALL})
    text = cw.render(answer)
    assert "A visitor who wants to pay can" in text
    assert answer["checkout"]["headline"] in text


# ------------------------------------------- the mechanic all three now share


def test_an_unrecognised_comment_shape_is_quiet_rather_than_loud():
    """The one direction `board_alarm` errs in, on purpose.

    A card whose comments this cannot read is treated as recently nudged. The
    failure that costs something is a comment every run, which teaches a
    reader to scroll past the card.
    """
    assert board_alarm.needs_nudge({"id": "x"}, NOW) is False
    assert board_alarm.needs_nudge(
        {"id": "x", "comments": [{"nothing": "datable"}]}, NOW) is False


def test_the_newest_comment_is_the_cooldown_and_not_the_oldest():
    card = {"id": "x", "created_at": (NOW - timedelta(days=9)).isoformat(),
            "comments": [{"created_at": (NOW - timedelta(days=5)).isoformat()},
                         {"created_at": (NOW - timedelta(hours=2)).isoformat()}]}
    assert board_alarm.needs_nudge(card, NOW) is False
    assert board_alarm.needs_nudge(card, NOW + timedelta(hours=23)) is True


def test_a_card_with_no_comments_ages_from_its_own_creation():
    card = {"id": "x", "created_at": (NOW - timedelta(hours=25)).isoformat(),
            "comments": []}
    assert board_alarm.needs_nudge(card, NOW) is True


def test_a_statement_is_said_once_and_never_nudged(recorder):
    """`nudge=None` is what makes a fallback card a statement rather than a fault."""
    card = {"id": "x", "title": "Press: 2026-W41 was written on a fallback",
            "column_id": "c-sprint",
            "created_at": (NOW - timedelta(days=30)).isoformat(), "comments": []}
    rec = recorder(board_payload([card]))
    did = board_alarm.place(card, payload=board_payload([card]), title="t",
                            body="b", nudge=None, now=NOW,
                            company="alexandria", tool="test")
    assert did["action"] == "already on the board"
    assert not [c for c in rec.calls if c[0] == "POST"]


def test_all_three_watchers_reach_the_same_copy_of_the_cooldown():
    """Three copies of a rule is three rules, and this one has been copied twice."""
    from tools import drift_watch, press_watch
    card = {"id": "x", "created_at": (NOW - timedelta(hours=25)).isoformat(),
            "comments": []}
    assert (press_watch.needs_nudge(card, NOW)
            == drift_watch.needs_nudge(card, NOW)
            == board_alarm.needs_nudge(card, NOW) is True)
    for module in (press_watch, drift_watch, cw):
        source = Path(module.__file__).read_text()
        assert "board_alarm.place(" in source, (
            f"{module.__name__} grew its own copy of the create-or-nudge step"
        )

import hashlib

# Commentary pools by outcome tier
_HIGH_GAIN = [
    "You could've retired to a beach by now. Probably a nice one. With a butler.",
    "That's enough money to start your own country. A small one, but still.",
    "Your future self is looking back at you with either love or pure rage right now.",
    "Wall Street would've put you on a poster. A very confusing poster.",
    "This is the part where you call your parents and tell them you were right.",
]

_MODERATE_GAIN = [
    "Not bad. You wouldn't be rich-rich, but you'd definitely upgrade your coffee order.",
    "That's a solid new car. Or a very extravagant sofa. You do you.",
    "Respectable gains. Your financial advisor would nod approvingly.",
    "You'd be ahead of most people. Which, honestly, is enough.",
    "Not a yacht, but definitely a really nice kayak.",
]

_SMALL_GAIN = [
    "You'd be slightly better off. Like, 'extra guacamole' better off.",
    "A small win is still a win. Your coffee fund would thank you.",
    "At least you beat inflation. Probably. Maybe. Ask an economist.",
    "Baby steps. Every portfolio starts somewhere.",
    "You'd be ahead — just not in a 'retire at 40' kind of way.",
]

_LOSS = [
    "Ouch. But hey, at least you learned something. Probably.",
    "The market had other plans. Rude, honestly.",
    "This is why they say 'past performance is not indicative of future results.'",
    "Not every bet pays off. The important thing is that you're here, reading this.",
    "The market is humbling. It does this to everyone eventually.",
]


def _pick(pool: list[str], seed: str) -> str:
    """Deterministically pick from a pool using a seed string."""
    index = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(pool)
    return pool[index]


def get_commentary(growth_pct: float, ticker: str, start_date: str) -> str:
    """
    Select contextually appropriate commentary based on growth percentage.
    Uses ticker+start_date as a deterministic seed so the same
    simulation always returns the same commentary.
    """
    seed = f"{ticker}_{start_date}"

    if growth_pct >= 500:
        return _pick(_HIGH_GAIN, seed)
    elif growth_pct >= 50:
        return _pick(_MODERATE_GAIN, seed)
    elif growth_pct >= 0:
        return _pick(_SMALL_GAIN, seed)
    else:
        return _pick(_LOSS, seed)

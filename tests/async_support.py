"""Run test-double coroutines that must complete without scheduling I/O."""


def run_immediate(coroutine):
    """Execute an immediate coroutine and reject hidden event-loop work.

    These unit tests use in-memory async doubles. A real event loop is covered
    by opt-in runtime/live validation, while this helper keeps the offline suite
    usable in sandboxes that prohibit the Windows event-loop socketpair.
    """

    try:
        coroutine.send(None)
    except StopIteration as stopped:
        return stopped.value
    coroutine.close()
    raise AssertionError("unit-test coroutine suspended; use an integration test")


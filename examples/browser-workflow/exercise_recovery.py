import sys
import asyncio
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

from workflow import serve, open_workflow

from openai.lib.browser import BrowserConfirmContext


async def allow(_action: BrowserConfirmContext) -> bool:
    return True


async def check(mode: str) -> None:
    with serve() as fixture:
        if mode == "storage":
            async with open_workflow(fixture, "A", confirm=allow) as workflow:
                for key in ("bookings", "correspondence"):
                    for value in (None, [], ["REQ-401"], 17, True, "booked"):
                        await workflow.page.evaluate(
                            """({key,value}) => {
                          localStorage.setItem('workflow.A.' + key, JSON.stringify(value));
                          localStorage.setItem('workflow.A.selected', JSON.stringify('REQ-401'));
                          localStorage.setItem('workflow.B.' + key, JSON.stringify({ keep: 'other fixture' }));
                        }""",
                            {"key": key, "value": value},
                        )
                        await workflow.page.goto(fixture[0] + "/dispatch?fixture=A")
                        result = await workflow.page.evaluate(
                            """(key) => ({
                          invalid: localStorage.getItem('workflow.A.' + key),
                          selected: localStorage.getItem('workflow.A.selected'),
                          other: localStorage.getItem('workflow.B.' + key),
                        })""",
                            key,
                        )
                        assert result == {
                            "invalid": None,
                            "selected": '"REQ-401"',
                            "other": '{"keep":"other fixture"}',
                        }, (key, value, result)
                        assert await workflow.stored() == {"bookings": {}, "correspondence": {}}
                        assert await workflow.verify() is False
                await workflow.page.evaluate("""()=>localStorage.setItem('workflow.A.bookings', JSON.stringify({
                    obsolete:{request:'obsolete',slot:'R2',time:'10:00'},'REQ-401':null
                }))""")
                await workflow.page.goto(fixture[0] + "/dispatch?fixture=A")
                assert await workflow.page.locator("[data-send]").count() == 0
                assert await workflow.page.locator("[data-revise]").count() == 2
                await workflow.page.locator('[data-revise="obsolete"]').click()
                await workflow.page.locator('[data-revise="REQ-401"]').click()
                assert await workflow.stored() == {"bookings": {}, "correspondence": {}}
                assert await workflow.verify() is False
                correct = {
                    "bookings": {"REQ-401": {"request": "REQ-401", "slot": "R2", "time": "10:00"}},
                    "correspondence": {
                        "REQ-401": {"request": "REQ-401", "slot": "R2", "recipient": "cedar@example.test"}
                    },
                }
                invalid_records: tuple[object, ...] = (None, [], 17, {}, {"slot": "R2"})
                for key in ("bookings", "correspondence"):
                    for value in invalid_records:
                        records = {**correct, key: {"REQ-401": value}}
                        await workflow.page.evaluate(
                            """saved => {
                              localStorage.setItem('workflow.A.bookings', JSON.stringify(saved.bookings));
                              localStorage.setItem('workflow.A.correspondence', JSON.stringify(saved.correspondence));
                            }""",
                            records,
                        )
                        assert await workflow.verify() is False, (key, value)
                        assert workflow.verified_records == records, "Verification must preserve saved evidence"
                await workflow.page.evaluate(
                    """saved => {
                      localStorage.setItem('workflow.A.bookings', JSON.stringify(saved.bookings));
                      localStorage.setItem('workflow.A.correspondence', JSON.stringify(saved.correspondence));
                    }""",
                    correct,
                )
                assert await workflow.verify(), "Valid records remain verifiable after malformed ones"
            assert workflow.page.is_closed()
            print(
                "PASS storage:12 invalid collection types,10 malformed selected records, valid saved proof,2 stale records revised, close"
            )
        elif mode == "startup":
            loop = asyncio.get_running_loop()
            received = asyncio.Event()
            release = threading.Event()

            class Handler(BaseHTTPRequestHandler):
                @override
                def log_message(self, format: str, *args: object) -> None:
                    pass

                def do_GET(self) -> None:
                    loop.call_soon_threadsafe(received.set)
                    release.wait(10)
                    try:
                        self.send_response(200)
                        self.end_headers()
                    except (BrokenPipeError, ConnectionResetError):
                        # Cancellation closes the client before this delayed response.
                        pass

            slow = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=slow.serve_forever, daemon=True)
            thread.start()

            async def starting():
                async with open_workflow(("http://127.0.0.1:" + str(slow.server_port), fixture[1]), "A", confirm=allow):
                    raise AssertionError("Stopped startup reached handoff")

            task = asyncio.create_task(starting())
            try:
                await asyncio.wait_for(received.wait(), 7)
                task.cancel()
                try:
                    await asyncio.wait_for(asyncio.shield(task), 1.2)
                except asyncio.CancelledError:
                    pass
                else:
                    raise AssertionError("Cancelled startup should not yield a workflow")
                print("PASS startup: task cancellation drains owned browser during finite held navigation")
            finally:
                release.set()
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                await asyncio.to_thread(slow.shutdown)
                slow.server_close()
                thread.join()
        else:
            raise AssertionError("Use storage or startup")


asyncio.run(check(sys.argv[1]))

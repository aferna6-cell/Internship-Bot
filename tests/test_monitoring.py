from internship_bot.monitoring import ApplicationMonitor


class Recorder:
    def __init__(self) -> None:
        self.messages = []

    def notify(self, message: str) -> None:
        self.messages.append(message)


def test_monitoring_records_success_failure() -> None:
    recorder = Recorder()
    monitor = ApplicationMonitor([recorder])
    monitor.record_success("greenhouse", "sam")
    monitor.record_failure("workday", "sam", RuntimeError("boom"))

    assert any("succeeded" in msg for msg in recorder.messages)
    assert any("failed" in msg for msg in recorder.messages)

class FeishuAdapter:
    def verify(self, event: object) -> bool:
        return True

    def handle(self, event: object) -> object:
        return event

class AsyncIteratorWrapper:
    def __init__(self, iterator):
        self.iterator = iter(iterator)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iterator)
        except StopIteration:
            raise StopAsyncIteration

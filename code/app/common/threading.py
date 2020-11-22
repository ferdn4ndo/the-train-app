from concurrent.futures import thread, wait


class ThreadingExecutor:

    def __init__(self, function, max_thread_workers=32):
        self.function = function
        self.max_thread_workers = max_thread_workers

    def run(self, arguments_set):
        total_executors = min(self.max_thread_workers, len(arguments_set))
        executor = thread.ThreadPoolExecutor(max_workers=total_executors)
        future_items = [executor.submit(self.function, argument) for argument in arguments_set]
        wait(future_items)
        for result in future_items:
            result.result()

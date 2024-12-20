from concurrent.futures import ThreadPoolExecutor
from asyncio import set_event_loop, new_event_loop, run_coroutine_threadsafe
from functools import partial

class ThreadPoolDeps:
    # 일단 스레드 풀 3
    thread_pool = ThreadPoolExecutor(max_workers=3)
    
    def __init__(self):
        return ThreadPoolDeps.thread_pool

async def run_async_by_multi_thread(func, *args, **kwargs):
    executor = ThreadPoolDeps()
    
    def run_event_loop_on_thread(func, *args, **kwargs):
        # 루프 생성 후 스레드의 루프로 설정
        loop = new_event_loop()
        set_event_loop(loop)
        # await 처럼 실행 후 루프는 닫기
        result = loop.run_until_complete(func(*args, **kwargs))
        loop.close()
        
        return result
    # 함수 인자 고정
    func_with_args = partial(run_event_loop_on_thread, func, *args, **kwargs)
    # executor 스레드풀에서 실행
    future = executor.submit(func_with_args)
    return future.result()
    
    
    
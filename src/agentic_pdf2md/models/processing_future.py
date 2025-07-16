import asyncio
from typing import Generic, TypeVar, Callable, Awaitable, List, Optional
from ..exceptions import OperationCancelledException

T = TypeVar('T')


class ProcessingFuture(Generic[T]):
    """Promise-like object for handling async operation results."""
    
    def __init__(self, operation_name: str = "Unknown"):
        self.operation_name = operation_name
        self._result: Optional[T] = None
        self._error: Optional[Exception] = None
        self._completed = False
        
        # Promise-like callbacks
        self._then_callbacks: List[Callable[[T], Awaitable[None]]] = []
        self._catch_callbacks: List[Callable[[Exception], Awaitable[None]]] = []
        self._finally_callbacks: List[Callable[[], Awaitable[None]]] = []
        
        # Task management
        self._task: Optional[asyncio.Task] = None
    
    async def then(self, callback: Callable[[T], Awaitable[None]]) -> 'ProcessingFuture[T]':
        """Add a success callback."""
        self._then_callbacks.append(callback)
        if self._completed and not self._error:
            await callback(self._result)
        return self
    
    async def catch(self, callback: Callable[[Exception], Awaitable[None]]) -> 'ProcessingFuture[T]':
        """Add an error callback."""
        self._catch_callbacks.append(callback)
        if self._completed and self._error:
            await callback(self._error)
        return self
    
    async def finally_(self, callback: Callable[[], Awaitable[None]]) -> 'ProcessingFuture[T]':
        """Add a finally callback."""
        self._finally_callbacks.append(callback)
        if self._completed:
            await callback()
        return self
    
    async def start_operation(self, coro: Awaitable[T]) -> 'ProcessingFuture[T]':
        """Start an async operation and return immediately."""
        async def _run_operation():
            try:
                result = await coro
                await self._complete(result)
            except Exception as e:
                await self._fail(e)
        
        self._task = asyncio.create_task(_run_operation())
        return self
    
    @classmethod
    async def create_and_start(cls, coro: Awaitable[T], operation_name: str = "Unknown") -> 'ProcessingFuture[T]':
        """Factory method to create and start in one call."""
        future = cls(operation_name)
        return await future.start_operation(coro)
    
    async def wait_for_completion(self) -> T:
        """Wait for the operation to complete."""
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError as exc:
                raise OperationCancelledException(f"Operation '{self.operation_name}' was cancelled") from exc
        
        if self._error:
            raise self._error
        return self._result
    
    def is_completed(self) -> bool:
        return self._completed
    
    def get_result(self) -> Optional[T]:
        return self._result
    
    def get_error(self) -> Optional[Exception]:
        return self._error
    
    def cancel(self) -> bool:
        """Cancel the underlying task if it exists."""
        if self._task and not self._task.done():
            return self._task.cancel()
        return False
    
    async def _complete(self, result: T):
        """Internal method to complete the future."""
        self._result = result
        self._completed = True
        
        # Execute callbacks
        for callback in self._then_callbacks:
            try:
                await callback(result)
            except Exception as e:
                print(f"Error in then callback: {e}")
        
        for callback in self._finally_callbacks:
            try:
                await callback()
            except Exception as e:
                print(f"Error in finally callback: {e}")
    
    async def _fail(self, error: Exception):
        """Internal method to fail the future."""
        self._error = error
        self._completed = True
        
        # Execute callbacks
        for callback in self._catch_callbacks:
            try:
                await callback(error)
            except Exception as e:
                print(f"Error in catch callback: {e}")
        
        for callback in self._finally_callbacks:
            try:
                await callback()
            except Exception as e:
                print(f"Error in finally callback: {e}")
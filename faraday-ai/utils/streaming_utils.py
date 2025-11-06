"""
FARADAY AI - Streaming Utilities
Helper functions for streaming text and audio
"""

import asyncio
from typing import AsyncIterator, Iterator

from utils.logger import logger


async def stream_text(
    text: str,
    chunk_size: int = 10,
    delay: float = 0.05
) -> AsyncIterator[str]:
    """
    Stream text in chunks with delay (simulates typing effect).

    Args:
        text: Text to stream
        chunk_size: Characters per chunk
        delay: Delay between chunks in seconds

    Yields:
        Text chunks
    """
    try:
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(delay)

    except Exception as e:
        logger.error(f"❌ Error streaming text: {e}")


async def stream_audio(
    audio_data: bytes,
    chunk_size: int = 1024
) -> AsyncIterator[bytes]:
    """
    Stream audio data in chunks.

    Args:
        audio_data: Audio bytes
        chunk_size: Bytes per chunk

    Yields:
        Audio chunks
    """
    try:
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.01)  # Small delay for smooth streaming

    except Exception as e:
        logger.error(f"❌ Error streaming audio: {e}")


async def merge_streams(*streams: AsyncIterator) -> AsyncIterator:
    """
    Merge multiple async streams into one.

    Args:
        *streams: Async iterators to merge

    Yields:
        Items from all streams
    """
    try:
        tasks = [asyncio.create_task(anext(stream)) for stream in streams]

        while tasks:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            for task in done:
                try:
                    result = task.result()
                    yield result

                    # Get next item from this stream
                    stream_index = tasks.index(task)
                    tasks[stream_index] = asyncio.create_task(anext(streams[stream_index]))

                except StopAsyncIteration:
                    # Stream finished
                    tasks.remove(task)

    except Exception as e:
        logger.error(f"❌ Error merging streams: {e}")


def chunked_iterator(iterator: Iterator, chunk_size: int) -> Iterator[list]:
    """
    Convert iterator to chunked iterator.

    Args:
        iterator: Input iterator
        chunk_size: Chunk size

    Yields:
        Chunks as lists
    """
    chunk = []
    for item in iterator:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk


async def buffer_stream(
    stream: AsyncIterator,
    buffer_size: int = 10
) -> AsyncIterator:
    """
    Buffer async stream for smoother output.

    Args:
        stream: Input stream
        buffer_size: Buffer size

    Yields:
        Buffered items
    """
    buffer = []

    try:
        async for item in stream:
            buffer.append(item)

            if len(buffer) >= buffer_size:
                for buffered_item in buffer:
                    yield buffered_item
                buffer = []

        # Yield remaining items
        for buffered_item in buffer:
            yield buffered_item

    except Exception as e:
        logger.error(f"❌ Error buffering stream: {e}")


# Export
__all__ = [
    'stream_text',
    'stream_audio',
    'merge_streams',
    'chunked_iterator',
    'buffer_stream',
]

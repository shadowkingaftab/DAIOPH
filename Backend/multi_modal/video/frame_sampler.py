"""FrameSampler - samples frames from video."""

from typing import Any, Dict, List, Optional


class FrameSampler:
    """Samples frames from video streams."""

    def __init__(self, fps: int = 1) -> None:
        """Initialize frame sampler.

        Args:
            fps: Frames to sample per second.
        """
        self._fps = fps

    def sample(self, video: Any) -> List[Any]:
        """Sample frames from video.

        Args:
            video: Video data.

        Returns:
            List[Any]: Sampled frames.
        """
        return []

    def get_fps(self) -> int:
        """Get sampling FPS.

        Returns:
            int: FPS.
        """
        return self._fps

</final_file_content>
</write_to_file></tool_call>
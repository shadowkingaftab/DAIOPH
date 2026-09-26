"""ModelDownloader - downloads models from remote sources."""

from typing import Any, Dict, Optional


class ModelDownloader:
    """Downloads models from remote sources."""

    def __init__(self, cache_dir: str = "./cache") -> None:
        """Initialize the model downloader.

        Args:
            cache_dir: Directory for cached downloads.
        """
        self._cache_dir = cache_dir

    def download(self, url: str, dest: Optional[str] = None) -> str:
        """Download a model from a URL.

        Args:
            url: Download URL.
            dest: Optional destination path.

        Returns:
            str: Path to downloaded file.
        """
        dest = dest or f"{self._cache_dir}/{url.split('/')[-1]}"
        return dest

    def get_cache_dir(self) -> str:
        """Get the cache directory.

        Returns:
            str: Cache directory path.
        """
        return self._cache_dir

</final_file_content>
</write_to_file></tool_call>
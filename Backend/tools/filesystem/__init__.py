"""Filesystem tools: read, write, search, metadata, watch, organize."""

from tools.filesystem.metadata import fs_metadata, get_metadata
from tools.filesystem.organize import fs_organize, organize_files
from tools.filesystem.read import fs_read, read_file
from tools.filesystem.search import fs_search, search_files
from tools.filesystem.watcher import create_watcher, fs_watch
from tools.filesystem.write import fs_write, write_file

__all__ = [
    "create_watcher", "fs_metadata", "fs_organize", "fs_read", "fs_search",
    "fs_watch", "fs_write", "get_metadata", "organize_files",
    "read_file", "search_files", "write_file",
]

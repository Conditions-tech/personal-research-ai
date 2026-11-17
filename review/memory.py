"""Pre-load RAM gate for app-initiated local analysis; no network or model access."""

import ctypes


# Same pre-load gate as the approved Qwen2.5 benchmark; never relaxed to fit.
MIN_AVAILABLE_BYTES = 4 * 1024 ** 3


class MemoryGateError(ValueError):
    """Safe to show; contains no research content."""


def available_memory_bytes():
    """Available physical RAM (Windows); page-file space does not count."""
    class Memory(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (n, ctypes.c_ulonglong) for n in ("total", "available", "page", "available_page",
                                            "virtual", "available_virtual", "extended")]
    data = Memory()
    data.length = ctypes.sizeof(data)
    try:
        measured = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(data))
    except (AttributeError, OSError):
        measured = False
    if not measured:
        raise MemoryGateError("Cannot measure available memory; no model was loaded. Review work is unchanged.")
    return data.available


def require_memory():
    """Refuse before a generation request can load the model into too little RAM."""
    available = available_memory_bytes()
    if available < MIN_AVAILABLE_BYTES:
        raise MemoryGateError(
            f"Only {available / 1024 ** 3:.1f} GiB of RAM is available; local analysis needs "
            f"{MIN_AVAILABLE_BYTES / 1024 ** 3:.0f} GiB before loading the model. Close other "
            "applications and try again. No model was loaded; review work is unchanged.")
    return available

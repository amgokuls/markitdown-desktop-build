# Hook for markitdown — collect all entry_points (converters)
from PyInstaller.utils.hooks import collect_all, collect_entry_point

datas, binaries, hiddenimports = collect_all("markitdown")

# Also collect magika model data
try:
    magika_datas, magika_bins, magika_hidden = collect_all("magika")
    datas += magika_datas
    binaries += magika_bins
    hiddenimports += magika_hidden
except Exception:
    pass

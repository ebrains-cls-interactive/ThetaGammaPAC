import numpy as np

POP_COLORS = {
    'OLM_pop': '#1f77b4',   # blue
    'PVBC_pop': '#2ca02c',  # green
    'PYR_pop': '#ff7f0e',   # orange
}


POP_LABELS = {
    'OLM_pop': 'OLM',
    'PVBC_pop': 'PVBC',
    'PYR_pop': 'PYR',
}

BIN_MS = 4  # 4 ms bins → 250 Hz (matches project analysis defaults)
LOW_FQ_RANGE = np.arange(1, 10, 0.5)   # phase frequencies (theta scan)
HIGH_FQ_RANGE = np.arange(15, 50, 2)   # amplitude frequencies (gamma)


def get_pop_spikes(data, pop_name):
    """Extract spike times and IDs for a given population, after starttime."""
    pops = data['populations']
    cfg = data['simConfig']
    rng = pops[pop_name]
    starttime = cfg.get('starttime', 300)

    spkt = np.array(data['spkt'])
    spkid = np.array(data['spkid'])

    mask = (spkid >= rng['start']) & (spkid < rng['end']) & (spkt >= starttime)
    return spkt[mask], spkid[mask]


def spikes_to_rate(spkt, n_cells, duration_ms, starttime_ms, bin_ms=4):
    """Convert spike times to a population firing rate signal.

    Parameters
    ----------
    spkt : array of spike times (ms)
    n_cells : number of cells in the population
    duration_ms : total simulation duration (ms)
    starttime_ms : analysis start time (ms)
    bin_ms : bin width in ms (default 4 → 250 Hz sampling)

    Returns
    -------
    t_sec : time vector in seconds
    rate_hz : firing rate in Hz
    fs : sampling rate in Hz
    """
    bins = np.arange(starttime_ms, duration_ms + bin_ms, bin_ms)
    counts, edges = np.histogram(spkt, bins=bins)
    rate_hz = counts / (bin_ms / 1000.0) / n_cells  # spikes/sec/cell
    t_sec = (edges[:-1] + bin_ms / 2) / 1000.0  # bin centers in seconds
    fs = 1000.0 / bin_ms
    return t_sec, rate_hz, fs

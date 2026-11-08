import ipywidgets
from matplotlib import pyplot as plt
from scipy import signal

from clsiwidgets.ui.base_widget import BaseWidget
from clsiwidgets.ui.utils.analysis import BIN_MS, POP_COLORS, POP_LABELS, get_pop_spikes, spikes_to_rate


class LevelTwoAnalysisWidget(ipywidgets.VBox, BaseWidget):

    def __init__(self):

        super().__init__()

        self._title_widget = ipywidgets.HTML(value="<h3>Level 2 — Population firing rates and Power Spectral Density</h3>")
        self._sub_title_widget = ipywidgets.HTML(value="<p>Spike trains are binned (4 ms bins → 250 Hz sampling rate) and converted to population firing rates. The PSD is computed using Welch's method.<br>This reproduces the analysis shown in Fig 2E-F of Ponzi et al. (2023).<br>Key features to look for:</p><ul><li><b>Theta peak</b> (~4–5 Hz) — strongest in OLM</li><li><b>Gamma peak</b> (~25 Hz) — visible in all populations</li></ul>")

        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

        self.output = ipywidgets.Output()
        self.children = [self._title_widget, self._sub_title_widget, self.output]

    def plot(self, runs: dict) -> None:
        self._title_widget.layout.display = ""
        self._sub_title_widget.layout.display = ""

        self.output.clear_output()
        with self.output:

            for label, data in runs.items():
                cfg = data['simConfig']
                pops = data['populations']
                starttime = cfg.get('starttime', 300)
                duration = cfg['duration']

                fig, axes = plt.subplots(1, 3, figsize=(16, 4))
                fig.suptitle(f'{label}', fontsize=13, fontweight='bold')

                # --- Panel 1: Population firing rates ---
                ax = axes[0]
                for pop_name in ['OLM_pop', 'PVBC_pop', 'PYR_pop']:
                    spkt, _ = get_pop_spikes(data, pop_name)
                    n_cells = pops[pop_name]['end'] - pops[pop_name]['start']
                    t_sec, rate, fs = spikes_to_rate(spkt, n_cells, duration, starttime, BIN_MS)
                    ax.plot(t_sec, rate, c=POP_COLORS[pop_name], label=POP_LABELS[pop_name], alpha=0.8, lw=0.8)

                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Rate (Hz)')
                ax.set_title('Population firing rates')
                ax.legend(fontsize=9)

                # --- Panel 2: PSD (linear y) ---
                ax = axes[1]
                for pop_name in ['OLM_pop', 'PVBC_pop', 'PYR_pop']:
                    spkt, _ = get_pop_spikes(data, pop_name)
                    n_cells = pops[pop_name]['end'] - pops[pop_name]['start']
                    _, rate, fs = spikes_to_rate(spkt, n_cells, duration, starttime, BIN_MS)
                    nperseg = min(256, len(rate))
                    noverlap = min(128, nperseg - 1)

                    freqs, psd = signal.welch(
                        rate,
                        fs=fs,
                        nperseg=nperseg,
                        noverlap=noverlap,
                        scaling="density"
                    )

                    ax.plot(freqs, psd, c=POP_COLORS[pop_name], label=POP_LABELS[pop_name])

                ax.set_xlabel('Frequency (Hz)')
                ax.set_ylabel('Power')
                ax.set_title('PSD (Welch)')
                ax.set_xlim(0, 60)
                ax.legend(fontsize=9)

                # --- Panel 3: PSD (log y) ---
                ax = axes[2]
                for pop_name in ['OLM_pop', 'PVBC_pop', 'PYR_pop']:
                    spkt, _ = get_pop_spikes(data, pop_name)
                    n_cells = pops[pop_name]['end'] - pops[pop_name]['start']
                    _, rate, fs = spikes_to_rate(spkt, n_cells, duration, starttime, BIN_MS)
                    nperseg = min(256, len(rate))
                    noverlap = min(128, nperseg - 1)

                    freqs, psd = signal.welch(
                        rate,
                        fs=fs,
                        nperseg=nperseg,
                        noverlap=noverlap,
                        scaling="density"
                    )

                    ax.semilogy(freqs, psd, c=POP_COLORS[pop_name], label=POP_LABELS[pop_name])

                ax.set_xlabel('Frequency (Hz)')
                ax.set_ylabel('Power (log)')
                ax.set_title('PSD (log scale)')
                ax.set_xlim(0, 60)
                ax.legend(fontsize=9)

                plt.tight_layout()
                plt.show()


    def clear(self) -> None:
        self.output.clear_output()
        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

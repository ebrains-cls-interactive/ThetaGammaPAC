import ipywidgets
from IPython.display import display
from matplotlib import pyplot as plt
from scipy import signal

from clsiwidgets.ui.base_widget import BaseWidget
from clsiwidgets.ui.utils.analysis import (
    BIN_MS,
    POP_COLORS,
    POP_LABELS,
    get_pop_spikes,
    spikes_to_rate,
)


class LevelFourAnalysisWidget(ipywidgets.VBox, BaseWidget):

    def __init__(self):

        super().__init__()

        self._title_widget = ipywidgets.HTML(value="<h3>Level 4 — Compare across parameter values</h3>")
        self._sub_title_widget = ipywidgets.HTML(value="<p>If you loaded multiple runs (different values of the swept parameter), this section overlays their PSDs and compares PAC metrics side by side.</p>")

        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

        self.output = ipywidgets.Output()
        self.children = [self._title_widget, self._sub_title_widget, self.output]

    def plot(self, runs: dict, pac_summary: list = []) -> None:
        self._title_widget.layout.display = ""
        self._sub_title_widget.layout.display = ""

        self.output.clear_output()
        with self.output:
            if len(runs) < 2:
                print("Only 1 run loaded — load multiple runs to enable comparison.")
                print("Go up and add more results.")
            else:
                # --- PSD comparison ---
                for pop_name in ['OLM_pop', 'PVBC_pop', 'PYR_pop']:
                    fig, ax = plt.subplots(figsize=(8, 4))

                    for label, data in runs.items():
                        cfg = data['simConfig']
                        pops = data['populations']
                        starttime = cfg.get('starttime', 300)
                        duration = cfg['duration']

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

                        ax.semilogy(freqs, psd, label=label, alpha=0.85)

                    ax.set_xlabel('Frequency (Hz)')
                    ax.set_ylabel('Power (log)')
                    ax.set_title(f'PSD comparison — {POP_LABELS[pop_name]}')
                    ax.set_xlim(0, 60)
                    ax.legend(fontsize=8)
                    plt.tight_layout()
                    plt.show()

            if len(runs) >= 2 and pac_summary:

                import pandas as pd
                df = pd.DataFrame(pac_summary)

                # --- PAC max comparison bar chart ---
                fig, axes = plt.subplots(1, 3, figsize=(15, 4))
                fig.suptitle('PAC peak comparison across runs', fontsize=13, fontweight='bold')

                for i, pop in enumerate(['OLM', 'PVBC', 'PYR']):
                    ax = axes[i]
                    sub = df[df['population'] == pop]
                    bars = ax.bar(range(len(sub)), sub['pac_max'],
                                tick_label=sub['run'].values,
                                color=POP_COLORS[f'{pop}_pop'], alpha=0.8)
                    ax.set_ylabel('PAC max')
                    ax.set_title(pop)
                    ax.tick_params(axis='x', rotation=45, labelsize=8)

                plt.tight_layout()
                plt.show()

                # --- Summary table ---
                print("\nPAC Summary Table:")
                pivot = df.pivot_table(index='run', columns='population',
                                    values=['pac_max', 'peak_theta_hz', 'peak_gamma_hz'])
                display(pivot)


    def clear(self) -> None:
        self.output.clear_output()
        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

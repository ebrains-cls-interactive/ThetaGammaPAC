import ipywidgets
import numpy as np
import pandas as pd
from IPython.display import display
from matplotlib import pyplot as plt
from pactools import Comodulogram

from clsiwidgets.ui.base_widget import BaseWidget
from clsiwidgets.ui.utils.analysis import (
    BIN_MS,
    HIGH_FQ_RANGE,
    LOW_FQ_RANGE,
    POP_LABELS,
    get_pop_spikes,
    spikes_to_rate,
)


class LevelThreeAnalysisWidget(ipywidgets.VBox, BaseWidget):

    def __init__(self):

        super().__init__()

        self._title_widget = ipywidgets.HTML(value="<h3>Level 3 — Phase-Amplitude Coupling (PAC)</h3>")
        self._sub_title_widget = ipywidgets.HTML(value="<p>PAC measures how the amplitude of high-frequency (gamma) oscillations is modulated by the phase of low-frequency (theta) oscillations.<br>We compute a <b>comodulogram</b> using <code>pactools</code>, scanning:</p><ul><li>Phase frequencies: 1–10 Hz (theta range)</li><li>Amplitude frequencies: 15–50 Hz (low gamma range)</li></ul><p>This reproduces the analysis shown in Fig 2G of Ponzi et al. (2023).<br>Strong PAC appears as a warm-coloured blob in the comodulogram around theta ~4–5 Hz × gamma ~25 Hz.</p>")

        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

        self._sub_section_title = ipywidgets.HTML(value="<h3>PAC summary metrics</h3>")
        self._sub_section_description = ipywidgets.HTML(value="<p>Extract the peak PAC value and the corresponding theta/gamma frequency pair for each population and run.</p>")
        self._sub_section_title.layout.display = "none"
        self._sub_section_description.layout.display = "none"
        self._sub_section_output = ipywidgets.Output()

        self.output = ipywidgets.Output()
        self.children = [self._title_widget, self._sub_title_widget, self.output, self._sub_section_title, self._sub_section_description, self._sub_section_output]

        self.pac_summary = []

    def plot(self, runs: dict) -> None:
        self._title_widget.layout.display = ""
        self._sub_title_widget.layout.display = ""

        self.output.clear_output()
        self._sub_section_output.clear_output()
        self.pac_summary = []
        with self.output:

            for label, data in runs.items():
                cfg = data['simConfig']
                pops = data['populations']
                starttime = cfg.get('starttime', 300)
                duration = cfg['duration']

                fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
                fig.suptitle(f'PAC Comodulograms — {label}', fontsize=13, fontweight='bold')

                for i, pop_name in enumerate(['OLM_pop', 'PVBC_pop', 'PYR_pop']):
                    spkt, _ = get_pop_spikes(data, pop_name)
                    n_cells = pops[pop_name]['end'] - pops[pop_name]['start']
                    _, rate, fs = spikes_to_rate(spkt, n_cells, duration, starttime, BIN_MS)

                    # pactools expects a 1D signal
                    sig = rate.astype(np.float64)

                    estimator = Comodulogram(
                        fs=fs,
                        low_fq_range=LOW_FQ_RANGE,
                        high_fq_range=HIGH_FQ_RANGE,
                        method='penny',
                        progress_bar=False,
                    )
                    estimator.fit(sig)

                    ax = axes[i]
                    estimator.plot(axs=[ax])
                    ax.set_title(POP_LABELS[pop_name])

                plt.tight_layout()
                plt.show()

            for label, data in runs.items():
                cfg = data['simConfig']
                pops = data['populations']
                starttime = cfg.get('starttime', 300)
                duration = cfg['duration']

                for pop_name in ['OLM_pop', 'PVBC_pop', 'PYR_pop']:
                    spkt, _ = get_pop_spikes(data, pop_name)
                    n_cells = pops[pop_name]['end'] - pops[pop_name]['start']
                    _, rate, fs = spikes_to_rate(spkt, n_cells, duration, starttime, BIN_MS)

                    sig = rate.astype(np.float64)

                    estimator = Comodulogram(
                        fs=fs,
                        low_fq_range=LOW_FQ_RANGE,
                        high_fq_range=HIGH_FQ_RANGE,
                        method='penny',
                        progress_bar=False,
                    )
                    estimator.fit(sig)

                    comod = estimator.comod_
                    pac_max = comod.max()
                    pac_mean = comod.mean()
                    idx = np.unravel_index(comod.argmax(), comod.shape)
                    peak_theta = LOW_FQ_RANGE[idx[0]]
                    peak_gamma = HIGH_FQ_RANGE[idx[1]]

                    self.pac_summary.append({
                        'run': label,
                        'population': POP_LABELS[pop_name],
                        'pac_max': round(float(pac_max), 6),
                        'pac_mean': round(float(pac_mean), 6),
                        'peak_theta_hz': float(peak_theta),
                        'peak_gamma_hz': float(peak_gamma),
                    })

            # Display as a table
            try:
                self._sub_section_title.layout.display = ""
                self._sub_section_description.layout.display = ""
                df_pac = pd.DataFrame(self.pac_summary)
                with self._sub_section_output:
                    display(df_pac)
            except ImportError:
                for row in self.pac_summary:
                    print(row)


    def clear(self) -> None:
        self.output.clear_output()
        self._sub_section_output.clear_output()
        self._sub_section_title.layout.display = "none"
        self._sub_section_description.layout.display = "none"
        self.pac_summary = []
        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

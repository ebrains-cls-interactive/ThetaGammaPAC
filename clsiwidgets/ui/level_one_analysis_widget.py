
import ipywidgets
import matplotlib.pyplot as plt
from IPython.display import display

from clsiwidgets.ui.base_widget import BaseWidget
from clsiwidgets.ui.utils.analysis import POP_COLORS, POP_LABELS, get_pop_spikes


class LevelOneAnalysisWidget(ipywidgets.VBox, BaseWidget):

    def __init__(self):

        super().__init__()

        self._title_widget = ipywidgets.HTML(value="<h3>Level 1 — Raster plot and firing rate statistics</h3>")
        self._sub_title_widget = ipywidgets.HTML(value='<p>The raster plot shows every spike as a dot. Colour-coded by population: <b>OLM</b> (blue), <b>PVBC</b> (green), <b>PYR</b> (orange).<br>This is the same type of plot as Fig 2B in Ponzi et al. (2023).</p>')

        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"

        self.output = ipywidgets.Output()
        self.children = [self._title_widget, self._sub_title_widget, self.output]

    def plot(self, runs: dict) -> None:
        self._title_widget.layout.display = ""
        self._sub_title_widget.layout.display = ""

        self.output.clear_output()
        with self.output:

            # Plot raster for each loaded run
            for label, run in runs.items():
                cfg = run['simConfig']
                starttime = cfg.get('starttime', 300)

                fig, ax = plt.subplots(figsize=(14, 5))

                for pop_name in ['PYR_pop', 'PVBC_pop', 'OLM_pop']:
                    t, ids = get_pop_spikes(run, pop_name)
                    ax.scatter(t / 1000, ids, s=0.5, c=POP_COLORS[pop_name],
                            label=POP_LABELS[pop_name], rasterized=True)

                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Cell index')
                ax.set_title(f'Raster plot — {label}')
                ax.legend(loc='upper right', markerscale=10)
                ax.set_xlim(starttime / 1000, cfg['duration'] / 1000)
                plt.tight_layout()
                display(fig)
                plt.close(fig)

    def clear(self) -> None:
        self.output.clear_output()
        self._title_widget.layout.display = "none"
        self._sub_title_widget.layout.display = "none"
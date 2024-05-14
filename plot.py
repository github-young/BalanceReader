# LICENSE: MIT <yxucn@connect.ust.hk>

import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as pl
import pandas as pd
from matplotlib.font_manager import FontProperties

# pl.style.use('ieee')
pl.rcParams.update(
    {
        "legend.fancybox": False,
        "legend.frameon": False,
        "font.serif": ["Times New Roman"],
        "font.family": "serif",
        "font.size": 15,
        "text.usetex": False,
        "pgf.texsystem": "xelatex",
        "pgf.preamble": "\n".join(
            [  # plots will use this preamble
                r"\usepackage[utf8]{inputenc}",
                r"\usepackage[T1]{fontenc}",
                r"\usepackage{siunitx}",
                r"\usepackage{amsmath}",
            ]
        ),
    }
)

## UNITS (g-s-m) --- DO NOT CHANGE THEM!
g = 1
kg = 1000 * g
s = 1
minute = 60
hour = 3600 * s
mass = 1
cm = 0.01
mm = 0.001


def get_CSV_filepath_rel(WDIR):
    filepath_list = []
    for root, dirs, files in os.walk(os.path.relpath(WDIR)):
        for file in files:
            if file.endswith(".csv"):
                filepath_list += [os.path.join(root, file)]
    return sorted(filepath_list)


def load_data(filename, start_from=2):
    df = pd.DataFrame(pd.read_csv(filename, sep=","))
    dropped_index = start_from
    seconds = df.iloc[dropped_index:, 0].values
    grams = df.iloc[dropped_index:, 1].values
    return seconds, grams - max(grams)


def apply_calc_window(data_len, window_len, window_start, offset_len=1):
    window_start = window_start % data_len
    if window_start >= data_len - window_len:
        # print(f"[!] Offset {offset_len} applied")
        window_start = data_len - window_len - offset_len
    return int(window_start)


def calc_eta(
    t,
    mass,
    window_len=5 * minute,
    window_start=0,
    area=(5 * cm) ** 2,
    offset=30 * s,
):
    t_step = t[1] - t[0]
    index_start_raw = int(window_start % t[-1] / t_step)
    index_start = apply_calc_window(
        len(t),
        window_len=window_len / t_step,
        window_start=index_start_raw,
        offset_len=int(offset / t_step),
    )
    index_end = index_start + int(window_len / t_step)
    mass_loss_in_window = mass[index_start] - mass[index_end]  # in gram
    eta_gsm = mass_loss_in_window / window_len / area  # in g / s / m2
    eta = eta_gsm * hour
    return eta, index_start, index_end


def plot_core(filename, t, mass, eta, window_start_index, window_end_index, fig, ax):
    label_str = r"%s; $\eta$ = %.1f g$\cdot$h$^{-1}$$\cdot$m$^{-2}$" % (
        Path(os.path.basename(filename)).stem,
        eta,
    )
    # label_str += r"$\unit{g.m^{-2}.h^{-1}}$"
    ax.plot(
        t,
        mass,
        "o",
        ls="-",
        markevery=[window_start_index, window_end_index],
        label=label_str,
    )
    return 0


def plot_shell(
    filename_list,
    t_list,
    mass_list,
    eta_list,
    window_start_index_list,
    window_end_index_list,
):
    fig, ax = pl.subplots(figsize=[12, 9])
    # plot single or multiple lines
    for filename, t, mass, eta, window_start_index, window_end_index in zip(
        filename_list,
        t_list,
        mass_list,
        eta_list,
        window_start_index_list,
        window_end_index_list,
    ):
        plot_core(filename, t, mass, eta, window_start_index, window_end_index, fig, ax)
    # plot single or multiple lines
    fontsize_small = 18
    fontsize_large = 24
    pl.ticklabel_format(useOffset=False)
    pl.xticks(np.arange(0, t[-1] + 60, 600), fontsize=fontsize_small)
    pl.yticks(fontsize=fontsize_small)
    pl.xlabel("Time / s", fontsize=fontsize_large)
    pl.ylabel("Mass change / g", fontsize=fontsize_large)
    pl.legend(fontsize=fontsize_small)
    title_str = f"CuO/AA-Cellulose-AA hydrogel/Al; time step = {t[1]-t[0]} s"
    pl.title(title_str, fontsize=fontsize_large)
    pl.savefig(f"{WDIR}/{WDIR}.png", dpi=144, bbox_inches="tight", backend="pgf")
    pl.close()
    return 0


def main_run(filepaths):
    print("[+] Plot:\n"+"\n".join(filepaths))
    t_list = []
    mass_list = []
    eta_list = []
    wsi_list = np.array([-5, -5, -14]) * minute
    window_start_index_list = []
    window_end_index_list = []
    for filename, wsi in zip(filepaths, wsi_list):
        t, mass = load_data(filename)
        t_list += [t]
        mass_list += [mass]
        eta, window_start_index, window_end_index = calc_eta(t, mass, window_start=wsi)
        eta_list += [eta]
        window_start_index_list += [window_start_index]
        window_end_index_list += [window_end_index]
    plot_shell(
        filepaths,
        t_list,
        mass_list,
        eta_list,
        window_start_index_list,
        window_end_index_list,
    )
    return 0


WDIR = os.path.relpath("./CuO")
filepaths = get_CSV_filepath_rel(WDIR)
main_run(filepaths[:-1])

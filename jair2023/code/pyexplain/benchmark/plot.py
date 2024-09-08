from pyexplain.benchmark.file_utils import cumulative_expl_time, cumulative_lits_derived_time
import numpy as np
import pandas as pd
import math
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['font.weight'] = 'bold'

# all functions for plotting the data


def cactus_plot(df):
    plt.figure(figsize=(20, 12))
    for i, row in df.iterrows():
        x, y, label = row["cumul_explain_step"], row["cumul_explain_time"], row["params_explanation_computer"]
        plt.plot(x, y, label=label.replace('_', '-'), linewidth=3)

    plt.legend(loc="upper left", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel("Cumulative $\#$ of explanations", fontsize=28)
    plt.ylabel("Time [s]", fontsize=28)
    plt.title("Log-scaled cumulative explanation-time", fontsize=28)
    plt.grid(True)
    plt.show()


def cactus_plot_derived_lits(df):
    plt.figure(figsize=(20, 12))
    for i, row in df.iterrows():
        x, y, label = row["cumul_explain_step"], row["cumul_explain_time"], row["params_explanation_computer"]
        plt.plot(x, y, label=label.replace('_', '-'), linewidth=3)
    plt.legend(loc="upper left", fontsize=20)
    #plt.xscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel("Cumulative $\#$ of literals", fontsize=28)
    plt.ylabel("Time [s]", fontsize=28)
    plt.title("Log-scaled cumulative derived literals time", fontsize=28)
    plt.grid(True)
    #plt.savefig("/home/emilio/research/OCUSExplain/code/pyexplain/benchmark/cactus_derived_lits" +datetime.now().strftime("%Y%m%d%H%M%S%f")+".png")
    plt.show()


def round_down(n, z):
    decimals = -1
    multiplier = 10 ** decimals
    return round(math.floor(n * multiplier) / multiplier)


def round_50(n, i=50):
    rounded = (n // i) * i
    return rounded


def heat_map_costs(ousCosts, musCosts, figure_path=None):
    COEFF_THICK = 1
    x, y, s = [], [], []
    d = {}

    for k in ousCosts:

        assert len(ousCosts[k]) == len(musCosts[k])

        for xi, yi in zip(ousCosts[k], musCosts[k]):

            if (xi, yi) in d:
                d[(xi, yi)] += COEFF_THICK
            else:
                d[(xi, yi)] = COEFF_THICK

    for ((xi, yi), si) in d.items():
        x.append(xi)
        y.append(yi)
        s.append(si)

    _, _ = plt.subplots(figsize=(5, 5))
    plt.scatter(x, y, s=s, marker='+')
    plt.xlabel('OUS Explanation cost', fontsize=22)
    plt.ylabel('MUS Explanation cost', fontsize=22)

    if figure_path:
        plt.savefig(figure_path, bbox_inches='tight')

    plt.show()


def heatMapCosts(ousCosts, musCosts, coeff_thick=1, figure_path=None):
    x = []
    y = []
    for k in ousCosts:
        x1 = ousCosts[k]
        y1 = musCosts[k]
        assert len(x1) == len(y1)
        x += x1
        y += y1

        d = {}
        for xi, yi in zip(x, y):
            if (xi, yi) in d:
                d[(xi, yi)] += coeff_thick
            else:
                d[(xi, yi)] = coeff_thick

        rounding = round_50
        num = 30
        xmin, xmax = min(x+y), max(x+y)
        all_vals = list(range(rounding(xmin, num),
                        rounding(xmax+num, num), num))

        all_vals.sort()
        all_valsreversed = list(all_vals)
        all_valsreversed.sort(reverse=True)

        matx = [[0] * len(all_vals) for i in all_vals]

        for ((xi, yi), si) in d.items():

            xpos = all_vals.index(rounding(xi, num))
            ypos = all_valsreversed.index(rounding(yi, num))
            matx[ypos][xpos] = si

        fig, ax = plt.subplots(figsize=(5, 5))
        im = ax.imshow(matx, cmap='Greys', interpolation='nearest')

        # We want to show all ticks...
        ax.set_xticks(np.arange(len(all_vals)))
        ax.set_yticks(np.arange(len(all_vals)))
        # ... and label them with the respective list entries.
        xticksLabels = [str(val) if idx %
                        2 == 0 else "" for idx, val in enumerate(all_vals)]
        ax.set_xticklabels(xticksLabels, fontsize=16)
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        yticksLabels = list(xticksLabels)
        yticksLabels.reverse()
        ax.set_yticklabels(yticksLabels, fontsize=16)

        ax.plot(np.arange(len(all_vals)), range(
            len(all_vals)-1, -1, -1), linestyle='--')
        fig.tight_layout()
        # plt.xlim((0, 50))d
        plt.xlabel('OUS Explanation cost', fontsize=22)
        plt.ylabel('MUS Explanation cost', fontsize=22)
        vals = [60, 120, 200, 260, 380]
        valsreversed = [60, 120, 200, 260, 380]
        valsreversed.reverse()
        if figure_path:
            plt.savefig(figure_path, bbox_inches='tight')
        plt.show()


def plot_derived_lits_avg_time(d_vals, figure_path=None, figsize=(16, 8), mapping=None,  no_legend=False, with_line=None, xlog=False, ylog=False,ylim=None, xlimit=None, ordering=None, next_to_graph=False, loc=None):
    #
    ordered_d_vals = list(d_vals.keys())

    if ordering:
        ordered_d_vals = ordering


    plt.figure(figsize=figsize)
    if with_line:
        plt.plot(list(range(0, 251, 1)), [
                 with_line]*251, linewidth=1, ls=('dashed'),color='black', label='Timeout')
    for config in ordered_d_vals:
        if config not in d_vals:
            continue
        timings = d_vals[config]
        x = timings["x"]
        y = timings["y"]
        max_id = len(x)

        label = config.replace('_', '-')

        if mapping and config in mapping:
            label = mapping[config]

        if label in ["MUS"]:
            plt.plot(x[:max_id], y[:max_id], label=label if not no_legend else None, 
                     linewidth=3, linestyle="--")
            continue

        plt.plot(x[:max_id], y[:max_id], linewidth=3,
                 label=label if not no_legend else None, 
                 )

    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    if xlog:
        plt.xscale('log')
    
    if ylog:
        plt.yscale('log')
    if xlimit:
        plt.xlim(xlimit)

    if ylim:
         plt.ylim(ylim)

    if next_to_graph:
        plt.legend(fontsize=20, loc='center left', bbox_to_anchor=(1.0, 0.55))
    elif loc:
        plt.legend(loc=loc, fontsize=20)
    elif not no_legend:
        plt.legend(loc="upper left", fontsize=20)
    else:
        plt.legend('', frameon=False)

    if not no_legend:
        plt.xlabel("Number of literals derived", fontsize=32)
        plt.ylabel("Avg. cumulative expl time [s]", fontsize=32)

    if figure_path:
        print("saving to path=", figure_path)
        plt.savefig(figure_path, bbox_inches='tight')

    plt.show()


def cactus_cumulative_lits_derived_time(df, column_name="params_explanation_config", figure_path=None, xlog=True, ylog=False, figsize=(16, 8), mapping=None, ordering=None, next_to_graph=False):
    plt.figure(figsize=figsize)

    all_column_values = set(df[column_name])

    x = []
    y = []
    max_y = []
    label = []

    if ordering:
        ordering_column_Values = ordering
    else:
        ordering_column_Values = all_column_values

    for id, column_value in enumerate(ordering_column_Values):
        xi, yi = cumulative_lits_derived_time(
            df[df[column_name] == column_value])
        x.append(xi)
        y.append(yi)
        if mapping:
            label.append(mapping[column_value])
        else:
            label.append(column_value)

        if int(max(yi)) < 7200:
            max_y.append((id, max(yi)))
        else:
            max_y.append((id, max(yi) + 10000 - max(xi)))

    if not ordering:
        max_y.sort(key=lambda xs: xs[1])

    for id, _ in max_y:
        plt.plot(x[id], y[id], label=label[id], linewidth=4)

    if next_to_graph:
        plt.legend(fontsize=20, loc='center left', bbox_to_anchor=(1.0, 0.5))
    else:
        plt.legend(loc="upper left", fontsize=20)

    if xlog:
        plt.xscale('log')
    
    if ylog:
        plt.yscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel("Cumulative number of literals derived", fontsize=26)
    plt.ylabel("Time [s]", fontsize=24)
    plt.grid(True)
    if figure_path:
        plt.savefig(figure_path, bbox_inches='tight')
    plt.show()


def cactus_cumulative_expl_time(df, column_name="params_explanation_config", figure_path=None, xlog=True, figsize=(16, 8), mapping=None, ordering=None, next_to_graph=False):
    plt.figure(figsize=figsize)

    all_column_values = set(df[column_name])
    x = []
    y = []
    max_y = []
    label = []

    if ordering:
        ordering_column_Values = ordering
    else:
        ordering_column_Values = all_column_values

    for id, column_value in enumerate(ordering_column_Values):
        xi, yi = cumulative_expl_time(df[df[column_name] == column_value])
        x.append(xi)
        y.append(yi)
        if mapping:
            label.append(mapping[column_value])
        else:
            label.append(column_value)

        if int(max(yi)) < 7200:
            max_y.append((id, max(yi)))
        else:
            max_y.append((id, max(yi) + 10000 - max(xi)))
    if not ordering:
        max_y.sort(key=lambda xs: xs[1])

    for id, my in max_y:
        plt.plot(x[id], y[id], label=label[id], linewidth=4)

    if next_to_graph:
        plt.legend(fontsize=20, loc='center left', bbox_to_anchor=(1.0, 0.5))
    else:
        plt.legend(loc="upper left", fontsize=20)

    if xlog:
        plt.xscale('log')
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.xlabel("Cumulative number of Explanation steps", fontsize=28)
    plt.ylabel("Time [s]", fontsize=28)
    # plt.title("Cumulative explanation-time",fontsize=28)
    plt.grid(True)
    if figure_path:
        plt.savefig(figure_path, bbox_inches='tight')
    plt.show()


def summarize_cumalitve_lits_derived_time(df_rq, column_name, ignored):
    # dict with cumulative times
    d_cumul_avg_time_incr = {
        config: {"x": None, "y": None} for config in set(df_rq[column_name]) if config not in ignored
    }

    for config in set(df_rq[column_name]):
        if config in ignored:
            continue
        t_ordered = []
        # make it 1 graph
        for _, row in df_rq[df_rq[column_name] == config].iterrows():
            t_ordered += row["average_lits_derived_time"]
        t_ordered.sort(key=lambda l: l[0])

        d_ordered = defaultdict(float)
        d_n_ordered = defaultdict(int)
        for step, ti in t_ordered:
            d_ordered[step] += ti
            d_n_ordered[step] += 1

        for step in d_ordered:
            d_ordered[step] /= d_n_ordered[step]
        x = []
        y = []
        for step in sorted(d_ordered):
            x.append(step)
            y.append(d_ordered[step])

        d_cumul_avg_time_incr[config] = {"x": x, "y": y}
    ordering = [config for config in sorted(
        d_cumul_avg_time_incr, key=lambda config: d_cumul_avg_time_incr[config]["y"][-1])]
    ordering.reverse()

    return d_cumul_avg_time_incr, ordering

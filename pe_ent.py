#!/usr/bin/python

# Generate these graphs

## Pie chart of the size of the sections
# Line graph like kev has
# Heat map of sections of the pe file - looking for ent

import lief

from plotly.offline import download_plotlyjs, plot
import plotly.graph_objs as go
from plotly.graph_objs import *

from plotly import tools
from collections import Counter
import numpy as np
from math import log, e

## Helper functions
def entropy(labels, base=None):
    value,counts = np.unique(labels, return_counts=True)
    norm_counts = counts / counts.sum()
    base = e if base is None else base
    return -(norm_counts * np.log(norm_counts)/np.log(base)).sum()



## Section size bar chart
def section_size_bar(pebin, filename):

    section_size_bar_raw = go.Bar(
        name='Raw size',
        x=[section.name for section in pebin.sections],
        y=[section.size for section in pebin.sections]
    )

    section_size_bar_virtual = go.Bar(
        name='Virtual size',
        x=[section.name for section in pebin.sections],
        y=[section.virtual_size for section in pebin.sections]
    )

    data = [section_size_bar_raw, section_size_bar_virtual]

    layout = go.Layout(
        barmode='stack',
        title='Raw/virtual section sizes: {}'.format(filename),
        xaxis=dict(
            title='Sections',
            zeroline=False
        ),
        yaxis=dict(
            title='Size',
            ticklen=5,
            nticks=10,
            zeroline=False,
            type='log',
            autorange=True
        )
    )

    return data, layout

## Occurance per byte
def section_byte_occurance_heatmap(pebin, filename):
    z = []
    y = []
    for section in pebin.sections:
        row = []
        c = Counter(section.content)
        for i in range(0, 256):
            row.append(c[i])
        z.append(row)
        y.append(section.name)

    data = go.Heatmap(
        x=['x{:02}'.format(d) for d in range(0, 256)],
        y=y,
        z=z,
        colorscale='Viridis',
    )

    layout = go.Layout(
        title='Byte frequency: {}'.format(filename),
        xaxis=dict(
            title='Byte: x0 to xFF',
            ticktext=['x{:02}'.format(d) for d in range(0, 256, 5)],
            tickvals=list(range(0, 256, 5)),
            tickangle=45,
        ),
        yaxis=dict(
            title='Binary section',
            ticktext=[ s.name for s in pebin.sections ],
            tickvals=[ s.name for s in pebin.sections ]
        )
    )

    return [data], layout

## Ent per section
def section_ent_line(pebin, filename, block_size=200, smooth=True):

    data = []
    for section in pebin.sections:

        # This gets the content block amounts and rounds up - so we always get 1 more than required
        block_len = -(-len(section.content) // block_size)

        shannon_samples = []

        i = 1
        prev_end = 0
        while prev_end <= len(section.content):

            block_start = prev_end
            block_end = i * block_len

            ent = entropy(section.content[ block_start : block_end ])
            shannon_samples.append(ent)

            prev_end = block_end+1
            i += 1

        data.append(go.Scatter(
            x=list(range(block_size)),
            y=shannon_samples,
            name = section.name,
            line=dict(shape=('spline' if smooth else 'line'))
        ))


    layout = go.Layout(
        xaxis=dict(
            showgrid = False,
            range = (0, block_size)

        ),
        yaxis=dict(
            range = (0,9),
            zeroline=True
        ),
    )


    return data, layout


if __name__ == '__main__':

    # filename='bins/aa14c8e777-cape'
    filename='bins/test.exe'
    # filename='bins/Locky.bin.mal'
    filename='bins/Shamoon.bin.mal'
    # filename='bins/Win32.Sofacy.A.bin.mal'

    pebin = lief.PE.parse(filename=filename)

    data, layout = section_ent_line(pebin, filename=filename)

    graph = go.Figure(data=data, layout=layout)
    plot(graph, filename='graph.html')


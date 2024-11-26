from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.objects.indicators import BaseIndicator

import plotly.graph_objects as plot
from plotly.subplots import make_subplots as subplot

import numpy as np


class PlotterGrid:

    @staticmethod
    def __init_plot_grid(rows, cols):
        plot_grid = []
        for i in range(rows):
            plot_grid.append([])
            for j in range(cols):
                plot_grid[i].append(None)
        return plot_grid

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.plots = self.__init_plot_grid(rows, cols)
        self.plots[0][0] = 'candles'
        self.indicator_index = {}

    def assign_indicator(self, indicator, mode='auto'):
        if mode == 'auto':
            if indicator.is_subplot:
                for i in range(len(self.plots)):
                    row = self.plots[i]
                    for j in range(len(row)):
                        if row[j] is None and indicator.indicator_id not in self.indicator_index.keys():
                            self.plots[i][j] = indicator.indicator_id
                            self.indicator_index[indicator.indicator_id] = f'{i+1},{j+1}'
            else:
                self.indicator_index[indicator.indicator_id] = '1,1'

    def get_subplot_index(self, indicator_id):
        return self.indicator_index[indicator_id]


class RenderEngine:

    @staticmethod
    def __calculate_view_height(num_subplots):
        if num_subplots == 0:
            return [1]
        return [0.8] + [(1-0.8)/num_subplots] * num_subplots

    def __generate_trace(self, trace_data):
        if isinstance(trace_data, CandleCluster):
            pass
        elif isinstance(trace_data, BaseIndicator):
            if trace_data.is_subplot:
                self.num_subplots += 1

    def render_chart(self):
        plotter_grid = PlotterGrid(len(self.indicators), 1)
        self.fig = subplot(
            rows=self.num_subplots + 1,
            cols=1,
            shared_xaxes=True,
            row_heights=self.__calculate_view_height(self.num_subplots)
        )
        window_df = self.window.to_dataframe()
        self.fig.add_trace(
            plot.Candlestick(
                x=window_df['time'],
                open=window_df['open'],
                high=window_df['high'],
                low=window_df['low'],
                close=window_df['close'],
                name='candles'
            ),
            row=1,
            col=1
        )
        for indicator in self.indicators.values():
            plotter_grid.assign_indicator(indicator)
            for i in range(indicator.y_count):
                if indicator.y_count == 1:
                    y_str = 'y'
                elif indicator.y_count > 1:
                    y_str = f'y{i+1}'
                row,col = plotter_grid.get_subplot_index(indicator.indicator_id).split(',')
                if hasattr(indicator, 'histogram') and f'y{i+1}' == indicator.histogram:
                    self.fig.add_trace(
                        plot.Bar(
                            x=indicator.data['x'],
                            y=indicator.data[y_str],
                            name=indicator.indicator_id,
                            marker_color=indicator.colors[y_str]
                        ),
                        row=(int(row)),
                        col=(int(col)),
                    )
                else:
                    self.fig.add_trace(
                        plot.Scatter(
                            x=indicator.data['x'],
                            y=indicator.data[y_str],
                            name=indicator.indicator_id,
                            mode='lines',
                            line=dict(color=indicator.colors[y_str])
                        ),
                        row=(int(row)),
                        col=(int(col)),
                    )
        for signal in self.signals:
            signal_data = signal.generate_signals_for_candle_cluster(self.window)
            for point_x, point_y in zip(signal_data['x'], signal_data['y']):
                if point_y == 1:
                    self.fig.add_vline(x=point_x, line_color="green")
                if point_y == 2:
                    self.fig.add_vline(x=point_x, line_width=3, line_dash="dash", line_color="green")
                if point_y == 3:
                    self.fig.add_vline(x=point_x, line_color="red")
                if point_y == 4:
                    self.fig.add_vline(x=point_x, line_width=3, line_dash="dash", line_color="red")
        self.fig.update_layout(
            xaxis_rangeslider_visible=False,
            yaxis={'fixedrange': False},
            title={'text': f'{self.window.instrument} {self.window.gran}'}
        )
        self.fig.show()



    def __init__(self, window: CandleCluster):
        self.window = window
        self.indicators = {}
        self.traces = []
        self.signals = []   # Signals are vertical lines
        self.fig = None
        self.ax = None
        self.num_subplots = 0
        self.auto_scale = True
        self.chart_type = 'candlestick'


    def add_indicator(self, indicator, label=None):
        label = label or indicator.indicator_id
        if indicator.is_subplot:
            self.num_subplots += 1
        if label in self.indicators.keys():
            diff_label = f'{label}_{len(self.indicators.keys())}'
            self.indicators[diff_label] = indicator
            self.indicators[diff_label].update(self.window)
        else:
            self.indicators[label] = indicator
            self.indicators[label].update(self.window)

    def add_signal(self, signal, label=None):
        self.signals.append(signal)

    def set_chart_type(self, chart_type):
        if chart_type not in ['candlestick', 'ohlc']:
            raise ValueError('Invalid chart type, must be either candlestick or ohlc')
        self.chart_type = chart_type



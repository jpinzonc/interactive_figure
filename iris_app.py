from flask import Flask, render_template, request
import pandas as pd
#from bokeh.charts import Histogram
from bokeh.embed import components
import numpy as np
app = Flask(__name__)
from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application


# Load the Iris Data Set
from sklearn import datasets
iris = datasets.load_iris()
X = iris.data
y = iris.target
iris_df = pd.DataFrame(X)
iris_df.loc[:,'Species'] = y
iris_df.columns = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Species"]

#iris_df = pd.read_csv("data/iris.data",
#    names=["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Species"])
feature_names = iris_df.columns[0:-1].values.tolist()
def make_dataset(df, feature, range_start = -60, range_end = 120, bin_width = 5):
    Species = df.Species.unique()
    by_carrier = pd.DataFrame(columns=['proportion', 'left', 'right',
                                       'f_proportion', 'f_interval',
                                       'name', 'color'])
    range_extent = range_end - range_start

    # Iterate through all the carriers
    for i, Species in enumerate(Species):

        # Subset to the carrier
        subset = iris_df[iris_df['Species'] == Species]

        # Create a histogram with 5 minute bins
        arr_hist, edges = np.histogram(subset[feature],
                                       bins = int(range_extent / bin_width),
                                       range = [range_start, range_end])

        # Divide the counts by the total to get a proportion
        arr_df = pd.DataFrame({'proportion': arr_hist / np.sum(arr_hist), 'left': edges[:-1], 'right': edges[1:] })

        # Format the proportion
        arr_df['f_proportion'] = ['%0.5f' % proportion for proportion in arr_df['proportion']]

        # Format the interval
        arr_df['f_interval'] = ['%d to %d minutes' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]

        # Assign the carrier for labels
        arr_df['name'] = Species

        # Color each carrier differently
        #arr_df['color'] = Category20_16[i]

        # Add to the overall dataframe
        by_carrier = by_carrier.append(arr_df)

    # Overall dataframe
    by_carrier = by_carrier.sort_values(['name', 'left'])

    return ColumnDataSource(by_carrier)

def make_plot(src):
    # Blank plot with correct labels
    p = figure(plot_width = 700, plot_height = 700,
        title = 'Histogram of Iris',
        x_axis_label = 'Length (mm)', y_axis_label = 'Proportion')
    # Quad glyphs to create a histogram
    p.quad(source = src, bottom = 0, top = 'proportion', left = 'left', right = 'right',
        color = 'color', fill_alpha = 0.7, hover_fill_color = 'color', legend = 'name',
        hover_fill_alpha = 1.0, line_color = 'black')
    # Hover tool with vline mode
    hover = HoverTool(tooltips=[('Carrier', '@name'),
            ('Delay', '@f_interval'),
            ('Proportion', '@f_proportion')],
                mode='vline')
    p.add_tools(hover)
    # Styling
    #p = style(p)
    return p

# Create the main plot
def create_figure(df, current_feature_name):
    p = make_plot(make_dataset(df, current_feature_name))
    return p

# Index page
@app.route('/')
def index():
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "Sepal Length"

	# Create the plot
	plot = create_figure(iris_df, current_feature_name)

	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("iris_index1.html", script=script, div=div,
		feature_names=feature_names,  current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)

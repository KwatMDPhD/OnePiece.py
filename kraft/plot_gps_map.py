from numpy import asarray, isnan, nan, unique
from plotly.colors import make_colorscale

from .COLORBAR import COLORBAR
from .DATA_TYPE_COLORSCALE import DATA_TYPE_COLORSCALE
from .get_colorscale_color import get_colorscale_color
from .get_element_x_dimension_triangulation_edges import (
    get_element_x_dimension_triangulation_edges,
)
from .merge_2_dicts_recursively import merge_2_dicts_recursively
from .plot_plotly_figure import plot_plotly_figure


def plot_gps_map(
    nodes,
    node_name,
    node_x_dimension,
    elements,
    element_name,
    element_x_dimension,
    dimension_grid=None,
    element_label=None,
    grid_probability=None,
    grid_label=None,
    label_colorscale=DATA_TYPE_COLORSCALE["categorical"],
    element_value=None,
    element_value_data_type="continuous",
    layout=None,
    element_value_binary_annotation=None,
    html_file_path=None,
    node_marker_size=30,
    node_marker_color="#2e211b",
    node_line_color="#23191e",
    node_text_annotation=None,
    element_marker_size=20,
    element_marker_color="#ebf6f7",
    element_marker_line_width=1,
    element_marker_line_color="#2e211b",
    n_contour=20,
    grid_label_opacity=0.7,
):

    layout_axis = {"showgrid": False, "zeroline": False, "showticklabels": False}

    title_text = "{} {}<br>{} {}".format(
        len(nodes), node_name, len(elements), element_name
    )

    if element_value is not None:

        title_text += "<br>{}".format(element_value.name)

    layout_template = {
        "height": 1000,
        "width": 1000,
        "title": {"x": 0.5, "text": "<b>{}</b>".format(title_text)},
        "xaxis": layout_axis,
        "yaxis": layout_axis,
        "annotations": [],
    }

    if layout is None:

        layout = layout_template

    else:

        layout = merge_2_dicts_recursively(layout_template, layout)

    edge_xs, edge_ys = get_element_x_dimension_triangulation_edges(node_x_dimension)

    node_trace = {"type": "scatter", "legendgroup": node_name}

    data = [
        {
            **node_trace,
            "showlegend": False,
            "x": edge_xs,
            "y": edge_ys,
            "line": {"color": node_line_color},
        },
        {
            **node_trace,
            "name": node_name,
            "x": node_x_dimension[:, 0],
            "y": node_x_dimension[:, 1],
            "text": nodes,
            "mode": "markers",
            "marker": {"size": node_marker_size, "color": node_marker_color},
            "hoverinfo": "text",
        },
    ]

    node_text_annotation_template = {
        "font": {"size": 15, "color": "#171412"},
        "borderpad": 2,
        "bgcolor": "#ffffff",
        "bordercolor": "#171412",
        "showarrow": False,
    }

    if node_text_annotation is None:

        node_text_annotation = node_text_annotation_template

    else:

        node_text_annotation = merge_2_dicts_recursively(
            node_text_annotation_template, node_text_annotation
        )

    layout["annotations"] += [
        {
            "x": node_x_dimension[i, 0],
            "y": node_x_dimension[i, 1],
            "text": "<b>{}</b>".format(node),
            **node_text_annotation,
        }
        for i, node in enumerate(nodes)
    ]

    element_trace = {
        "type": "scatter",
        "name": element_name,
        "mode": "markers",
        "marker": {
            "size": element_marker_size,
            "color": element_marker_color,
            "line": {
                "width": element_marker_line_width,
                "color": element_marker_line_color,
            },
        },
        "hoverinfo": "text",
    }

    if grid_label is not None:

        grid_label_not_nan_unique = unique(grid_label[~isnan(grid_label)])

        label_color = {
            label: get_colorscale_color(
                label_colorscale, label, grid_label_not_nan_unique.size
            )
            for label in grid_label_not_nan_unique
        }

        data.append(
            {
                "type": "contour",
                "showlegend": False,
                "x": dimension_grid,
                "y": dimension_grid,
                "z": grid_probability[::-1],
                "autocontour": False,
                "ncontours": n_contour,
                "contours": {"coloring": "none"},
            }
        )

        for label in grid_label_not_nan_unique:

            z = grid_probability.copy()

            z[grid_label != label] = nan

            data.append(
                {
                    "type": "heatmap",
                    "x": dimension_grid,
                    "y": dimension_grid,
                    "z": z[::-1],
                    "colorscale": make_colorscale(
                        ("rgb(255, 255, 255)", label_color[label])
                    ),
                    "opacity": grid_label_opacity,
                    "showscale": False,
                    "hoverinfo": "none",
                }
            )

    if element_value is not None:

        element_value = element_value.reindex(index=elements)

        element_value = element_value[element_value.abs().sort_values().index]

        element_x_dimension_ = element_x_dimension[
            [elements.index(element) for element in element_value.index]
        ]

        if element_value_data_type == "continuous":

            tickvals = element_value.describe()[
                ["min", "25%", "50%", "mean", "75%", "max"]
            ]

        else:

            tickvals = element_value.unique()

        data.append(
            merge_2_dicts_recursively(
                element_trace,
                {
                    "x": element_x_dimension_[:, 0],
                    "y": element_x_dimension_[:, 1],
                    "text": tuple(
                        "{}<br>{:.2f}".format(element, value)
                        for element, value in element_value.items()
                    ),
                    "marker": {
                        "color": element_value,
                        "colorscale": DATA_TYPE_COLORSCALE[element_value_data_type],
                        "colorbar": merge_2_dicts_recursively(
                            COLORBAR,
                            {
                                "tickmode": "array",
                                "tickvals": tickvals,
                                "ticktext": tuple(
                                    "{:.2e}".format(tickval) for tickval in (tickvals)
                                ),
                            },
                        ),
                    },
                },
            )
        )

        if (
            element_value_data_type == "binary"
            and element_value_binary_annotation is not None
        ):

            layout["annotations"] += [
                {
                    "x": element_x_dimension_[i, 0],
                    "y": element_x_dimension_[i, 1],
                    "text": "<b>{}</b>".format(element_value.index[i]),
                    "arrowhead": 2,
                    "arrowwidth": 2,
                    "arrowcolor": "#c93756",
                    "standoff": None,
                    "clicktoshow": "onoff",
                    **element_value_binary_annotation,
                }
                for i in element_value.values.nonzero()[0]
            ]

    elif element_label is not None:

        for label in grid_label_not_nan_unique:

            is_label = element_label == label

            data.append(
                merge_2_dicts_recursively(
                    element_trace,
                    {
                        "legendgroup": "Label {:.0f}".format(label),
                        "name": "Label {:.0f}".format(label),
                        "x": element_x_dimension[is_label, 0],
                        "y": element_x_dimension[is_label, 1],
                        "text": asarray(elements)[is_label],
                        "marker": {"color": label_color[label]},
                    },
                )
            )

    else:

        data.append(
            merge_2_dicts_recursively(
                element_trace,
                {
                    "x": element_x_dimension[:, 0],
                    "y": element_x_dimension[:, 1],
                    "text": elements,
                },
            )
        )

    plot_plotly_figure({"layout": layout, "data": data}, html_file_path)

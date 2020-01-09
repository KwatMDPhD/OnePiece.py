from numpy import apply_along_axis

from .compute_joint_probability import compute_joint_probability
from .get_dimension_resolutions import get_resolutions
from .plot_mesh_grid import plot_mesh_grid
from .unmesh import unmesh


def compute_posterior_probability(
    element_x_dimension,
    plot=True,
    names=None,
    **estimate_kernel_density_keyword_arguments,
):

    point_x_dimension, joint_probabilities = compute_joint_probability(
        element_x_dimension,
        plot=plot,
        names=names,
        **estimate_kernel_density_keyword_arguments,
    )

    target_dimension_resolution = get_resolutions(point_x_dimension)[-1]

    posterior_probabilities = apply_along_axis(
        lambda vector: vector / (vector.sum() * target_dimension_resolution),
        -1,
        unmesh(point_x_dimension, joint_probabilities)[1],
    ).reshape(joint_probabilities.shape)

    if plot:

        plot_mesh_grid(
            point_x_dimension,
            posterior_probabilities,
            names=names,
            value_name="Posterior Probability",
        )

    return point_x_dimension, posterior_probabilities
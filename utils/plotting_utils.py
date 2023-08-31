import matplotlib.pylab as plt
import matplotlib.animation as anim
import numpy as np
import networkx as nx
import os

def plot_RCC_Evidence(lags, *to_plot, **kwargs):
    """
    TODO: Add description

    Arguments
    ---------
    lags:
    *to_plot: (dicts) where the keys ["data", "error", "label", "color", "style", "linewidth"]
    """

    # Location of the maximum correlation
    if 'scale' in kwargs.keys():
        lags = lags * kwargs['scale'] # Repetition Time (TR)

    # Instantiate figure
    fig, ax = plt.subplots(figsize=(6,4))
    ax.remove()

    ##################
    left, bottom, width, height = [0.1, 0.12 , 0.85, 0.85]
    ax1 = fig.add_axes([left, bottom, width, height])
    # Plot main curves
    for curve in to_plot:    
        ax1.plot(lags, curve["data"], curve["linewidth"], color=curve["color"], linestyle=curve["style"], label=curve["label"], alpha=curve["alpha"])
        ax1.fill_between(lags, curve["data"]-curve["error"], curve["data"]+curve["error"],
            alpha=0.2, edgecolor=curve["color"], facecolor=curve["color"], linewidth=0        
        )
    # Plot significant times: It requires 
    if "significance_marks" in kwargs.keys():
        y_ini = -0.01
        for curve in kwargs["significance_marks"]:
            ax1.fill_between(curve["data"]*lags, y_ini, y_ini+0.02, alpha=0.8, facecolor=curve["color"], linewidth=0, label=curve["label"])
            y_ini += 0.02
    # Figures details
    z_min, z_max = kwargs["limits"]
    ax1.vlines(x=0, ymin=z_min, ymax=z_max, linewidth=0.3, color='grey', linestyles='--')
    ax1.hlines(y=0, xmin=lags[0], xmax=lags[-1], linewidth=0.3, color='grey', linestyles='--')
    ax1.spines["top"].set_visible(False), ax1.spines["right"].set_visible(False)
    ax1.set_ylabel(kwargs['y_label'], fontsize=15)
    ax1.set_yticks([z_min, 0.5*(z_min+z_max),z_max]), ax1.set_yticklabels([str(z_min), str(0.5*(z_min+z_max)), str(z_max)]), ax1.set_ylim([z_min-0.01,z_max+0.02])
    ax1.set_xlim([lags[0],lags[-1]]), ax1.set_xlabel(kwargs['x_label'], fontsize=15)
    # Legend
    plt.legend(fontsize=8, frameon=False, ncols=2)
    
    ###############
    # Visualization
    if 'save' in kwargs.keys():
        format = kwargs['save'].split(".")[-1]
        if 'dpi' in kwargs.keys():
            plt.savefig(kwargs['save'], dpi=kwargs['dpi'], format=format)
        else:
            plt.savefig(kwargs['save'], format=format)
    else:
        plt.show()
    plt.close()


def to_netwokx(matrices: np.ndarray):
    """
    Transforms numpy ndarrays into networkx graphs. It can operat on a sigle grpah as well as a list of grphs

    Parameters
    ----------
    matrices : np.ndarray
        The 2 or 3 dimensional array accordingly in case of a single graph or multiple graphs

    Returns
    -------
    List[nx.DiGraph]
        The list of nx graphs
    """

    if matrices.ndim == 2:
        matrices = np.expand_dims(matrices, axis=0)
    
    graphs = []
    for matrix in matrices:

        # Create the graph
        G = nx.DiGraph()

        # Add the nodes to the graph
        for i in range(len(matrix)):
            G.add_node(str(i))

        # Add the edges to the graph
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if not np.isclose(matrix[i][j], 0):
                    G.add_edge(str(i), str(j),weight=matrix[i][j])
        
        graphs.append(G)
    
    return graphs


def plot_ec_networks(effective_connectivity_networks, lags, animate=False, fps=5):
    """
    Visualizes the effective_connectivity_networks. It saves EC network for each time lag. It can also
    generate animation of the connectome evolution with the time lag increasing.

    Parameters
    ----------
    effective_connectivity_networks : List[nx.DiGraph]
        The list of EC networks sorted by the according lag value
    lags : Sequence
        The time lags corresponding to the EC networks
    animate : bool, optional
        The flag tells wether to animate, by default False
    fps : int, optional
        The fps speed of the animation, by default 5
    """

    def animate_and_save():

        # Animate process
        fig, ax = plt.subplots()
        fig.set_size_inches(5, 5)
        frames = []
        for img in net_images:

            frame = ax.imshow(img, animated=True)
            frame.axes.set_axis_off()
            frames.append([frame])

        # Save and display animation
        writervideo = anim.PillowWriter(fps=fps)
        ani = anim.ArtistAnimation(fig, frames, interval=50, blit=True, repeat_delay=1000)
        ani.save("tmp/ec_neetwork_evolution.gif", writer=writervideo)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    
    net_images = []
    for i, net in enumerate(effective_connectivity_networks):
        save_path = os.path.join("tmp", f"net_{i}.png")
        edges = net.edges()
        weights = [net[u][v]['weight'] for u, v in edges]
        nx.draw(net, with_labels=True, pos=nx.shell_layout(net), width=weights)
        plt.text(0.8, 0.9, f'{lags[i]}s', fontsize=15)
        plt.savefig(save_path)
        plt.clf()
        net_images.append(plt.imread(save_path))
    
    if animate:
        animate_and_save()


if __name__ == '__main__':

    path_to_npy = "Results29-08-2023_10-34/sub-0013_Length-100/Networks/sub-0013_Length-100_RCC.npy"
    ec_matrices: np.ndarray = np.load(path_to_npy)
    ec_networks = to_netwokx(ec_matrices)
    plot_ec_networks(ec_networks, np.arange(-5, 6, dtype=np.int32), animate=True, fps=2)

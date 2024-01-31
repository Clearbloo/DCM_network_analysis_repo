import os.path as osp
import argparse

import pandas as pd
import seaborn as sns
from constants import DATA_DIR, OUTPUT_DIR
from matplotlib import pyplot as plt

def main(save_output: bool=False):
    dataset_path = osp.join(DATA_DIR, "author_stats.csv")
    dataset = pd.read_csv(dataset_path)
    dataset = dataset.dropna()

    # remove irrelivant data from each author
    dataset = dataset.drop(
    [
        "id",
        "name_of_author",
        "institute",
        "country",
        "institute_ID",
        "citation_count",
        "average_citations",
        "total_papers",
        "paper_freq",
        "author_classification",
    ],
    axis=1,
)

    # sns.pairplot(dataset, y_vars=["h_index"], x_vars=["average_DCM_papers_of_coauthors", "connected_institutes", "connections", "second_order_connections", "average_h_index_of_coauthors"], diag_kind="kde", kind='reg')
    sns.pairplot(
    dataset,
    y_vars=["h_index"],
    x_vars=[
        "average_coauthors",
        "connected_institutes",
        "average_h_index_of_coauthors",
        "average_DCM_papers_of_coauthors",
    ],
)
    if save_output:
        plt.savefig(osp.join(OUTPUT_DIR, 'figs/variables_with_h.pdf'))
    plt.show()
    plt.close()

    h_indexes = dataset.h_index
    second_order_collaborations_per_first_order_collaboration = (
    dataset.second_order_connections / dataset.connections
)
    sns.scatterplot((second_order_collaborations_per_first_order_collaboration, h_indexes))
    plt.show()
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a quick graph")
    parser.add_argument('--save', '-s', action='store_true', help='Save the output figure')
    args = parser.parse_args()

    # Call the main function with the save_output argument
    main(save_output=args.save)
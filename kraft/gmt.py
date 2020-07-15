def read_gmt(gmt_file_path):

    gene_set_genes = {}

    with open(gmt_file_path) as io:

        for line in io.readlines():

            splits = line.split(sep="\t")

            gene_set_genes[splits[0]] = tuple(gene for gene in splits[2:] if gene != "")

    return gene_set_genes


def read_gmts(gmt_file_paths):

    gene_set_genes = {}

    for file_path in gmt_file_paths:

        gene_set_genes.update(read_gmt(file_path))

    return gene_set_genes
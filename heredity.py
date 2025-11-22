def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """
    probability = 1

    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]

        # Determine gene count for this person
        if person in two_genes:
            genes = 2
        elif person in one_gene:
            genes = 1
        else:
            genes = 0

        # Probability of having this number of genes
        if mother is None and father is None:
            # No parents: use unconditional probability
            gene_prob = PROBS["gene"][genes]

        else:
            # Person has parents: calculate from inheritance
            passing = {}

            for parent in [mother, father]:
                if parent in two_genes:
                    # Parent passes gene with 99%
                    passing[parent] = 1 - PROBS["mutation"]
                elif parent in one_gene:
                    # Parent passes gene with 50% (half/half), but mutation applies
                    passing[parent] = 0.5
                else:
                    # Parent passes gene only via mutation (1%)
                    passing[parent] = PROBS["mutation"]

            # Compute probability that THIS person has exactly `genes` copies
            if genes == 2:
                gene_prob = passing[mother] * passing[father]
            elif genes == 1:
                gene_prob = passing[mother] * (1 - passing[father]) + (1 - passing[mother]) * passing[father]
            else:  # genes == 0
                gene_prob = (1 - passing[mother]) * (1 - passing[father])

        # Probability of trait given gene count
        has_trait = person in have_trait
        trait_prob = PROBS["trait"][genes][has_trait]

        # Multiply into joint probability
        probability *= gene_prob * trait_prob

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add joint probability p to the correct gene and trait counts.
    """
    for person in probabilities:

        # Update gene distribution
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        elif person in one_gene:
            probabilities[person]["gene"][1] += p
        else:
            probabilities[person]["gene"][0] += p

        # Update trait distribution
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Normalize gene and trait distributions so they sum to 1.
    """
    for person in probabilities:

        # Normalize gene distribution
        total_gene = sum(probabilities[person]["gene"].values())
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] /= total_gene

        # Normalize trait distribution
        total_trait = sum(probabilities[person]["trait"].values())
        for t in probabilities[person]["trait"]:
            probabilities[person]["trait"][t] /= total_trait

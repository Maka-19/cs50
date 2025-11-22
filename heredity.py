#!/usr/bin/env python3
import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no copies of gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def load_data(filename):
    """
    Load gene information from a file into a dictionary.
    File format: name,mother,father,trait
    trait: 1 (True), 0 (False), blank for unknown.

    Returns a dict mapping names to dicts with keys:
      name, mother, father, trait (True/False/None)
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            mother = row["mother"].strip() if row["mother"] is not None else ""
            father = row["father"].strip() if row["father"] is not None else ""
            trait = row["trait"].strip() if row["trait"] is not None else ""

            if mother == "":
                mother_val = None
            else:
                mother_val = mother

            if father == "":
                father_val = None
            else:
                father_val = father

            if trait == "1":
                trait_val = True
            elif trait == "0":
                trait_val = False
            else:
                trait_val = None

            data[name] = {
                "name": name,
                "mother": mother_val,
                "father": father_val,
                "trait": trait_val
            }
    return data


def powerset(s):
    """
    Return list of all subsets of set s (as sets).
    """
    s = list(s)
    result = []
    for r in range(len(s) + 1):
        for combo in itertools.combinations(s, r):
            result.append(set(combo))
    return result


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return the joint probability.

    people: dict returned from load_data
    one_gene: set of names with exactly one copy
    two_genes: set of names with exactly two copies
    have_trait: set of names who exhibit trait
    """

    # Start with probability 1 and multiply in each person's probability
    probability = 1.0

    for person, info in people.items():
        mother = info.get("mother")
        father = info.get("father")

        # Treat empty string as None (defensive)
        if mother == "":
            mother = None
        if father == "":
            father = None

        # Determine number of genes for this person
        if person in two_genes:
            genes = 2
        elif person in one_gene:
            genes = 1
        else:
            genes = 0

        # If no parental information, use unconditional probability
        if mother is None and father is None:
            gene_prob = PROBS["gene"][genes]
        else:
            # compute probability parent passes gene
            def pass_prob(parent):
                # parent may not exist (shouldn't happen here), but defend
                if parent is None:
                    return PROBS["mutation"]
                if parent in two_genes:
                    # parent has two copies -> passes gene with prob 1 - mutation
                    return 1 - PROBS["mutation"]
                elif parent in one_gene:
                    # parent has one copy -> passes gene with prob 0.5
                    return 0.5
                else:
                    # parent has zero copies -> only passes gene by mutation
                    return PROBS["mutation"]

            p_m = pass_prob(mother)
            p_f = pass_prob(father)

            # Now compute probability that child has 'genes' copies
            if genes == 2:
                gene_prob = p_m * p_f
            elif genes == 1:
                gene_prob = p_m * (1 - p_f) + (1 - p_m) * p_f
            else:  # genes == 0
                gene_prob = (1 - p_m) * (1 - p_f)

        # Probability of trait given gene count
        has_trait = person in have_trait
        trait_prob = PROBS["trait"][genes][has_trait]

        # Multiply into joint probability
        probability *= gene_prob * trait_prob

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add joint probability p to the probabilities dictionary.

    probabilities structure:
      probabilities[person]["gene"][0/1/2] and probabilities[person]["trait"][True/False]
    """

    for person in probabilities:
        # gene
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        elif person in one_gene:
            probabilities[person]["gene"][1] += p
        else:
            probabilities[person]["gene"][0] += p

        # trait
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Normalize the probabilities such that each distribution sums to 1.
    """

    for person, dist in probabilities.items():
        # Normalize gene distribution
        total_gene = sum(dist["gene"].values())
        if total_gene == 0:
            # Defensive fallback: if zero, skip normalization to avoid division by zero,
            # but this indicates something went wrong upstream.
            raise ValueError(f"Total gene probability for {person} is zero; cannot normalize.")
        for g in dist["gene"]:
            dist["gene"][g] = dist["gene"][g] / total_gene

        # Normalize trait distribution
        total_trait = sum(dist["trait"].values())
        if total_trait == 0:
            raise ValueError(f"Total trait probability for {person} is zero; cannot normalize.")
        for t in dist["trait"]:
            dist["trait"][t] = dist["trait"][t] / total_trait


def main():

    # Check proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Set up probabilities dictionary
    probabilities = {
        person: {
            "gene": {0: 0.0, 1: 0.0, 2: 0.0},
            "trait": {True: 0.0, False: 0.0}
        }
        for person in people
    }

    names = set(people.keys())

    # Loop over all sets of people who might have the trait
    for have_trait in powerset(names):
        # Check against known information: if someone's trait is known but
        # this set disagrees, skip this set.
        violates_evidence = False
        for person in names:
            if people[person]["trait"] is not None:
                if people[person]["trait"] != (person in have_trait):
                    violates_evidence = True
                    break
        if violates_evidence:
            continue

        # Loop over all ways to choose who has one gene
        for one_gene in powerset(names):
            # Loop over all ways to choose who has two genes (disjoint from one_gene)
            for two_genes in powerset(names - one_gene):
                # Compute joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                # Update the probabilities dictionary
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Normalize
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value, prob in sorted(probabilities[person][field].items()):
                print(f"    {value}: {prob:.4f}")


if __name__ == "__main__":
    main()

import random

def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next.
    """

    num_pages = len(corpus)
    distribution = dict()

    # If the page has no outgoing links, treat it as linking to ALL pages
    if len(corpus[page]) == 0:
        for p in corpus:
            distribution[p] = 1 / num_pages
        return distribution

    # Otherwise:
    linked = corpus[page]
    num_links = len(linked)

    for p in corpus:
        distribution[p] = (1 - damping_factor) / num_pages

    # Add damping probability to linked pages
    for p in linked:
        distribution[p] += damping_factor / num_links

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling.
    """

    # Initialize counts for all pages
    counts = {page: 0 for page in corpus}

    # First sample: choose a page at random
    pages = list(corpus.keys())
    current_page = random.choice(pages)
    counts[current_page] += 1

    # Remaining samples
    for _ in range(1, n):
        model = transition_model(corpus, current_page, damping_factor)

        # Randomly choose next page based on probability distribution
        next_page = random.choices(
            population=list(model.keys()),
            weights=list(model.values()),
            k=1
        )[0]

        counts[next_page] += 1
        current_page = next_page

    # Convert counts into probabilities
    pageranks = {page: counts[page] / n for page in counts}
    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively applying the formula.
    """

    N = len(corpus)
    pagerank = {page: 1 / N for page in corpus}

    # Preprocess: treat pages with no links as linking to ALL pages
    fixed_corpus = dict()
    for page in corpus:
        if len(corpus[page]) == 0:
            fixed_corpus[page] = set(corpus.keys())
        else:
            fixed_corpus[page] = corpus[page]

    converged = False
    while not converged:
        new_ranks = dict()

        for page in pagerank:
            # Base probability from random jump
            rank = (1 - damping_factor) / N

            # Add contributions from all pages that link to this one
            total = 0
            for p in pagerank:
                if page in fixed_corpus[p]:
                    total += pagerank[p] / len(fixed_corpus[p])

            rank += damping_factor * total
            new_ranks[page] = rank

        # Check convergence (change <= 0.001)
        converged = all(
            abs(new_ranks[p] - pagerank[p]) <= 0.001
            for p in pagerank
        )

        pagerank = new_ranks

    # Normalize so they sum to exactly 1
    total = sum(pagerank.values())
    pagerank = {p: pagerank[p] / total for p in pagerank}

    return pagerank

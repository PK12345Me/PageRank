import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    num_pages = len(corpus)
    distribution = {}

    if corpus[page]:
        # With probability damping_factor, choose a link from the current page
        linked_pages = corpus[page]
        num_links = len(linked_pages)
        for link in linked_pages:
            distribution[link] = damping_factor / num_links

        # With probability 1 - damping_factor, choose any page at random
        for p in corpus:
            distribution[p] = distribution.get(p, 0) + (1 - damping_factor) / num_pages

    else:
        # If page has no outgoing links, treat it as linking to all pages including itself
        for p in corpus:
            distribution[p] = 1 / num_pages

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # pages = [key for key, value in corpus.items()]
    pages = list(corpus.keys())
    # print(pages)
    page = random.choice(pages)
    # page_rank_counts = {}
    page_rank_counts = {page: 0 for page in pages}

    for _ in range(n - 1):

        page_rank_counts[page] += 1

        # newDict goes here from transition_model
        DictOut = transition_model(corpus, page, damping_factor)

        keys = list(DictOut.keys())
        probabilities = list(DictOut.values())
        # print(keys,probabilities)

        page = random.choices(keys, probabilities)[0]
        # print("page ",page)

    page_ranks = {page: count / n for page, count in page_rank_counts.items()}
    # print(page_ranks)
    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    corpuslength = len(pages)
    page_rank_counts = {page: 1 / corpuslength for page in pages}
    converged = False

    while not converged:
        new_ranks = {}

        for page in pages:
            total = (1 - damping_factor) / corpuslength
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    total += damping_factor * (
                        page_rank_counts[possible_page] / len(corpus[possible_page])
                    )

                elif len(corpus[possible_page]) == 0:
                    total += damping_factor * (
                        page_rank_counts[possible_page] / corpuslength
                    )
            new_ranks[page] = total

        # Check for convergence
        converged = all(
            abs(new_ranks[page] - page_rank_counts[page]) < 0.001 for page in pages
        )
        page_rank_counts = new_ranks

        n = sum(page_rank_counts.values())
        page_rank_counts = {page: rank / n for page, rank in page_rank_counts.items()}

    return page_rank_counts


if __name__ == "__main__":
    main()

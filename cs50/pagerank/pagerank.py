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
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.

    """

    # Links avaiable given a current page
    links = corpus[page]
    n_links = len(links)

    # All Pages
    all_pages = list(corpus.keys())
    n_pages = len(all_pages)

    # If links are returned for current page
    if n_links > 0:

        transition_model = {}

        # Base Probability
        random_prob = (1-damping_factor)/n_pages

        # Probability for Linked Pages
        linked_prob = damping_factor/n_links

        for p in all_pages:
            if p in links:
                transition_model[p] = linked_prob + random_prob
            else:
                transition_model[p] = random_prob

    # If no links are returned
    else:
        # Equal probablity between all pages
        prob = 1/n_pages

        # Creating our transition model with all available page options
        transition_model = {key: prob for key in all_pages}

    return transition_model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Extract all page names from Corpus
    pages = list(corpus.keys())

    # Choose a random starting page
    page = random.choice(pages)

    # Initative counts dictionary with page names and their counts
    counts = {p: 0 for p in pages}
    counts[page] += 1  # Counting the starting page as visited

    for i in range(n-1):

        # Calcuate the transition model of the current page
        distribution = transition_model(corpus, page, damping_factor)

        # Choose the next page based on probabilities
        page = random.choices(
            population=list(distribution.keys()),
            weights=list(distribution.values())
        )[0]

        # Track the vist
        counts[page] += 1

    # Normalize results
    page_rank = {p: counts[p]/n for p in counts}

    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Extract all page names from Corpus and set n_pages variable
    pages = list(corpus.keys())
    n_pages = len(pages)

    # Starting probability of 1/N
    start_prob = 1/len(pages)

    # Initative page rank dictionary with all pages and set their starting probability 1/N
    page_rank = {p: start_prob for p in pages}

    while True:  # We will continue to iterate until convergence

        updated_ranks = {}  # Initatizing dictionary for updated ranks

        for p in pages:  # Looping through all pages in corpus

            # Calcualting their starting rank using below formula (provided by assignment instructions)
            base_rank = (1 - damping_factor) / n_pages
            sum = 0  # setting initial sum for calculating page rank to be modified in loop

            # Using this nested loop we are finding the number of linked pages for each page in our corpus
            for pi in pages:
                linked_pages = corpus[pi]  # Extracting linked pages for each page (pi)
                n_linked_pages = len(linked_pages)  # Counting the number of linked pages

                if linked_pages:
                    if p in linked_pages:  # Check if the page we're investigating is even included in our linked pages
                        # If yes, then we add the page rank for
                        sum = sum + (page_rank[pi] / n_linked_pages)
                else:
                    # If no linked pages then we treat it as if it links to every page uniformly
                    # we use n_pages over n_linked_pages because of the above assumption
                    sum = sum + (page_rank[pi] / n_pages)

            # We loop through all of the pages and continue adding the page
            # rank for a single particular page to all other pages
            # before finally setting the updated rank equal to the full sum of all the pages we can infer via corpus or assume via no linked pages assumption
            updated_ranks[p] = base_rank + damping_factor * sum

        converged = True
        convergence_threshold = 0.001  # Value set for later convergence testing

        # We then compare our newly found page ranks to those of the previous iteration
        for p in pages:
            # If the difference between the two sets is greater than 0.001 our threshold, we continue calcualting page rank
            if abs(updated_ranks[p] - page_rank[p] >= convergence_threshold):
                converged = False
                break

        # If the above loop finds the difference between the two values to be less than 0.001,
        # converged stays true and we exit the while loop
        if converged:
            break

        # Update page rank and repeat; if converged remains true after the threshold comparison this line of code will not execute
        # And ther previous iterations page_rank will be returned
        # Otherwise page_rank is set to the updated_rank and we continue iterating and until our PageRank values are no longer flucuating greater than the threshold
        page_rank = updated_ranks

    return page_rank


if __name__ == "__main__":

    main()

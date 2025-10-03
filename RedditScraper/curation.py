from typing import List, Tuple, Dict
import re


def _keyword_match(text: str, keywords: List[str]) -> List[str]:
    text_l = text.lower()
    hits = []
    for kw in keywords:
        if kw.lower() in text_l:
            hits.append(kw)
    return hits


def curate_sources(
    reddit,
    candidate_subreddits: List[str],
    candidate_keywords: List[str],
    target_sub_count: int = 10,
    target_kw_count: int = 20,
    time_filter: str = "month",
    probe_limit: int = 15,
) -> Tuple[List[str], List[str], Dict[str, int]]:
    """
    Probe candidate subreddits and keywords, keep those that actually yield posts.
    Returns curated subreddits, curated keywords, and per-subreddit hit counts.
    """
    sub_hits: Dict[str, int] = {}
    kw_hits: Dict[str, int] = {kw: 0 for kw in candidate_keywords}

    working_subs = []

    for sub in candidate_subreddits:
        try:
            subreddit = reddit.subreddit(sub)
            total_hits = 0
            for method in ("hot", "top", "new"):
                if method == "top":
                    posts = subreddit.top(time_filter=time_filter, limit=probe_limit)
                elif method == "hot":
                    posts = subreddit.hot(limit=probe_limit)
                else:
                    posts = subreddit.new(limit=probe_limit)

                checked = 0
                for p in posts:
                    checked += 1
                    text = f"{p.title} {getattr(p, 'selftext', '')}"
                    hits = _keyword_match(text, candidate_keywords)
                    if hits:
                        total_hits += 1
                        for h in hits:
                            kw_hits[h] += 1
                    if checked >= probe_limit:
                        break
            if total_hits > 0:
                sub_hits[sub] = total_hits
                working_subs.append(sub)
        except Exception:
            # Inaccessible sub (e.g., 403)
            continue

    # Rank and trim
    curated_subs = sorted(working_subs, key=lambda s: sub_hits.get(s, 0), reverse=True)[:target_sub_count]
    curated_kws = [kw for kw, _ in sorted(kw_hits.items(), key=lambda x: x[1], reverse=True)[:target_kw_count]]

    return curated_subs, curated_kws, sub_hits






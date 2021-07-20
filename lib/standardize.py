import pandas as pd


def standardize_from_lookup_table(df: pd.DataFrame, col: str, lookup_table: list[list[str]]) -> pd.DataFrame:
    """Standardize a column with a lookup table.

    Each entry in lookup table contain all variations of a string that need to be standardize.
    The first string in an entry is considered canonical and all variations will be replaced
    with it.

    For example with lookup table:
    [
        ...
        ["the university of sydney", "sydney uni", "university sydney"],
        ...
    ]
    The strings "sydney uni", "university sydney" will be replaced with "the university of sydney"

    This function also print unmatched strings after a successful run

    Args:
        df (pd.DataFrame):
            the frame to process
        col (str):
            the column to standardize
        lookup_table (list of list of str):
            list of entries that need to be standardized. The first string in an entry
            is considered canonical and all subsequent strings are variations that need
            to be replaced with the canonical string.

    Returns:
        the processed frame
    """
    # create list of sequences sorted by length
    table = []
    for i, seqs in enumerate(lookup_table):
        for s in seqs:
            table.append((len(s), s, i))
    table.sort(key=lambda x: x[0], reverse=True)
    sorted_lens, sorted_seqs, sorted_inds = zip(*table)

    unmatched_seqs = set()

    def find_seq(s):
        if pd.isna(s):
            return []
        seqs = []
        sub_strs = [s]
        while len(sub_strs) > 0:
            sub_str = sub_strs.pop()
            str_len = len(sub_str)
            # limit searches to sequences of equal or less length
            for start_ind, n in enumerate(sorted_lens):
                if n <= str_len:
                    break
            for i, seq in enumerate(sorted_seqs[start_ind:]):
                try:
                    pat_start_ind = sub_str.index(seq)
                    break
                except ValueError:
                    pass
            else:
                unmatched_seqs.add(sub_str)
                continue
            i = i + start_ind
            seqs.append(sorted_inds[i])
            if pat_start_ind > 0:
                sub_strs.append(sub_str[:pat_start_ind])
            pat_end_ind = pat_start_ind + sorted_lens[i]
            if pat_end_ind < str_len:
                sub_strs.append(sub_str[pat_end_ind:])
        return sorted(seqs)

    def join_seqs(seqs):
        return "; ".join(list(map(lambda x: lookup_table[x][0], seqs)))

    df.loc[:, col] = df[col].map(find_seq).map(join_seqs)

    print("standardize_from_lookup_table: unmatched sequences:\n  %s" %
          unmatched_seqs)

    return df

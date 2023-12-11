from .__init__ import *
from .config import datapath

# Load cosine similarity matrix, if it doesn't exist, compute it and store it


def compute_top_k_cosine_similarity_skipping_zeros(R: np.array, k: int=30 )-> np.ndarray:
    n_movies = R.shape[1]
    S = np.zeros((n_movies, n_movies))
    eps = 1e-10

    for i in tqdm(range(n_movies)):
        # Use broadcasting to find set of non-zero users for both columns i and j
        valid_indices = R[:, i] != 0

        for j in range(i + 1, n_movies):
            # Find common valid indices for both columns i and j (i.e. a binary mask of valid indices for both columns)
            l = valid_indices & (R[:, j] != 0) # logical and to check the movies was rated by the same user

            if np.sum(l) >= 3:
                dot_prod = np.sum(R[l, i] * R[l, j])
                norm_i = np.linalg.norm(R[l, i])
                norm_j = np.linalg.norm(R[l, j])

                S[i, j] = 0.5 + 0.5 * (dot_prod / (norm_i * norm_j + eps))

        # Keep only top k
        top_k_indices = np.argpartition(S[i, :], -k)[-k:] # get top k indices
        # Set all indices not in top k to 0
        S[i, :][~np.isin(np.arange(n_movies), top_k_indices)] = 0 #S[i, ~top_k_indices] = 0
    return S

def get_similarity_matrix(R: np.ndarray, 
                          k: int = 30,
                          datapath: Path = datapath,
                          filename: str = 'similarity_matrix_top_k.npy') -> np.ndarray:
    """Get similarity matrix

    Args:
        R (np.ndarray): Rating matrix
        metric (str, optional): Similarity metric. Defaults to 'cosine'.
        filename (str, optional): Filename to save/load similarity matrix. Defaults to 'similarity_matrix.npy'.

    Returns:
        np.ndarray: Similarity matrix
    """
    path = datapath/filename
    if os.path.exists(path):
        print(f"Loading similarity matrix from {path}")
        similarity_matrix = np.load(path)
    else:
        if not os.path.exists(datapath):
            os.makedirs(datapath)
        print(f"Computing similarity matrix using k = {k}")
        similarity_matrix = compute_top_k_cosine_similarity_skipping_zeros(R, k=30)
        np.save(path, similarity_matrix)
    return similarity_matrix
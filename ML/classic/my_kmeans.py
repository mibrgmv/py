import numpy as np


def euclidean_distance(x1, x2):
    return np.sqrt(np.sum((x1 - x2)**2))

class MyKMeans:
    def __init__(self, n_clusters, max_iter=300):
        self.n_clusters = n_clusters
        self.max_iter = max_iter

    def fit(self, data):
        self.centroids = data[np.random.choice(data.shape[0], self.n_clusters, replace=False)]

        for _ in range(self.max_iter):

            clusters = [[] for _ in range(self.n_clusters)]
            for x in data:
                distances = [euclidean_distance(x, centroid) for centroid in self.centroids]
                cluster_idx = np.argmin(distances)
                clusters[cluster_idx].append(x)

            self.centroids = np.array([np.mean(cluster, axis=0) for cluster in clusters])

    def predict(self, data):
        labels = []
        for x in data:
            distances = [euclidean_distance(x, centroid) for centroid in self.centroids]
            label = np.argmin(distances)
            labels.append(label)
        return np.array(labels)

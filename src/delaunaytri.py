import numpy as np
from math import sqrt


class DelaunayTriangulation:
    def __init__(self, center=(0, 0), radius=9999):

        center = np.asarray(center)

        self.coords = [
            center + radius * np.array((-1, -1)),
            center + radius * np.array((+1, -1)),
            center + radius * np.array((+1, +1)),
            center + radius * np.array((-1, +1)),
        ]

        self.triangles = {}
        self.circles = {}

        T1 = (0, 1, 3)
        T2 = (2, 3, 1)
        self.triangles[T1] = [T2, None, None]
        self.triangles[T2] = [T1, None, None]

        for t in self.triangles:
            self.circles[t] = self.circumcenter(t)

    def circumcenter(self, tri):

        poiints = np.asarray([self.coords[v] for v in tri])
        poiints2 = np.dot(poiints, poiints.T)
        A = np.bmat([[2 * poiints2, [[1], [1], [1]]], [[[1, 1, 1, 0]]]])

        b = np.hstack((np.sum(poiints * poiints, axis=1), [1]))
        x = np.linalg.solve(A, b)
        bary_coords = x[:-1]
        center = np.dot(bary_coords, poiints)

        radius = np.sum(np.square(poiints[0] - center))
        return (center, radius)

    def inCircleFast(self, tri, p):

        center, radius = self.circles[tri]
        return np.sum(np.square(center - p)) <= radius

    def addPoint(self, p):

        p = np.asarray(p)
        idx = len(self.coords)

        self.coords.append(p)

        bad_triangles = []
        for T in self.triangles:
            if self.inCircleFast(T, p):
                bad_triangles.append(T)

        boundary = []

        T = bad_triangles[0]
        edge = 0

        while True:

            tri_op = self.triangles[T][edge]
            if tri_op not in bad_triangles:

                boundary.append((T[(edge + 1) % 3], T[(edge - 1) % 3], tri_op))
                edge = (edge + 1) % 3
                if boundary[0][0] == boundary[-1][1]:
                    break
            else:

                edge = (self.triangles[tri_op].index(T) + 1) % 3
                T = tri_op
        for T in bad_triangles:
            del self.triangles[T]
            del self.circles[T]

        new_triangles = []
        for (e0, e1, tri_op) in boundary:

            T = (idx, e0, e1)

            self.circles[T] = self.circumcenter(T)

            self.triangles[T] = [tri_op, None, None]

            if tri_op:

                for i, neigh in enumerate(self.triangles[tri_op]):
                    if neigh:
                        if e1 in neigh and e0 in neigh:

                            self.triangles[tri_op][i] = T

            new_triangles.append(T)

        N = len(new_triangles)
        for i, T in enumerate(new_triangles):
            self.triangles[T][1] = new_triangles[(i + 1) % N]
            self.triangles[T][2] = new_triangles[(i - 1) % N]

    def exportTriangles(self):

        return [
            (a - 4, b - 4, c - 4)
            for (a, b, c) in self.triangles
            if a > 3 and b > 3 and c > 3
        ]

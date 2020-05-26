import cv2
from imutils import face_utils
import numpy as np
import imutils
import dlib
from PIL import Image
import imageio
import sys
from delaunaytri import DelaunayTriangulation
import glob


def shape_to_np(shape, dtype="int"):
	coords = np.zeros((72, 2), dtype=dtype)
	for i in range(0, 72):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	return coords


class ResizeImage():
    def __init__(self, image_one_path, image_two_path):
        self.image_one_path = image_one_path
        self.image_two_path = image_two_path
        self.img1 = cv2.imread(image_one_path)
        self.img2 = cv2.imread(image_two_path)

    def resizer(self):
        min_ht = min(self.img1.shape[0], self.img2.shape[0])
        min_wd = min(self.img1.shape[1], self.img2.shape[1])
        dims = (min_wd, min_ht)
        self.img1 = cv2.resize(self.img1, dims, interpolation=cv2.INTER_AREA)
        self.img2 = cv2.resize(self.img2, dims, interpolation=cv2.INTER_AREA)
        print("Resized Dims: ", self.img1.shape, self.img2.shape)
        cv2.imwrite(self.image_one_path, self.img1)
        cv2.imwrite(self.image_two_path, self.img2)

class CreateControlPoints():
    def __init__(self, img):
        self.img = img


    def create_control_points(self):  
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
        self.image = cv2.imread(self.img)
        # image = imutils.resize(self.image, width=500)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)
        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            
            if type(shape) != None:
                corner_pts = [
                                [0, 0], 
                                [self.image.shape[1] - 1, self.image.shape[0] - 1], 
                                [self.image.shape[1] - 1,  0], 
                                [0, self.image.shape[0] - 1]
                            ]

                shape = np.append(shape, corner_pts, axis = 0)
                print("Computed Points. {}".format(len(shape)))
                return shape
            # brackets = ["[","]"]
            # for coordinate in shape:
            #     coordinate = str(coordinate)
            #     coordinate = "".join(points for points in coordinate if not points in brackets)
            #     coordinate = coordinate.replace(" ", ", ")
            #     self.coordinate = coordinate
            #     return coordinate


class CreateTriangle():
    def __init__(self, coord_one, coord_two):
        self.coord_one = coord_one
        self.coord_two = coord_two

    def create_triangles(self):
        dt = DelaunayTriangulation()
        pts = []
        for pts1, pts2 in zip(self.coord_one, self.coord_two):
            #  print("ONE = {} | TWO = {}".format(i, j))
            x = (pts1[0] + pts2[0]) / 2
            y = (pts1[1] + pts2[1]) / 2
            pts.append((x, y))
            dt.addPoint((x, y))
        dt_tris = dt.exportTriangles()
        print(len(dt_tris), "Delaunay triangles")
        return(dt_tris)

class CreateAffineTransform():

    def __init__(self, dt_tris, img1, img2, coord1, coord2):
        self.dt_tris = dt_tris
        self.img1 = np.float32(cv2.imread(img1))
        self.img2 = np.float32(cv2.imread(img2))
        self.coord1 = coord1
        self.coord2 = coord2

    def applyingAT(self, src, sT, dT, sz):
        # finding the affine transform on the given tri's
        warpMat = cv2.getAffineTransform(np.float32(sT), np.float32(dT))

        # Applying the  Affine Transform
        output = cv2.warpAffine(
            src,
            warpMat,
            (sz[0], sz[1]),
            None,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )

        return output

    def morphingTriangles(self, img1, img2, img, t1, t2, t, alpha):

        # Bounding rectangles
        r1 = cv2.boundingRect(np.float32([t1]))
        r2 = cv2.boundingRect(np.float32([t2]))
        r = cv2.boundingRect(np.float32([t]))

        # Offsetting
        t1Rect = []
        t2Rect = []
        tRect = []

        for i in range(0, 3):
            tRect.append(((t[i][0] - r[0]), (t[i][1] - r[1])))
            t2Rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))
            t1Rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))

        # Fill the triangles to get a mask to be used at later stage
        msk = np.zeros((r[3], r[2], 3), dtype=np.float32)
        cv2.fillConvexPoly(msk, np.int32(tRect), (1.0, 1.0, 1.0), 16, 0)

        iR1 = img1[r1[1] : r1[1] + r1[3], r1[0] : r1[0] + r1[2]]
        iR2 = img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]]

        size = (r[2], r[3])
        wI1 = self.applyingAT(iR1, t1Rect, tRect, size)
        wI2 = self.applyingAT(iR2, t2Rect, tRect, size)

        # Blend and copy the patches
        iR = (1.0 - alpha) * wI1 + alpha * wI2
        img[r[1] : r[1] + r[3], r[0] : r[0] + r[2]] = (
            img[r[1] : r[1] + r[3], r[0] : r[0] + r[2]] * (1 - msk) + iR * msk
        )

    def perform_affine_transform(self, factor = 40):
        for i in range(0, factor):
            alpha = i / factor
            # print(alpha)
            points = []
            # Compute weighted average point coordinates
            for pts1, pts2 in zip(self.coord1, self.coord2):
                x = (1 - alpha) * pts1[0] + alpha * pts2[0]
                y = (1 - alpha) * pts1[1] + alpha * pts2[1]
                points.append((x, y))
            # print(points)
            # print(self.img1.shape)
            # Allocate space for final output
            imgMorph = np.zeros(self.img1.shape, dtype=self.img1.dtype)
            for single_tri_coord in self.dt_tris:
                x, y, z = single_tri_coord
                x = int(x)
                y = int(y)
                z = int(z)

                t1 = [self.coord1[x], self.coord1[y], self.coord1[z]]
                t2 = [self.coord2[x], self.coord2[y], self.coord2[z]]
                t = [points[x], points[y], points[z]]
                # print(t1, t2, t)
                # Morph one triangle at a time.
                self.morphingTriangles(self.img1, self.img2, imgMorph, t1, t2, t, alpha)

            # Display Result
            # cv2.imshow("Morphed Face", np.uint8(imgMorph))
            x = i + 100
            frame = './morph_frames/' + "frame_" + str(x) + ".jpg"
            cv2.imwrite(frame, (imgMorph))
    
        images = []
        filenames = glob.glob("./morph_frames/" + "*.jpg")
        # print(filenames)
        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimsave("./output_gif/morphed.gif", images)
        print("GIF Created and SAVED!")

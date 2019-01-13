import numpy as np
import argparse
import matplotlib.pyplot as plt
import cv2
import sys
import os
import os.path as osp

#Performing canny edge detection 
def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
            v = np.median(image)
    # apply automatic Canny edge detection using the computed median
            lower = int(max(0, (1.0 - sigma) * v))
            upper = int(min(255, (1.0 + sigma) * v))
            edged = cv2.Canny(image, lower, upper)
    # return the edged image
            return edged
#Denoising the image     
def denoise(image,lower,upper):
            drawing = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    if (image[i,j] < lower):
                        drawing[i,j] = 0
                    elif(image[i,j] > upper):
                        drawing[i,j] = 255
                    else:
                        drawing[i,j]=image[i,j]
            return drawing


def argument_parser():
    """
    argument parser : 
    return ; argparse object with imag dir
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--images", required=True, help="path to input dataset of images")
    return ap.parse_args()
def get_images(opt):
    images = opt.images 
    try :
        imlist = [osp.join(osp.realpath('.'), images, img) for img in os.listdir(images) if os.path.splitext(img)[1] =='.txt']
    except NotADirectoryError:
        imlist=[]
        imlist.append(osp.join(osp.realpath('.'),images))
    except FileNotFoundError:
           print ("No file or directory with the name {}".format(images))
           exit()
    return imlist       
def main():
    """
    main function to run this script. 
    """
    # construct the argument parse and parse the arguments
    print("in main")

    args = argument_parser()
    print(args)
    # a = "./Images"
    count_of_image = 0
    im = get_images(args)
    # print(im)
    for imagePath in im:
        
        env1 = np.loadtxt(imagePath)
        img = env1        
        plt.rcParams['image.cmap'] = 'gray' # Necessary to override default matplot behaviour
        print("Image:"+ "{}".format(count_of_image)) 
        plt.imshow( img)
        plt.show()
        
        drawing = denoise(img,1,4)        
        plt.imshow(drawing)
        plt.show()

		# img1  = auto_canny(cv2.boxFilter(drawing, (5, 5),0))
        img1  = auto_canny(cv2.medianBlur(drawing, 5))
        plt.imshow(img1)
        plt.show()

        img1  = cv2.dilate(img1, None, iterations=2)
        plt.imshow(img1)
        plt.show()

        img1  = cv2.erode(img1, None, iterations=2)
        plt.imshow(img1)
        plt.show()

        cropped = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
        cropped[30:108,60:120]=img1[30:108,60:120]# get the interested region
		#         cropped[35:110,60:120]=img1[35:110,60:120]# get the interested region
        plt.imshow(cropped)
        plt.show()
        
		#CONTOUR DETECTION and FINDING the BOUNDING BOX        
        img2, contours, hierarchy = cv2.findContours(cropped, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
        screenCnt = None
        contours_poly = [None]*len(contours)
        boundRect = [None]*len(contours)
        
        for i, c in enumerate(contours):
            contours_poly[i] = cv2.approxPolyDP(c, 3, True)
            boundRect[i] = cv2.boundingRect(contours_poly[i])
			#Calculating the clearance value for avoidance maneuver 
            left = boundRect[0][0]-60
            right = 120-(boundRect[0][0]+boundRect[0][2])            
            clearance_left = left*1.5/60
            clearance_right = right*1.5/60
            cv2.imwrite('mine.png',env1)
            image = cv2.imread('mine.png')
            for i in range(len(contours)):
                color = (0, 255, 125)
                cv2.rectangle(image, (int(boundRect[i][0]), int(boundRect[i][1])), \
                	(int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, 1)
                plt.imshow(image)
                plt.show()
            if (left > right):
                
                print("Since the clearance value is:",clearance_left)
                print("ROBOT! Please move left") 
            else:
                
                print("Since the clearance value is:",clearance_right)
                print("ROBOT! Please move right")
            

            count_of_image = count_of_image +1


if __name__ == '__main__':
    main()

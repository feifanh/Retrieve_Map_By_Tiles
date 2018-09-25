import os
import urllib
import math
import time
from decimal import Decimal
from PIL import Image

from tileGeoTransfer import *


def checkBlankImg_B(filename):
	'''
	input type: file path
	return type: Boolean
	'''
	im = Image.open(filename)
	pix = im.load()

	# print im.size
	pixel_values = list(im.getdata())
	
	# RGB channel
	if min(pixel_values) == max(pixel_values):
		return True

	return False


def checkBlankImg_A(filename):
	'''
	input type: file path
	return type: Boolean
	'''
	im = Image.open(filename)
	pix = im.load()

	# print im.size
	pixel_values = list(im.getdata())
	zipped = zip(pixel_values)

	# RGB channel
	if min(zipped[0][0]) == max(zipped[0][0]) \
		and min(zipped[1][0]) == max(zipped[1][0]) \
		and min(zipped[2][0]) == max(zipped[2][0]):
		return True

	return False


# store four corner (lat, long) of a tile image into txt file
def store_4Geo_Boundary(lnglat_path, x, y, z):
	f = open(lnglat_path,"w+")

	# bottom right
	lat, lng = getGeoFromTile(x, y, z)
	f.write("%f %f\n"%(lat, lng))

	# bottom left
	lat, lng = getGeoFromTile(x + 1, y, z)
	f.write("%f %f\n"%(lat, lng))

	# top right
	lat, lng = getGeoFromTile(x, y + 1, z)
	f.write("%f %f\n"%(lat, lng))

	# top left
	lat, lng = getGeoFromTile(x + 1, y + 1, z)
	f.write("%f %f\n"%(lat, lng))

	f.close()


def getImgFromUrl(url_A, url_B, stored_directory, x, y, z):
	obj_A = urllib.urlopen(url_A)
	obj_B = urllib.urlopen(url_B)


	if obj_A.getcode() == 200 and obj_B.getcode() == 200:

		if not os.path.exists(stored_directory):
			os.makedirs(stored_directory)

		name_A = stored_directory + "mapA_%d_%d_%d.jpg" % (x, y, z)
		name_B = stored_directory + "mapB_%d_%d_%d.jpg" % (x, y, z)
		urllib.urlretrieve(url_A, name_A)
		urllib.urlretrieve(url_B, name_B)


		# Check if the image is blank, i.e: sea, plain grass
		if checkBlankImg_A(name_A) or checkBlankImg_B(name_B):
			if os.path.exists(name_A) and os.path.exists(name_B):
				os.remove(name_A)
				os.remove(name_B)
				print "delete: ", x, y, z
			else:
				print "file does not exist"
		else:
			lnglat_dir = stored_directory + "lnglat/"
			if not os.path.exists(lnglat_dir):
				os.makedirs(lnglat_dir)

			lnglat_path = lnglat_dir + "map_%d_%d_%d.txt" % (x, y, z)
			store_4Geo_Boundary(lnglat_path, x, y, z)
			
			print "success: ", x, y, z
	else:
		print "F", x, y, z


def retrieveMap_byxyz(x_start, x_end, y_start, y_end, z):
	# Please put the given url format here
	urlBase_A_map = "" # url 1
	urlBase_B_map = "" # url 2
	
	stored_directory = "folder_xyz_16/"
	
	for x in xrange(x_start, x_end + 1):
		for y in xrange(y_start, y_end + 1):
			
			# different url may have different order of x, y, z
			url_A_map = urlBase_A_map % (z, x, y)
			url_B_map = urlBase_B_map % (z, x, y)
			
			getImgFromUrl(url_A_map, url_B_map, stored_directory, x, y, z)
			time.sleep(0.005)


# get the tile index boundaries from longitude and latitude
def getBoundary(start_lat, end_lat, start_long, end_long, zoom):
	x0, y0, z = getTileFromGeo(start_lat, start_long, zoom)
	x1, y1, z = getTileFromGeo(start_lat, end_long, zoom)
	x2, y2, z = getTileFromGeo(end_lat, start_long, zoom)
	x3, y3, z = getTileFromGeo(end_lat, end_long, zoom)

	start_x = min(x0, x1, x2, x3)
	end_x = max(x0, x1, x2, x3)
	start_y = min(y0, y1, y2, y3)
	end_y = max(y0, y1, y2, y3)

	retrieveMap_byxyz(start_x, end_x, start_y, end_y, z)


if __name__ == "__main__":
	getBoundary(52.0000, 54.0000, -1.0000, 1.0000, 16)




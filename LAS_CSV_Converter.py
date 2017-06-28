#!/usr/bin/env python
'''
    LAS_CSV_Converter.py : This python script is intended to convert LIDAR LAS files to and from CSV format
'''

__author__ = "Hieu Nguyen"
__copyright__ = "Copyright 2017, Hieu Nguyen"
__version__ = "1.0"
__status__ = "Development"

import numpy as np
import csv
import datetime
from laspy import *

# LASFileManager : handles IO streams of LAS to CSV
class LASFileManager:

    def __init__(self, infilename, outfilename):
        self.inFileName = infilename
        self.outFileName = outfilename

        self.readStream = None
        self.writeStream = None

        self.fileInfo = None

    def open_read_stream(self):
        self.readStream = file.File(self.inFileName, mode='r')

        num_points = self.readStream.__len__()

        # Obtain offsets and scaling values
        x_offset = self.readStream.header.offset[0]
        y_offset = self.readStream.header.offset[1]
        z_offset = self.readStream.header.offset[2]

        x_scale = self.readStream.header.scale[0]
        y_scale = self.readStream.header.scale[1]
        z_scale = self.readStream.header.scale[2]

        header_size = sum(1 for i in self.readStream.point_format)
        attributes = []

        # Obtain the header information
        for attribute in self.readStream.point_format:
            attributes.append(attribute.name)

        # init file information
        self.fileInfo = FileInfo(num_points,
                                 x_offset, y_offset, z_offset,
                                 x_scale, y_scale, z_scale,
                                 header_size, attributes)

    def close_read_stream(self):
        self.readStream.close()

    def open_write_stream(self):
        self.writeStream = open(self.outFileName, mode='w')

    def close_write_stream(self):
        self.writeStream.close()

    def writeln(self, content):
        self.writeStream.write(content + "\n")


# CSVFileManager : handles IO streams of CSV to LAS
class CSVFileManager:

    def __init__(self, infilename, outfilename):
        self.infilename = infilename
        self.outfilename = outfilename

        self.readStream = None
        self.writeStream = None

        self.X_points = []
        self.Y_points = []
        self.Z_points = []


    def open_read_stream(self):
        # self.readStream = open(self.infilename, mode='r')
        self.readStream = csv.reader(open(self.infilename, mode='r'), delimiter=' ')

    def close_read_stream(self):
        self.readStream.close()

    def open_write_stream(self, head):
        self.writeStream = file.File(self.outfilename, mode='w', header=head)

    def close_write_stream(self):
        self.writeStream.close()

    def add_point(self, x, y, z):
        self.X_points.append(x)
        self.Y_points.append(y)
        self.Z_points.append(z)

    def load_points(self):
        for row in self.readStream:
            self.add_point(row[0], row[1], row[2])

    def push_points(self):
        self.writeStream.X = np.array(self.X_points)
        self.writeStream.Y = np.array(self.Y_points)
        self.writeStream.Z = np.array(self.Z_points)

    def set_header_info(self, _file_signature, _date, _min, _max, _version, _offset, _scale, _software_id, _system_id):
        #self.writeStream.header.file_signature = _file_signature
        self.writeStream.header.date = datetime.datetime(_date[0], _date[1], _date[2])
        #self.writeStream.header.file_source_id
        #self.writeStream.header.guid

        self.writeStream.header.max = _max
        self.writeStream.header.min = _min

        _major, _minor = _version.split(".")
        self.writeStream.header.major_version = _major
        self.writeStream.header.minor_version = _minor

        self.writeStream.header.offset = _offset
        self.writeStream.header.scale = _scale

        self.writeStream.header.software_id = '{:<32}'.format(_software_id[:32])
        self.writeStream.header.system_id = '{:<32}'.format(_system_id[:32])


# FileInfo : holds onto information of the file
class FileInfo:

    def __init__(self, num_points, x_offset, y_offset, z_offset,
                                 x_scale, y_scale, z_scale,
                                 header_size, attributes):

        self.num_points = num_points
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.z_scale = z_scale
        self.header_size = header_size
        self.attributes = attributes

    def get_header(self):
        head = ""
        index = 0

        for att in self.attributes:
            index += 1
            head += str(att)

            if index < self.header_size:
                head += ","

        return head

# INCOMPLETE - this function has not yet been fully implemented
def csv_to_las(input_file_name, output_file_name):

    manager = CSVFileManager(input_file_name, output_file_name)

    head = header.Header()

    #manager.open_read_stream()
    manager.open_write_stream(head)

    #inFile = manager.readStream
    outFile = manager.writeStream

    file_sig = 'LASF'
    date = [2013,6,4]
    maxx = [330786.99,4840757.20,990.56]
    minn = [329127.03, 4839565.68, 4839565.68]
    offset = [329999.8947, 4839000.0062, 0.0]
    scale = [0.0001, 0.0001, 0.0001]
    soft_id = "software_id"
    sys_id = "system_id"
    version = "1.2"

    manager.set_header_info(file_sig,date,minn,maxx,version,offset,scale,soft_id,sys_id)

    manager.add_point(329999.8947,4839000.0062,0.671)
    manager.add_point(330002.2338,4838999.6872,0.617)
    manager.add_point(330026.3268,4839042.692,0.417)
    manager.add_point(330047.6052,4839040.4722,0.7269)
    manager.add_point(330051.1468,4839040.851,0.645)
    manager.add_point(330020.8758,4839046.2249,0.2888)

    manager.push_points()

    #manager.close_read_stream()
    manager.close_write_stream()

# las_to_csv : pretty self explanatory
def las_to_csv(input_file_name, output_file_name):

    fileManager = LASFileManager(input_file_name, output_file_name)

    # open read and write streams
    fileManager.open_read_stream()
    fileManager.open_write_stream()

    # get streams
    inFile = fileManager.readStream
    outFile = fileManager.writeStream

    # get file information
    file_info = fileManager.fileInfo

    # write header information to csv
    outFile.write(file_info.get_header() + "\n")

    attributes = file_info.attributes

    # counter for progress
    progressCounter = 0
    progressMax = file_info.num_points

    # write point information to csv
    for points_list in inFile.points:

        for points in points_list:

            lineValues = []
            line = ""
            index = 0

            for attribute in points:

                # obtain actual value after accounting for scaling and offset values
                if attributes[index] == "X":
                    outValue = ( attribute * file_info.x_scale ) + file_info.x_offset
                elif attributes[index] == "Y":
                    outValue = ( attribute * file_info.y_scale ) + file_info.y_offset
                elif attributes[index] == "Z":
                    outValue = ( attribute * file_info.z_scale ) + file_info.z_offset
                else:
                    outValue = attribute

                lineValues.append(outValue)
                line += (str(outValue))

                if index < file_info.header_size-1:
                    line += ","

                index += 1

            outFile.write(line + "\n")

        progressCounter += 1

        if progressCounter % 1000 == 0:
            print(str(progressCounter) + " / " + str(progressMax))
            # break

    # close streams
    inFile.close()
    outFile.close()

# las_to_csv_2 : extracts only x,y,z values to be transformed
def las_to_csv_2(input_file_name, output_file_name, utm_zone):

    fileManager = LASFileManager(input_file_name, output_file_name)

    # open read and write streams
    fileManager.open_read_stream()
    fileManager.open_write_stream()

    # get streams
    inFile = fileManager.readStream
    outFile = fileManager.writeStream

    # get file information
    file_info = fileManager.fileInfo

    # write header information to csv
    outFile.write("utm_e,utm_n,height," + utm_zone + "\n")

    attributes = file_info.attributes

    # counter for progress
    progressCounter = 0
    progressMax = file_info.num_points

    # write point information to csv
    for points_list in inFile.points:

        for points in points_list:

            lineValues = []
            line = ""
            index = 0

            for attribute in points:

                # obtain actual value after accounting for scaling and offset values
                if attributes[index] == "X":
                    outValue = ( attribute * file_info.x_scale ) + file_info.x_offset
                elif attributes[index] == "Y":
                    outValue = ( attribute * file_info.y_scale ) + file_info.y_offset
                elif attributes[index] == "Z":
                    outValue = ( attribute * file_info.z_scale ) + file_info.z_offset
                elif index == 3:
                    outValue = "ON-9"
                else:
                    break
                    outValue = attribute

                lineValues.append(outValue)
                line += (str(outValue))

                if index < 3:#file_info.header_size-1:
                    line += ","

                index += 1

            outFile.write(line + "\n")

        progressCounter += 1

        if progressCounter % 1000 == 0:
            print(str(progressCounter) + " / " + str(progressMax))
            break

    # close streams
    inFile.close()
    outFile.close()

# Main Script
inf = "0243690065100_2013_ALLHITS.las"
outf = "output_full_trunc.csv"

las_to_csv_2(inf, outf, "ON-9")

#fm = LASFileManager(inf, outf)
#fm.open_read_stream()
#fm.open_write_stream()
#
#for i in fm.readStream.header.vlrs:
#    print(i.to_byte_string())


# asd = file.File(inf, mode='rw')
#
# x = asd.X
# y = asd.Y
# z = asd.Z
#
# asd.X = y
# asd.Y = z
# asd.Z = x
#
# asd.close()

#fm.readStream.X = y
#fm.readStream.Y = z
#fm.readStream.Z = x

# lasfm = base.FileManager(inf, mode='r')

#print(fm.readStream.point_format.etree())

#fm.writeln(str(fm.readStream.header.schema.xml()))

#csv_to_las("", "test.las")

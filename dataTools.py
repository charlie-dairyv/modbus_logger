#!/usr/bin/python

import csv
import sys, getopt
from collections import OrderedDict
import datetime as dt

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

   print 'Input file is "', inputfile
   print 'Output file is "', outputfile

def csvMerger(filename1,filename2,outputfile):
    """Interleaves two CSV files
        The new set of headers will be the union of the two sets of headers.
        Tries to interleave the two data sets, adding points from the shorter list
        to the nearest datapoint in the longer list
    """
    data=OrderedDict()
    with open(filename1,'rU') as file1:
        with open(filename2,'rU') as file2:
            reader1 = csv.DictReader(file1, dialect='excel')
            reader2 = csv.DictReader(file2, dialect='excel')

            data1 = []
            for each in reader1:
                data1.append(each)
            data2 = []
            for each in reader2:
                data2.append(each)

    combinedData = data1 + data2

    sortedCombinedData = sorted(combinedData, key=lambda k: k['time'])

    write_headers = set(data1[0].keys() + data2[0].keys())

    with open(outputfile,'w') as f:
        writer = csv.DictWriter(f, fieldnames=write_headers)
        headers = dict( (n,n) for n in write_headers )
        writer.writerow(headers)
        for each in sortedCombinedData:
            writer.writerow(each)


def list_to_csv(filename,outputfilename):
    """converts list of datapoints from datagetter to csv format
    """
    data=OrderedDict()
    with open(filename,'rU') as file:
        reader = csv.reader(file, delimiter='\t')

        read_headers = ['time', 'tag', 'value']
        for col in read_headers:
            data[col.strip()] = []
        print "Headers = %s" % data.keys()

        for row in reader:
            key = data.iterkeys()
            for col in row:
                thisKey = key.next()
                try:
                    data[thisKey].append(float(col))
                except:
                    data[thisKey].append(col)

        ldata = zip(data['time'], data['tag'], data['value'])


        write_headers = ['time']
        for each in set(data['tag']):
            write_headers.append(each)

        #data = []
        #for each in ldata:
    with open(outputfilename,'w') as f:
        writer = csv.DictWriter(f, fieldnames=write_headers)
        headers = dict( (n,n) for n in write_headers )
        writer.writerow(headers)
        for each in ldata:
            writer.writerow({'time':each[0], each[1]:each[2]})

def elapsedmin_to_ctime(filename, time0):
    """ Does a thing
    """
    with open(filename,'rU') as file:
        reader = csv.DictReader(file, dialect='excel')

        data=[]
        for row in reader:
            try:
                time = row['time']
            except:
                try:
                    time = row['Time']
                    row.pop('Time')
                except:
                    raise ValueError, 'CSV file has no header "time"'

            if time == '':
                pass
            else:
                coercedtime = float(time)
                delt = dt.timedelta(minutes=float(coercedtime))
                row['time'] = time0 + delt
                data.append(row)

    fieldnames = data[0].keys()

    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        headers = dict( (n,n) for n in fieldnames )
        writer.writerow(headers)
        for each_row in data:
            writer.writerow(each_row)

def hhmm_to_ctime(file, date):
    """converts an hh:mm timestamp from orig excel to ctime

    file - CSV formatted, possibly excel dialect
    date = datetime.date object
    """
    with open(filename,'rU') as file:
        reader = csv.DictReader(file, dialect='excel')

        data=[]
        for row in reader:
            try:
                time = row['time']
            except:
                try:
                    time = row['Time']
                    row.pop('Time')
                except:
                    raise ValueError, 'CSV file has no header "time"'

            if time == '':
                pass
            else:
                coercedtime = float(time)
                row['time'] = time0 + delt
                data.append(row)

    fieldnames = data[0].keys()

    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        headers = dict( (n,n) for n in fieldnames )
        writer.writerow(headers)
        for each_row in data:
            writer.writerow(each_row)



if __name__ == "__main__":
   #main(sys.argv[1:])
   #list_to_csv('test.csv','newdata.csv')
   #zero = dt.datetime.strptime('2014-09-12 09:10AM' , '%Y-%m-%d %I:%M%p')
   #elapsedmin_to_ctime('20140912data.csv', zero)
   csvMerger('20140912data.csv','test.csv')

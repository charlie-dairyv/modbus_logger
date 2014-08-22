import random
import datetime
import sys

import logging
logger = logging.getLogger(__name__)

logger.debug("--- Initializing Plot.ly ---")
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *

#-----  Get stream keys from credential file
#Keep the stream is's in a Module level var, take them out as they are used.
#New stream ids MUST be added to credential file to be used.  try mvim ~/.plotly/.credentials
#TODO make this a treadsafe datatype?  or lock them?  who knows.


class frontend(object):
    def __init__(self):
        pass
    def write(self,stream,data):
        """prototype of the write interface, non functional

        write() at the very least should take a data point and a stream/target to append it to
        """
        pass

class plotly_frontend(frontend):
    """Creates and manages the interface to Plot.ly

    The pattern for use is Define, then Create, the Write

    Define - through init or add_line, define the traces you will be sending
    Create - Once all traces are created, create the Plot on Plotly
    Write - use the write() method to send data

    Once the plot has been created, cannot change appearance or add new traces.
    """
    def __init__(self, devices=[], max_points=600):
        """ """
        #todo add ability to use custom login credentials
        self.stream_helpers ={}
        self.traces = {}
        self.streams = {}
        self.MODE = 'lines+markers'
        self.max_points = max_points
        self.unique_url = None
        self.mystream_ids = []

        self.mystream_ids += tls.get_credentials_file()['stream_ids']
        logger.debug("Loading Plotly steam ids: %s" % self.mystream_ids)
        logger.debug("Loading Device names: %s" % devices)


        for each in devices:
            try:

                self.stream_helpers[each]= Stream(
                                token=self.mystream_ids.pop(),
                                maxpoints=self.max_points)
            except IndexError:
                logger.warning("Not enough Stream IDs for devices supplied! This device will not be streamed: %s" % each)
            except:
                raise
            finally:
                for name, stream_id in self.stream_helpers.items():
                    logger.info('making trace %s with %s' % (name,stream_id))
                    self.traces[name] = Scatter(x=[],y=[],mode=self.MODE,
                                name=name, stream=stream_id)

    def add_line(self, device, mode=None):
        if mode is None: mode = self.MODE
        self.stream_helpers[each]= Stream(
                                token=stream_ids.pop(),
                                maxpoints=self.max_points)
        logger.info('making trace %s with %s' % (name,stream_id))
        self.traces[name] = Scatter(x=[],y=[],mode=MODE,
                                name=name, stream=stream_id)


    def create(self):
        """Create the Plot and Streams"""
        if self.unique_url is not None:
            #if create has already been called, do nothing and return false
            return False
        else:
            data = Data(self.traces.values())
            layout = Layout(title = "Data %s" % datetime.datetime.now().strftime('%Y-%m-%d'))
            self.fig = Figure(data=data, layout=layout)

            new_plot_name = "Data %s" % datetime.datetime.now().strftime('%Y-%m-%d')
            self.unique_url = py.plot(self.fig, filename=new_plot_name)
            logger.debug("Plot created at %s" % self.unique_url)

            logger.info("Creating streams for %s" % self.stream_helpers.keys())
            for name, stream in self.stream_helpers.items():
                self.streams[name] = py.Stream(stream['token'])
                self.streams[name].open()

            return self.unique_url

    def write(self,target,value,time):
        """Target is the Name of the device for the data point
        value is an (x,y) pair, y is a float, x is in Epoch time"""
        #TODO add fall backs, so that x and y are interchangable with time and data and can be passed as dict
        x=datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S.%f')
        y=value
        baz=dict(x=x,y=y)
        logger.info("Target: %s" % target)
        logger.info("Streams[target]: %s" %  self.streams[target])
        self.streams[target].write(baz)

    def write_event(self, event):
        """Takes an event as an arguament, unpacks it and passes it into write()"""
        logger.debug(event)
        try:
            value = event.value
            time = event.time
            target = event.device.name
        except:
            logger.error("Caught an error in plotly_frontend.write_event(): %s" % sys.exc_info()[0])

        self.write(target, value, time)

    def __del__(self):
        for each in self.streams.values():
            each.close()

def add_stream_id(new_ids):
    """Safe way to add steam id's to credentials

    wraps unsafe tls.set_credentials_file() method"""
    ids = tls.get_credentials_file()['stream_ids']

    for each in new_ids:
        ids.append(each)

    tls.set_credentials_file(stream_ids=ids)
    return True

   #streams[name].write(dict(x=0,y=0))
if __name__ == '__main__':
    import time
    import main

    i=0
    N=600
    devices = ['test']
    graph = plotly_frontend(devices)
    graph.create()

    while i<N:
        i += 1
        baz=dict(value=random.random(), time=time.time())
        graph.write('test',**baz)

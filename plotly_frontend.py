import logging
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *
import random
import datetime
import main

logger = logging.getLogger(__name__)

#get stream keys from credential file
stream_ids = tls.get_credentials_file()['stream_ids']
logger.info(stream_ids)

devices =["TE10", "TE20", "TE21", "TE22"]

#set up
objstreams ={}
traces = {}
MAXPOINTS = 600 #10 min of data points
MODE = 'lines+markers'

for i, stream_id in enumerate(stream_ids):
    objstreams[devices[i]]= Stream(
                                token=stream_id,
                                maxpoints=MAXPOINTS)

for name, stream_id in objstreams.items():
    logger.info('making trace %s with %s' % (name,stream_id))
    traces[name] = Scatter(x=[],y=[],mode=MODE,
                        name=name, stream=stream_id)


data = Data(traces.values())
layout = Layout(title = 'Test123')
fig = Figure(data=data, layout=layout)

new_plot_name = "Data %s" % datetime.datetime.now().strftime('%Y-%m-%d')
unique_url = py.plot(fig, filename=new_plot_name)
logger.warning(unique_url)


streams = {}
for name, stream in objstreams.items():
    streams[name] = py.Stream(stream['token'])
    streams[name].open()
   #streams[name].write(dict(x=0,y=0))

i=0
N=600
while i<N:
    i += 1
    for stream in streams.values():
        x=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        y=random.random()
        baz=dict(x=x,y=y)
        #logger.info("To %s writing %s" % (stream.stream_id['token'],baz))
        stream.write(baz)

for stream in streams.values():
    stream.close()

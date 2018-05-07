# !/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output,State
from data_cleaning import searchword_cleanlasttime as searchword_cleanlasttime
from data_cleaning import makeintervals as makeintervals
from data_cleaning import classify_times as classify_times
from data_cleaning import make_x_y_values as make_x_y_values
from data_cleaning import makelist_timestamps as makelist_timestamps
from data_cleaning import get_vid_id as get_vid_id
from data_cleaning import make_watch_link as make_watch_link
from crawl import pull_transcript as pull_transcript
from data_cleaning import make_time_buckets as make_time_buckets
from data_cleaning import extract_id
from cacher import search_cache
import time


app = dash.Dash(__name__)
server = app.server


@server.route('/hey')
def hello():
    return "Hey theere"

# app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.css.append_css({'external_url': 'https://codepen.io/ivyjx/pen/deGQGd.css'})


app.layout = html.Div(children=[
    html.H1(children='YouTube Suite', style={
        'textAlign': 'center', }),
    html.P(children='Application to search the content of a YouTube video', style={
        'textAlign': 'center', }),


    html.Div([
        html.Div([
            html.Div(children='''
                        Search a YouTube video:
                    '''),
            dcc.Input(
                id='input_url',
                placeholder='Enter video link...',
                type='text',
                size=85,
                value='',
            ),
        ], className='eight columns')
        ,

        html.Div([
            html.Div(children='''
                        Search a word:
                    '''),

            dcc.Input(
                id='input',
                placeholder='Enter a word to search...',
                type='text',
                size=20,
                value='', ),


        ], className='four columns'),

    ], className='row', style={'margin-top': '20'}),

    html.Div([

            html.Div(
                    [
        html.Div(
            [
                html.Div(id='target'),
            ],
                    className='video-container'    ),
        ],
            className='eight columns',
            style={'margin-top': '20'}
        ),
        html.Div(
            [
                # html.H4('Timestamps',),
                html.Div(id='timestamplist'),
                # html.Div(
                # # listtimes, #FIXME
                # style={'width':'180', 'height':'200', 'overflow':'scroll'}   ),
            ], className='four columns', style={'margin-top': '20'}),
    ], className='row'),

    html.Div([
        html.Div(id='output-graph',
                 className='twelve columns', ),
    ], className='row'),


],
    className='ten columns offset-by-one', style={'display': 'inline-block'})


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
    ,[State('input_url', 'value')]
)
def update_value(input1,input2):
    try:

        cleanid = get_vid_id(str(input2))
        selenium_link = make_watch_link(cleanid)
        cache_lasttimestamp, cache_captionsd = search_cache(cleanid)
        if not cache_lasttimestamp and not cache_captionsd:
            print("we gots to runs seleny")
            pull_transcript(selenium_link,cleanid)


        searchedword, list_times, lasttime = searchword_cleanlasttime(input1, cache_lasttimestamp,cache_captionsd)
        print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZz",input2)
        buckets = make_time_buckets(cache_lasttimestamp)
        intervalm, listofintervals = makeintervals(buckets, lasttime)
        dict_raw_times, dict_count_freq = classify_times(listofintervals, list_times)

        xaxis, yaxis, rawtimestamps = make_x_y_values(dict_raw_times, dict_count_freq)
        data = [go.Bar(x=xaxis, y=yaxis, name='{}'.format(searchedword), text=rawtimestamps,
                       marker=dict(color='rgb(78, 150, 150)'), hoverinfo='all')]

        layout = go.Layout(
            title='Frequency for word = " {word}" in intervals of {min} minutes '.format(word=searchedword,
                                                                                         min=intervalm),
            xaxis=dict(title='Timestamp in video'),
            yaxis=dict(title='Occurrence frequency of word', autotick=True),
            bargap=0.1

        )

        return dcc.Graph(
            id='freqchart',
            figure=go.Figure(
                data=data,
                layout=layout)
        )


    except:
        #return "That word is not in the video!"
        return " "


@app.callback(Output('target', 'children'), [Input(component_id='input_url', component_property='value')])
def embed_iframe(value):
    embed_url = extract_id(value)
    print(embed_url)

    return html.Iframe(src=embed_url, width='560', height='315', )


# https://www.youtube.com/watch?v=sh-MQboWJug
# https://www.youtube.com/embed/sh-MQboWJug
# https://www.youtube.com/embed/uZs1AHQBz24?rel=0
# https://www.youtube.com/watch?v=NAp-BIXzpGA&pbjreload=10
# https://www.youtube.com/embed/NAp-BIXzpGA




@app.callback(Output(component_id='timestamplist', component_property='children'),
              [Input(component_id='input', component_property='value')]
              ,[State('input_url', 'value')]
              )
def listingtimes(input1,input2):
    try:
        cleanid = get_vid_id(str(input2))
        selenium_link = make_watch_link(cleanid)
        cache_lasttimestamp, cache_captionsd = search_cache(cleanid)
        if not cache_lasttimestamp and not cache_captionsd:
            print("we gots to runs seleny2222")
            captions_present = pull_transcript(selenium_link,cleanid)
            if captions_present == "No":
                print('RRRRRRRRRRRRRRRRRRRrrr')
                return html.P(children='Captions are not available.', style={
                    'textAlign': 'left', })
        if cache_captionsd == { "." : "[00:00]" }:
            return html.P(children='Captions are not available.', style={
                'textAlign': 'left', })


        if input1 not in cache_captionsd:
            return html.P(children='{} does not appear in video.'.format(input1), style={
                'textAlign': 'left', })


        searchedword, list_times, lasttime = searchword_cleanlasttime(input1, cache_lasttimestamp,cache_captionsd)
        print('XXXXXXXXXXXXXXXXXXXXXXXX', input2)
        intervalm, listofintervals = makeintervals(10, lasttime)
        dict_raw_times, dict_count_freq = classify_times(listofintervals, list_times)
        listtimes = makelist_timestamps(dict_raw_times)
        return html.Div(listtimes, style={'width': '180', 'height': '200', 'overflow': 'scroll'}, )

    except:
        return ""


if __name__ == '__main__':
    app.run_server(port=8553, debug=True)
    # app.run_server(host='0.0.0.0')

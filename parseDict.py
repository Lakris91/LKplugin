import numpy as np
from livestockFEM_v2 import FEM_frame
import plotly.graph_objs as go
import math
import dash_core_components as dcc
import dash_html_components as html
import timeit

def plotDict(outDict,Plots=['Nodes','Elements','DOFPlot','ForcePlot1','ForcePlot2','ForcePlot3']):
    plotNames={ 'Nodes':'Nodes',
                'Elements':'Elements',
                'DOFPlot':'Deformation',
                'ForcePlot1':'Normal Forces',
                'ForcePlot2':'Shear Forces',
                'ForcePlot3':'Bending Moments'
                }

    plotColors={'Nodes':'rgba(50,50,50,0.7)',
                'Elements':'rgba(50,50,50,0.7)',
                'DOFPlot':'#E0A914',
                'ForcePlot1':'#0F84B5',
                'ForcePlot2':'#64B227',
                'ForcePlot3':'#E50428'
                }

    units={'1':'meter',
            '1000':'millimeter'}
    unitfactor=outDict['UnitScaling']
    scatterPlot=[]
    start = timeit.default_timer()
    #Nodes Plot
    nodes=np.array(outDict['Nodes'])*outDict['UnitScaling']
    minx=np.min(nodes,axis=0)[0]
    maxx=np.max(nodes,axis=0)[0]
    miny=np.min(nodes,axis=0)[1]
    maxy=np.max(nodes,axis=0)[1]

    num=np.arange(len(nodes))
    if 'Nodes' in Plots:
        scatterPlot.append(go.Scatter(x=nodes[:,0],y=nodes[:,1],name=plotNames['Nodes'],mode='markers+text',marker=dict(color=plotColors['Nodes']),text=num,textposition='top center' ))
    #Elements Plots
    if 'Elements' in Plots:
        elenum=[]
        elex=np.array([])
        eley=np.array([])
        for elei,ele in enumerate(outDict['Topology']):
            elenum+=[None,elei,None]
            elex=np.append(elex,np.insert(ele,1,np.average(ele,axis=0),axis=0)[:,0])
            eley=np.append(eley,np.insert(ele,1,np.average(ele,axis=0),axis=0)[:,1])
            if elei != len(outDict['Topology']):
                elenum.append(None)
                elex=np.append(elex,None)
                eley=np.append(eley,None)
        scatterPlot.append(go.Scatter(x=elex,y=eley,name=plotNames['Elements'],line=dict(color=plotColors['Elements'],dash = 'dot'),mode='lines+text',
                    text=np.array(elenum),textposition='top center'))
    #Deformation and forces plots
    for namei,plot in enumerate(Plots):
        if plot == 'Nodes' or plot == 'Elements':
            continue
        plotlist = np.array(outDict[plot])
        forcex=np.array([])
        forcey=np.array([])
        x0=plotlist[:,:,0]
        y0=plotlist[:,:,1]
        minx=min(minx,np.min(x0))
        maxx=max(maxx,np.max(x0))
        miny=min(miny,np.min(y0))
        maxy=max(maxy,np.max(y0))
        #print(bool(namei))
        for i in range(len(x0)):
            if plot =='DOFPlot':
                scatterPlot.append(go.Scatter(x=x0[i],y=y0[i],name=plotNames[plot],line=dict(color=plotColors[plot],width = 2),mode='lines',showlegend=not(bool(i)),visible=True))
                continue
            scatterPlot.append(go.Scatter(x=x0[i],y=y0[i],name=plotNames[plot],line=dict(color=plotColors[plot],width = 1),mode='lines',fill="toself",text = ["Points only"+str(i) for i in range(len(x0[i]))], hoverinfo = 'text',hoveron='points',showlegend=not(bool(i)),visible=True))
    minx=int(math.floor(minx/unitfactor)*unitfactor-unitfactor/2)
    miny=int(math.floor(miny/unitfactor)*unitfactor-unitfactor/2)
    maxx=int(math.ceil(maxx/unitfactor)*unitfactor+unitfactor/2)
    maxy=int(math.ceil(maxy/unitfactor)*unitfactor+unitfactor/2)
    xrange=[minx,maxx]
    yrange=[miny,maxy]
    stop = timeit.default_timer()
    print('Scatter: ', stop - start)
    start = timeit.default_timer()
    femPlot=html.Div([
        dcc.Graph(
            id='FEM-Plot',
            figure={
                'data': scatterPlot,
                'layout': go.Layout(
                    autosize=True,
                    #width=800,
                    #height=800,
                    xaxis={'title': units[str(int(unitfactor))],
                            'range' : xrange,
                            'zeroline':False,
                            'scaleanchor' : 'y',
                            'tickvals':list(range(xrange[0],xrange[1],max(1,int(unitfactor/2))))
                            },
                    yaxis={'title': units[str(int(unitfactor))],
                            'range' : yrange,
                            'zeroline':False,
                            'tickvals':list(range(yrange[0],yrange[1],max(1,int(unitfactor/2))))
                            },
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': -.1,'orientation':'h'},
                    hovermode='closest'
                )
            }
        )
    ])
    stop = timeit.default_timer()
    print('Plot: ', stop - start)
    return femPlot
#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dash import Dash, html, dcc, Input, Output, callback,State
from datetime import date
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# In[2]:


external_stylesheets = [
    dbc.themes.BOOTSTRAP,  # Bootstrap
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css"  # Bootstrap Icons 
]
app = Dash(__name__,external_stylesheets=external_stylesheets)
df = pd.read_csv('data.csv',parse_dates=['Date'])
df.columns = df.columns.str.strip()  


# In[3]:


#Layout design
select_period=dcc.DatePickerRange(
        id='date',min_date_allowed=date(2012, 10, 1),max_date_allowed=date(2015, 8, 27),initial_visible_month=date(2015, 1, 2),
start_date=date(2015, 1, 1),end_date=date(2015, 3, 31),style={"height": "20px"})
text=dcc.Markdown( f"""**Select Period: **""",)
select_period_card = dbc.Card(
    dbc.CardBody(
        dbc.Row([dbc.Col(text, width="auto",style={"margin-top": "20px"}),dbc.Col(select_period, width="auto")],
            align="center",justify="start",className="align-items-center" ),))
select_category1=dcc.Dropdown(['By Product', 'By Region'], 'By Product', id='category-dropdown1')
select_category2=dcc.Dropdown(['By Product', 'By Region'], 'By Product', id='category-dropdown2')
sort_icon_1 = html.I(className="bi bi-arrow-down-up", id="sort-icon-1", style={'cursor': 'pointer'})
sort_icon_2 = html.I(className="bi bi-arrow-down-up", id="sort-icon-2", style={'cursor': 'pointer'})
select_category3=dcc.Dropdown(['Sales by State', 'Profit by State','ARTR by State','ITR by State'], 'Sales by State', id='category-dropdown3')
app.layout = dbc.Container([
    dcc.Store(id='sort-order-1', data='asc'),
    dcc.Store(id='sort-order-2', data='asc'),
    dcc.Store(id="period-selected", data={}),
    dbc.Row(dbc.Col(html.Div(select_period_card),className='mb-2',md=12),style={"height": "10%"}),
    dbc.Row([
    dbc.Col([dbc.Row(html.Div(id='card'),className="mb-3",style={"height": "20%"}),
           dbc.Row([dbc.Col(html.Div(id='line-chart-1'),md=6),dbc.Col(html.Div(id='line-chart-2'),md=6)],className="mb-3",style={"height": "35%"}),
           dbc.Row([dbc.Col([dbc.Row([dbc.Col(sort_icon_1,width=1),dbc.Col(select_category1)])]),
                   dbc.Col([dbc.Row([dbc.Col(sort_icon_2,width=1),dbc.Col(select_category2)])])],className="mb-3",style={"height": "5%"}),
           dbc.Row([dbc.Col(html.Div(id='bar-chart-1'),md=6),dbc.Col(html.Div(id='bar-chart-2'),md=6)],className="mb-3",style={"height": "40%"}),
            ], md=8,style={"height": "90%"}),#left column
    dbc.Col([dbc.Row([html.Div(dbc.Card([dbc.CardHeader(select_category3),dbc.CardBody(dcc.Graph(id='State performance',style={'padding': '0',"height": "100%"}))]))],className="mb-3",style={"height": "30%","overflow": "auto"}),
           dbc.Row([html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='month ARTR',style={'padding': '0'}))],style={'padding': '0', 'margin': '0'}),className="mb-3",style={"height": "30%"})]),
           dbc.Row(html.Div(id='ITR'),className="mb-3",style={"height": "40%","overflow": "auto"})],md=4)
    ],style={"margin": "0","height":"90%"})#right column
],style={"backgroundColor": "lightgray"})


# In[4]:


#Left column design
@callback(
    Output("period-selected", "data"),
    Input("date", "start_date"),
    Input("date", "end_date")
)
def selected_period(start_date,end_date):
    df1 = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    return df1.to_json(date_format='iso', orient='split')

def format_growth_rate(growth_rate):
    color = "green" if growth_rate >= 0 else "red"
    symbol = "+" if growth_rate >= 0 else ""
    return html.Span(f"{symbol}{growth_rate*100:.2f}%", style={"color": color})

@callback(
    Output("card", "children"),
    Input("period-selected", "data")
)
def update_panel(jsonified_cleaned_data):
    df2=pd.read_json(jsonified_cleaned_data,orient='split')
    total_actual_sales=df2['Sales'].sum()
    total_target_sales=df2['Target_sales'].sum()
    growth_rate1=(total_actual_sales-total_target_sales)/total_target_sales #total sales
    total_actual_profit=df2['Profit'].sum()
    total_target_profit=df2['Target_profit'].sum()
    actual_profit_margin=total_actual_profit/total_actual_sales
    target_profit_margin=total_target_profit/total_target_sales
    growth_rate2=(actual_profit_margin-target_profit_margin)/target_profit_margin#profit margin
    total_actual_inventory1=df2['Beginning Inventory'].sum()
    total_actual_inventory2=df2['Ending Inventory'].sum()
    total_actual_cogs=df2['Cogs'].sum()
    actual_inventory_turnover_Ratio=total_actual_cogs/((total_actual_inventory1+total_actual_inventory2)/2)#Inventory Turnover Ratio 
    total_actual_receivable=df2['Closing Balance'].sum()
    actual_ARTR=(total_actual_sales/total_actual_receivable)#Accounts Receivable Turnover Ratio
    symbol1 =  format_growth_rate(growth_rate1)
    symbol2 =  format_growth_rate(growth_rate2)
    style1={"font-size": "12px"}
    style2={"font-size": "15px", "font-weight": "bold"}
    control_panel=dbc.Row([
        dbc.Col([dbc.Row([dbc.Col(dcc.Markdown( f"""Total Sales""",style=style1)),dbc.Col(symbol1)]),
                 dbc.Row(dcc.Markdown( f"""**$**{total_actual_sales:.2f} """,style=style2))]),
        dbc.Col([dbc.Row([dbc.Col(dcc.Markdown( f"""Profit Margin """,style=style1)),dbc.Col(symbol2)]),
                 dbc.Row(dcc.Markdown( f"""{actual_profit_margin*100:.2f}% """,style=style2))]),
        dbc.Col([dbc.Row(dcc.Markdown( f"""Inventory Turnover Ratio""",style=style1)),
                 dbc.Row(dcc.Markdown( f"""{actual_inventory_turnover_Ratio*100:.2f}% """,style=style2))]),
        dbc.Col([dbc.Row(dcc.Markdown( f"""Accounts Receivable Turnover Ratio""",style=style1)),
                 dbc.Row(dcc.Markdown( f"""{actual_ARTR*100:.2f}% """,style=style2))])       
    ])
    card=dbc.Card([dbc.CardBody(control_panel)])
    return card

@callback(
    Output("line-chart-1", "children"),
    Input("period-selected", "data")
)
def update_linechart1(jsonified_cleaned_data):
    df3=pd.read_json(jsonified_cleaned_data,orient='split')
    df3['YearMonth']=df3['Date'].dt.to_period('M')
    df_monthly = df3.groupby('YearMonth').agg({'Sales': 'sum','Target_sales':'sum'}).reset_index()
    df_monthly['YearMonth'] = df_monthly['YearMonth'].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Sales'],mode='lines+markers',name='Sales',
                             line=dict(color="royalblue", width=3),marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Target_sales'],mode='lines+markers',name='Target_sales',
                             line=dict(color="mediumorchid", width=3, dash='dash'),marker=dict(size=8)
    ))
    fig.update_xaxes(showgrid=False,type='category',tickangle=45)  
    fig.update_yaxes(showgrid=True, gridcolor="lightgray", gridwidth=0.5) 
    fig.update_layout(title='Total Sales', plot_bgcolor="white",margin=dict(l=40, r=40, t=80, b=40),height=400,width=350,legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="center", x=0.5))
    card1=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig),style={'padding': '0'})],style={'padding': '0', 'margin': '0'})
    return card1

@callback(
    Output("line-chart-2", "children"),
    Input("period-selected", "data")
)
def update_linechart2(jsonified_cleaned_data):
    df4=pd.read_json(jsonified_cleaned_data,orient='split')
    df4['YearMonth']=df4['Date'].dt.to_period('M')
    df_monthly = df4.groupby('YearMonth').agg({'Profit': 'sum','Target_profit':'sum'}).reset_index()
    df_monthly['YearMonth'] = df_monthly['YearMonth'].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Profit'],mode='lines+markers',name='Profit',
                              line=dict(color="royalblue", width=3),marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Target_profit'],mode='lines+markers',name='Target_profit',
                              line=dict(color="mediumorchid", width=3, dash='dash'),marker=dict(size=8)
    ))
    fig.update_xaxes(showgrid=False,type='category',tickangle=45)  
    fig.update_yaxes(showgrid=True, gridcolor="lightgray", gridwidth=0.5)
    fig.update_layout(title='Profit',plot_bgcolor="white",margin=dict(l=40, r=40, t=80, b=40),height=400,width=350,legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="center", x=0.5))
    card2=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig),style={'padding': '0'})],style={'padding': '0', 'margin': '0'})
    return card2
    
@app.callback(
    Output('sort-order-1', 'data'), 
    Input('sort-icon-1', 'n_clicks'), 
    State('sort-order-1', 'data')  
)
def toggle_sort_order(n_clicks, current_order):
    if n_clicks is None:  
        return current_order
    
    if current_order == 'asc':
        return 'desc'
    else:
        return 'asc'

@callback(
    Output("bar-chart-1", "children"),
    Input("period-selected", "data"),
    Input('category-dropdown1','value'),
    Input('sort-order-1', 'data')
)
def update_barchart1(jsonified_cleaned_data,category_dropdown1,sort_order):
    df5=pd.read_json(jsonified_cleaned_data,orient='split')
    if category_dropdown1=='By Product':
        df_product=df5.groupby('Product').agg({'Sales': 'sum','Target_sales':'sum'}).reset_index()
        df_product = df_product.sort_values('Sales', ascending=(sort_order == 'asc'))
        fig=go.Figure()
        fig.add_trace(go.Bar(x=df_product['Sales'],y=list(range(len(df_product))),name='Actual Sales',orientation='h',
                             hovertemplate="Actual Sales: %{x:,}<extra></extra>"))
        for i in range(len(df_product)):
            fig.add_trace(go.Scatter(x=[df_product['Target_sales'][i], df_product['Target_sales'][i]],y=[i - 0.3, i + 0.3], mode='lines',
                                     line=dict(color='black', width=2),showlegend=False,
                                    hovertemplate="Target Sales: %{x:,}<extra></extra>")) 
        fig.update_layout(yaxis=dict(tickvals=list(range(len(df_product))),ticktext=df_product['Product']))
    else:
         df_region=df5.groupby('State').agg({'Sales': 'sum','Target_sales':'sum'}).reset_index()
         df_region = df_region.sort_values('Sales', ascending=(sort_order == 'asc')) 
         fig=go.Figure()
         fig.add_trace(go.Bar(x=df_region['Sales'],y=list(range(len(df_region))),name='Actual Sales',orientation='h',
                             hovertemplate="Actual Sales: %{x:,}<extra></extra>"))
         for i in range(len(df_region)):
            fig.add_trace(go.Scatter(x=[df_region['Target_sales'][i], df_region['Target_sales'][i]],y=[i - 0.3, i + 0.3], mode='lines',
                                     line=dict(color='black', width=2),showlegend=False,
                                     hovertemplate="Target Sales: %{x:,}<extra></extra>")) 
         fig.update_layout(yaxis=dict(tickvals=list(range(len(df_region))),ticktext=df_region['State']))
    fig.add_shape(type="line", x0=0,x1=1,y0=1, y1=1,xref="paper",yref="paper",line=dict(color="lightgray", width=0.5))
    fig.add_shape(type="line",x0=0,x1=0,y0=0,y1=1,xref="paper",yref="paper",line=dict(color="lightgray", width=0.5))
    fig.update_xaxes(showgrid=True, gridcolor="lightgray", gridwidth=0.5)
    fig.update_yaxes(showgrid=False)  
    fig.update_layout(title='Actual vs Target Sales',xaxis_title="",yaxis_title="",barmode='overlay',bargap=0.3,plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=0, t=30, b=0),height=400,width=350,legend=dict(orientation="h",yanchor="bottom",y=0.97,xanchor="center", x=0.5)) 
    card3=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig,style={'padding': '0'}))],style={'padding': '0', 'margin': '0'})
    return card3
    
@app.callback(
    Output('sort-order-2', 'data'),  
    Input('sort-icon-2', 'n_clicks'),  
    State('sort-order-2', 'data')  
)
def toggle_sort_order(n_clicks, current_order):
    if n_clicks is None: 
        return current_order
    
    if current_order == 'asc':
        return 'desc'
    else:
        return 'asc'

@callback(
    Output("bar-chart-2", "children"),
    Input("period-selected", "data"),
    Input('category-dropdown2','value'),
    Input('sort-order-2', 'data')
)
def update_barchart2(jsonified_cleaned_data,category_dropdown2,sort_order):
    df5=pd.read_json(jsonified_cleaned_data,orient='split')
    if category_dropdown2=='By Product':
        df_product=df5.groupby('Product').agg({'Profit': 'sum','Target_profit':'sum'}).reset_index()
        df_product = df_product.sort_values('Profit', ascending=(sort_order == 'asc'))
        fig=go.Figure()
        fig.add_trace(go.Bar(x=df_product['Profit'],y=list(range(len(df_product))),name='Actual Profit',orientation='h',
                            hovertemplate="Actual Profit: %{x:,}<extra></extra>"))
        for i in range(len(df_product)):
            fig.add_trace(go.Scatter(x=[df_product['Target_profit'][i], df_product['Target_profit'][i]],y=[i - 0.3, i + 0.3], mode='lines',
                                     line=dict(color='black', width=2),showlegend=False,
                                    hovertemplate="Target Profit: %{x:,}<extra></extra>")) 
        fig.update_layout(yaxis=dict(tickvals=list(range(len(df_product))),ticktext=df_product['Product']))
    else:
        df_region=df5.groupby('State').agg({'Profit': 'sum','Target_profit':'sum'}).reset_index()
        df_region = df_region.sort_values('Profit', ascending=(sort_order == 'asc'))
        fig=go.Figure()
        fig.add_trace(go.Bar(x=df_region['Profit'],y=list(range(len(df_region))),name='Actual Profit',orientation='h',
                            hovertemplate="Actual Profit: %{x:,}<extra></extra>"))
        for i in range(len(df_region)):
            fig.add_trace(go.Scatter(x=[df_region['Target_profit'][i], df_region['Target_profit'][i]],y=[i - 0.3, i + 0.3], mode='lines',
                                     line=dict(color='black', width=2),showlegend=False,
                                    hovertemplate="Target Profit: %{x:,}<extra></extra>")) 
        fig.update_layout(yaxis=dict(tickvals=list(range(len(df_region))),ticktext=df_region['State']))
    fig.add_shape(type="line", x0=0,x1=1,y0=1, y1=1,xref="paper",yref="paper",line=dict(color="lightgray", width=0.5))
    fig.add_shape(type="line",x0=0,x1=0,y0=0,y1=1,xref="paper",yref="paper",line=dict(color="lightgray", width=0.5))
    fig.update_xaxes(showgrid=True, gridcolor="lightgray", gridwidth=0.5)
    fig.update_yaxes(showgrid=False) 
    fig.update_layout(title='Actual vs Target Profit',xaxis_title="",yaxis_title="",barmode='overlay',bargap=0.3,plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=0, t=30, b=0),height=400,width=350,legend=dict(orientation="h",yanchor="bottom",y=0.97,xanchor="center", x=0.5))  
    card4=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig,style={'padding': '0'}))],style={'padding': '0', 'margin': '0'})
    return card4
        


# In[5]:


#Right column design
@callback(
    Output("State performance", "figure"),
    Input("period-selected", "data"),
    Input('category-dropdown3','value')
)
def update_map(jsonified_cleaned_data,category_dropdown3):
    df6=pd.read_json(jsonified_cleaned_data,orient='split')
    if category_dropdown3=='Sales by State':
        df_sales=df6.groupby('State').agg({'Sales': 'sum'}).reset_index()
        fig=px.choropleth(df_sales, locations='State',locationmode='USA-states',color='Sales',hover_name='State',hover_data=['Sales'], 
        color_continuous_scale='Viridis')
    elif category_dropdown3=='Profit by State':
        df_profit=df6.groupby('State').agg({'Profit': 'sum'}).reset_index()
        fig=px.choropleth(df_profit, locations='State',locationmode='USA-states',color='Profit',hover_name='State',hover_data=['Profit'], 
        color_continuous_scale='Viridis')
    elif category_dropdown3=='ARTR by State':
        df_ARTR=df6.groupby('State').agg({'Sales': 'sum','Closing Balance':'sum'}).reset_index()
        df_ARTR['State ARTR']=(df_ARTR['Closing Balance']/df_ARTR['Sales'])*28
        fig=px.choropleth(df_ARTR, locations='State',locationmode='USA-states',color='State ARTR',hover_name='State',hover_data=['State ARTR'], 
        color_continuous_scale='Viridis')
    else:
        df_ITR=df6.groupby('State').agg({'Cogs': 'sum','Ending Inventory':'sum','Beginning Inventory':'sum'}).reset_index()
        df_ITR['State ITR']=df_ITR['Cogs']/((df_ITR['Ending Inventory']+df_ITR['Ending Inventory'])/2)
        fig=px.choropleth(df_ITR, locations='State',locationmode='USA-states',color='State ITR',hover_name='State',hover_data=['State ITR'], 
        color_continuous_scale='Viridis')
    fig.update_geos(
    fitbounds="locations",  
    showlakes=True, 
    lakecolor='rgb(255, 255, 255)',
    showcountries=False,
    coastlinecolor="black",
    projection_type="albers usa"  
)
    fig.update_layout(height=350,margin=dict(l=0, r=0, t=0, b=0))
    return fig

@callback(
    Output("month ARTR", "figure"),
    Input("period-selected", "data")
)
def update_month_DSO(jsonified_cleaned_data):
    df7=pd.read_json(jsonified_cleaned_data,orient='split')
    df7['YearMonth']=df7['Date'].dt.to_period('M')
    df7['YearMonth'] = df7['YearMonth'].astype(str)
    df7=df7.groupby('YearMonth').agg({'Sales': 'sum','Closing Balance':'sum'}).reset_index()
    df7['Month ARTR']=df7['Sales']/df7['Closing Balance']
    fig=px.line(df7,x='YearMonth',y='Month ARTR',title='Accounts Receivable Turnover Ratio',markers=True)
    fig.update_xaxes(type='category')
    fig.update_traces(line=dict(color="royalblue", width=3),
                      marker=dict(size=8, color="rgba(255, 165, 0, 0.8)", symbol='circle', line=dict(color="white", width=1)),
                     fill='tozeroy',fillcolor="rgba(173, 216, 230, 0.3)")
    fig.update_layout(plot_bgcolor='white',xaxis_title="",yaxis_title="",height=310,margin=dict(l=40, r=40, t=60, b=60))
    fig.update_xaxes(showgrid=False,tickangle=45)  
    fig.update_yaxes(range=[0.00, 0.1],showgrid=True, gridcolor="lightgray", gridwidth=0.5)
    return fig
    

@callback(
    Output("ITR", "children"),
    Input("period-selected", "data")
)
def update_barchart3(jsonified_cleaned_data):
    df8=pd.read_json(jsonified_cleaned_data,orient='split')
    df8['YearMonth']=df8['Date'].dt.to_period('M')
    df8['YearMonth'] = df8['YearMonth'].astype(str)
    df8=df8.groupby('YearMonth').agg({'Cogs': 'sum','Ending Inventory':'sum','Beginning Inventory':'sum'}).reset_index()
    df8['ITR']=df8['Cogs']/(df8['Ending Inventory']+df8['Beginning Inventory'])
    #df8 = df8.sort_values('ITR', ascending=True)
    fig=px.line(df8,x='YearMonth',y='ITR',title='Inventory Turnover Ratio',markers=True)
    fig.update_xaxes(type='category')
    fig.update_traces(line=dict(color="royalblue", width=3),
                      marker=dict(size=8, color="rgba(255, 165, 0, 0.8)", symbol='circle', line=dict(color="white", width=1)),
                     fill='tozeroy',fillcolor="rgba(173, 216, 230, 0.3)")
    fig.update_layout(plot_bgcolor='white',xaxis_title="",yaxis_title="",height=310,margin=dict(l=40, r=40, t=60, b=60))
    fig.update_xaxes(showgrid=False,tickangle=45) 
    fig.update_yaxes(range=[0, 0.1],showgrid=True, gridcolor="lightgray", gridwidth=0.5)
    card=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig,style={'width': '100%', 'padding': '0', 'margin': '0'}))],style={'padding': '0', 'margin': '0'})
    return card

   


# In[6]:


if __name__ == '__main__':
    app.run(debug=True)


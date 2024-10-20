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
    dbc.themes.BOOTSTRAP,  # Bootstrap 样式表
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css"  # Bootstrap Icons 样式表
]
app = Dash(__name__,external_stylesheets=external_stylesheets)
df = pd.read_csv('Coffee_Chain_Sales_NN.csv',parse_dates=['Date'])
df.columns = df.columns.str.strip()  


# In[3]:


select_period=dcc.DatePickerRange(
        id='date',min_date_allowed=date(2012, 10, 1),max_date_allowed=date(2015, 8, 27),initial_visible_month=date(2015, 1, 2),
start_date=date(2015, 1, 1),end_date=date(2015, 3, 31),style={"height": "20px"})
text=dcc.Markdown( f"""**Select Period: **""",)
select_period_card = dbc.Card(
    dbc.CardBody(
        dbc.Row([dbc.Col(text, width="auto"),dbc.Col(select_period, width="auto")],
            align="center",justify="start",className="align-items-center" ),))
# select_period_card = dbc.Card(
#     dbc.CardBody(dbc.Row([dbc.Col(text,width="auto", style={"padding-right": "0px"}),dbc.Col(select_period,width="auto")],
#                          align="center",justify="start", style={"margin": "0px"})),style={"padding": "10px", "width": "100%"})
select_category1=dcc.Dropdown(['By Product', 'By Region'], 'By Product', id='category-dropdown1')
select_category2=dcc.Dropdown(['By Product', 'By Region'], 'By Product', id='category-dropdown2')
sort_icon_1 = html.I(className="bi bi-arrow-down-up", id="sort-icon-1", style={'cursor': 'pointer'})
sort_icon_2 = html.I(className="bi bi-arrow-down-up", id="sort-icon-2", style={'cursor': 'pointer'})
select_category3=dcc.Dropdown(['Sales by State', 'Profit by State','DSO by State','ITR by State'], 'Sales by State', id='category-dropdown3')
app.layout = dbc.Container([
    dcc.Store(id='sort-order-1', data='asc'),
    dcc.Store(id='sort-order-2', data='asc'),
    dcc.Store(id="period-selected", data={}),
    dbc.Row(dbc.Col(html.Div(select_period_card),className='mb-2',md=12)),
    dbc.Row([
    dbc.Col([dbc.Row(html.Div(id='card'),className="mb-3"),
           dbc.Row([dbc.Col(html.Div(id='line-chart-1'),md=6),dbc.Col(html.Div(id='line-chart-2'),md=6)],className="mb-3"),
           dbc.Row([dbc.Col([dbc.Row([dbc.Col(sort_icon_1,width=1),dbc.Col(select_category1)])]),
                   dbc.Col([dbc.Row([dbc.Col(sort_icon_2,width=1),dbc.Col(select_category2)])])],className="mb-3"),
           dbc.Row([dbc.Col(html.Div(id='bar-chart-1'),md=6),dbc.Col(html.Div(id='bar-chart-2'),md=6)],className="mb-3"),
            ], md=12),#left column
    dbc.Col([dbc.Row([dbc.Card([dbc.CardHeader(select_category3),dbc.CardBody(dcc.Graph(id='State performance'))])],className="mb-3"),
           dbc.Row(dcc.Graph(id='month DSO'),className="mb-3"),
           dbc.Row(html.Div(id='ITR'),className="mb-3")],md=12)
    ],style={"margin": "0"})#right column
],style={"backgroundColor": "lightgray"})


# In[4]:


@callback(
    Output("period-selected", "data"),
    Input("date", "start_date"),
    Input("date", "end_date")
)
def selected_period(start_date,end_date):
    df1 = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    return df1.to_json(date_format='iso', orient='split')

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
    total_actual_inventory=df2['Ending Inventory'].sum()
    total_actual_cogs=df2['Cogs'].sum()
    actual_inventory_turnover=total_actual_cogs/total_actual_inventory#inventory turnover公式期初余额没有，需要调整
    total_actual_receivable=df2['Closing Balance'].sum()
    actual_DSO=(total_actual_receivable/total_actual_sales)*28 #DSO,公式天数有误
    control_panel=dbc.Row([
        dbc.Col([dbc.Row(dcc.Markdown( f"""** Total Sales **{growth_rate1:.2f} """,)),
                 dbc.Row(dcc.Markdown( f"""**$**{total_actual_sales:.2f} """,))]),
        dbc.Col([dbc.Row(dcc.Markdown( f"""** Profit Margin **{growth_rate2:.2f} """,)),
                 dbc.Row(dcc.Markdown( f"""{actual_profit_margin:.2f} """,))]),
        dbc.Col([dbc.Row(dcc.Markdown( f"""** Inventory Turnover **""",)),
                 dbc.Row(dcc.Markdown( f"""{actual_inventory_turnover:.2f} """,))]),
        dbc.Col([dbc.Row(dcc.Markdown( f"""** DSO **""",)),
                 dbc.Row(dcc.Markdown( f"""{actual_DSO:.2f} """,))])       
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
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Sales'],mode='lines+markers',name='Sales',line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Target_sales'],mode='lines+markers',name='Target_sales',line=dict(color='purple')
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),height=400,width=300,legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="center", x=0.5))
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
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Profit'],mode='lines+markers',name='Profit',line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(x=df_monthly['YearMonth'],y=df_monthly['Target_profit'],mode='lines+markers',name='Target_profit',line=dict(color='purple')
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),height=400,width=300,legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="center", x=0.5))
    card2=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig),style={'padding': '0'})],style={'padding': '0', 'margin': '0'})
    return card2
    
@app.callback(
    Output('sort-order-1', 'data'),  # 更新排序状态
    Input('sort-icon-1', 'n_clicks'),  # 点击图标时触发
    State('sort-order-1', 'data')  # 当前排序状态
)
def toggle_sort_order(n_clicks, current_order):
    if n_clicks is None:  # 如果没有点击，保持当前状态
        return current_order
    # 切换排序状态
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
        df_product=df5.groupby('Product').agg({'Sales': 'sum'}).reset_index()
        df_product = df_product.sort_values('Sales', ascending=(sort_order == 'asc')) 
        fig=px.bar(df_product,x='Sales',y='Product',title='Total Sales')
    else:
         df_region=df5.groupby('State').agg({'Sales': 'sum'}).reset_index()
         df_region = df_region.sort_values('Sales', ascending=(sort_order == 'asc'))
         fig=px.bar(df_region,x='Sales',y='State',title='Total Sales')
    fig.update_layout(xaxis_title="",yaxis_title="",margin=dict(l=0, r=0, t=0, b=0),height=400,width=300,legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="center", x=0.5)) 
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
    # 切换排序状态
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
        df_product=df5.groupby('Product').agg({'Profit': 'sum'}).reset_index()
        df_product = df_product.sort_values('Profit', ascending=(sort_order == 'asc'))
        fig=px.bar(df_product,x='Profit',y='Product',title='Profit')
    else:
        df_region=df5.groupby('State').agg({'Profit': 'sum'}).reset_index()
        df_region = df_region.sort_values('Profit', ascending=(sort_order == 'asc'))
        fig=px.bar(df_region,x='Profit',y='State',title='Profit')
    fig.update_layout(xaxis_title="",yaxis_title="",margin=dict(l=0, r=0, t=0, b=0),height=400,width=300,legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="center", x=0.5))  
    card4=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig,style={'padding': '0'}))],style={'padding': '0', 'margin': '0'})
    return card4
        


# In[5]:


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
    elif category_dropdown3=='DSO by State':
        df_DSO=df6.groupby('State').agg({'Sales': 'sum','Closing Balance':'sum'}).reset_index()
        df_DSO['State DSO']=(df_DSO['Closing Balance']/df_DSO['Sales'])*28
        fig=px.choropleth(df_DSO, locations='State',locationmode='USA-states',color='State DSO',hover_name='State',hover_data=['State DSO'], 
        color_continuous_scale='Viridis')
    else:
        df_ITR=df6.groupby('State').agg({'Cogs': 'sum','Ending Inventory':'sum'}).reset_index()
        df_ITR['State ITR']=df_ITR['Cogs']/df_ITR['Ending Inventory']
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
    return fig

@callback(
    Output("month DSO", "figure"),
    Input("period-selected", "data")
)
def update_month_DSO(jsonified_cleaned_data):
    df7=pd.read_json(jsonified_cleaned_data,orient='split')
    df7['YearMonth']=df7['Date'].dt.to_period('M')
    df7['YearMonth'] = df7['YearMonth'].astype(str)
    df7=df7.groupby('YearMonth').agg({'Sales': 'sum','Closing Balance':'sum'}).reset_index()
    df7['Month DSO']=(df7['Closing Balance']/df7['Sales'])*28
    fig=px.line(df7,x='YearMonth',y='Month DSO',title='Days Sales Outstanding(DSO)')
    fig.update_layout(xaxis_title="",yaxis_title="",height=400)
    return fig

@callback(
    Output("ITR", "children"),
    Input("period-selected", "data")
)
def update_barchart2(jsonified_cleaned_data):
    df8=pd.read_json(jsonified_cleaned_data,orient='split')
    df8=df8.groupby('Product').agg({'Cogs': 'sum','Ending Inventory':'sum'}).reset_index()
    df8['ITR']=df8['Cogs']/df8['Ending Inventory']
    df8 = df8.sort_values('ITR', ascending=True)
    fig=px.bar(df8,x='ITR',y='Product',title='Inventory Turnover Rate')
    card=dbc.Card([dbc.CardBody(dcc.Graph(figure=fig,style={'height': '100%', 'width': '100%', 'padding': '0', 'margin': '0'}))],style={'padding': '0', 'margin': '0'})
    return card

   


# In[6]:


if __name__ == '__main__':
    app.run(debug=True)


from dash import Dash, html, dcc, Input, Output

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import pandas as pd

# external_scripts = [


#     {
#         'src':"https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js",
#         'integrity':"sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4",
#         'crossorigin':"anonymous"
#     }
# ]

# external CSS stylesheets
external_stylesheets = [
    {
        'href': "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css",
        'rel': 'stylesheet',
        'integrity': "sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65",
        'crossorigin': "anonymous"
    },
    'style.css'

]


app = Dash(__name__,
           external_stylesheets=external_stylesheets)

server = app.server


def success(outcome):
    if outcome == "Success":
        return 1
    else:
        return 0


def failure(outcome):
    if outcome == "Failure":
        return 1
    else:
        return 0


# print(df.Date.dt.day)
df = pd.read_excel("dashboard.xlsx")

df["Success"] = df.Outcome.apply(success)
df["Failure"] = df.Outcome.apply(failure)

states = df.State.unique().tolist()
# print(states)

outcomes = df.Outcome.unique().tolist()
# print(outcomes)
dates = df.Date
# print(dates)

fdate = dates.max()

sdate = dates.min()
# print(sdate)
# print(fdate)


def filter_data(outcome="all", state="all", stdate=sdate, eddate=fdate):
    global df
    global number_of_calls
    global number_of_success_calls
    global number_of_failure_calls
    global ratio_success_overall
    global failed_success_timeout
    global number_of_calls_by_state
    global number_of_calls_by_state_success
    global number_of_calls_by_state_ratio
    global success_time_out

    df = pd.read_excel("dashboard.xlsx")

    df["Success"] = df.Outcome.apply(success)
    df["Failure"] = df.Outcome.apply(failure)

    if outcome == "all" and state == "all":
        # print('1 outcome == "all" and state == "all"')
        # print(df.Date >= stdate )
        # print(df.Date)
        df = df[(df.Date >= stdate) & (df.Date <= eddate)]
        # print(df.Date)
    elif outcome == "all":
        # print('2 outcome == "all"')
        df = df[(df.Date >= stdate) & (df.Date <= eddate)]
        df = df[df.State.isin(state)]
        # print(df.head())
    elif state == "all":
        # print('state == "all"')

        df = df[(df.Date >= stdate) & (df.Date <= eddate)]
        df = df[df.Outcome.isin(outcome)]

    else:
        # print('all have values"')
        df = df[(df.Date >= stdate) & (df.Date <= eddate)]
        df = df[df.Outcome.isin(outcome)]
        df = df[df.State.isin(state)]
        # print(df.head())

    # print(df.head())
    number_of_calls = df.groupby("Date")["Country"].count()
    number_of_success_calls = df.groupby("Date")["Success"].sum()
    number_of_failure_calls = df.groupby("Date")["Failure"].sum()

    ratio_success_overall = number_of_success_calls / number_of_calls * 100

    failed_success_timeout = df.groupby("Outcome")["Outcome"].count()

    number_of_calls_by_state = df.groupby("State")["Success"].count()
    number_of_calls_by_state_success = df.groupby("State")["Success"].sum()

    number_of_calls_by_state_ratio = (
        number_of_calls_by_state_success / number_of_calls_by_state * 100).sort_values(ascending=False)

    success_time_out = df[df["Success"] == 1].groupby(
        "Time_Period")["Success"].count().sort_index()


app.layout = html.Div(className="bg-danger", children=[
    html.Div([
        html.Div("Dashboar of calls",
                className="shadow p-3  bg-body rounded text-center",style= {
                    'font-size':'40px'
                }
                )
    ],
    style= { 
        'padding-top':'30px',
        'padding-bottom':'30px',
        'width':"90%",
        'margin':'auto'
    }),

    html.Div([

        html.Div([

            html.Div([
                html.P("Select an exercise:"),
                dcc.Dropdown([
                    {'label': 'Question 1', 'value': 'q1'},
                    {'label': 'Question 2', 'value': 'q2'},
                    {'label': 'Question 3', 'value': 'q3'},
                    {'label': 'Question 4', 'value': 'q4'},
                    {'label': 'Question 5', 'value': 'q5'}],
                    value='q1',
                    id="input",
                    className="qu"
                ),
            ]),
            html.Div([
                html.P("Select date range:"),

                dcc.DatePickerRange(
                    # month_format='M-D-Y-Q',
                    end_date_placeholder_text='M-D-Y-Q',
                    id="input3",
                    start_date=sdate,
                    end_date=fdate,
                    min_date_allowed=sdate,
                    max_date_allowed=fdate,
                    className="li"
                ),
            ]),

            html.Div([
                html.P("Select a state:"),

                dcc.Dropdown(states,
                             multi=True,
                             value='all',
                             placeholder="All",
                             id="input1"
                             ),
            ]),


            


            html.Div([
                html.P("Select outcomes:"),
                dcc.Checklist(outcomes,
                              # value = 'all',
                              id="input2"
                              ),
            ]),

        ]),

        html.Div(
            dcc.Graph(id="output",)
        )
    ], className="d-flex justify-content-between",
    style={
        'width':'90%',
        'margin':'auto',
        'padding-bottom': '40px'
        
    }),

],
    style={
        # 'margin-bottom': '20px'
}
)


@app.callback(
    Output('output', 'figure'),
    Input('input', 'value'),
    Input('input1', 'value'),
    Input('input2', 'value'),
    Input('input3', 'start_date'),
    Input('input3', 'end_date'),
)
def update_output(value, value1, value2, start_date, end_date):
    # print("________")
    # print("start date: " + str(start_date))
    # print("end date: " +str(end_date))

    # print("start date: " + str(type(start_date)))
    # print("end date: " +str(type(end_date)))

    # print("________")
    # print(value2)
    # print("________")

    if value2 == None or len(value2) == 0:
        value2 = "all"

    if len(value1) == 0:
        value1 = "all"

    filter_data(value2, value1, start_date, end_date)
    if value == "q1":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=number_of_calls.index, y=number_of_calls.values,
                                 mode='lines+markers',
                                 name='Overall calls '))
        fig.add_trace(go.Scatter(x=number_of_success_calls.index, y=number_of_success_calls.values,
                                 mode='lines+markers',
                                 name='Number of successful calls'))
        fig.add_trace(go.Scatter(x=number_of_failure_calls.index, y=number_of_failure_calls.values,
                                 mode='lines+markers',
                                 name='Number of failed calls'))
        fig.add_trace(go.Scatter(x=ratio_success_overall.index, y=ratio_success_overall.values,
                                 mode='lines+markers',
                                 name='Ratio of successful calls to overall'))
        fig["layout"]["title"] = "Time series and ratio of successful calls"
        fig["layout"]["xaxis"]["title"] = "Date"
        fig["layout"]["yaxis"]["title"] = "Number of calls or ratio"
        fig["layout"]["legend_title"] = "Options"
        return fig

    if value == "q2":
        fig1 = go.Figure()

        fig1.add_trace(go.Bar(x=number_of_success_calls.index, y=number_of_success_calls.values,
                              name='Number of successful calls'))

        fig1.add_trace(go.Bar(x=number_of_failure_calls.index, y=number_of_failure_calls.values,
                              name='Number of failed calls'))

        fig1["layout"]["title"] = "Failed/successful calls"
        fig1["layout"]["xaxis"]["title"] = "Date"
        fig1["layout"]["yaxis"]["title"] = "Number of calls"
        fig1["layout"]["legend_title"] = "Options"
        return fig1

    if value == "q3":

        fig2 = go.Figure(data=[go.Pie(
            labels=failed_success_timeout.index, values=failed_success_timeout.values)])
        fig2["layout"]["title"] = "Failure/Success/Timeout"
        fig2["layout"]["legend_title"] = "Call outcome"

        return fig2

    if value == "q4":

        fig3 = go.Figure()

        fig3.add_trace(go.Bar(x=number_of_calls_by_state_ratio.index, y=number_of_calls_by_state_ratio.values,
                              name='Number of successful calls'))
        fig3["layout"]["title"] = "Most successfull state by success call"
        fig3["layout"]["xaxis"]["title"] = "Date"
        fig3["layout"]["yaxis"]["title"] = "Ratio of success"
        fig3["layout"]["legend_title"] = "Options"
        return fig3

    if value == "q5":
        fig4 = make_subplots(rows=1, cols=2,
                             column_widths=[0.5, 0.5], specs=[[{"type": "pie"}, {"type": "pie"}]],
                             subplot_titles=("Calls per state", "successfull calls per state"))
        fig4.add_trace(row=1, col=1,
                       trace=go.Pie(labels=number_of_calls_by_state.index, values=number_of_calls_by_state.values,))
        fig4.add_trace(row=1, col=2,
                       trace=go.Pie(labels=number_of_calls_by_state_success.index, values=number_of_calls_by_state_success.values,))

        return fig4

    if value == "q6":
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(x=success_time_out.index, y=success_time_out.values,
                              name='Number of successful calls'))
        return fig5


if __name__ == "__main__":
    app.run_server(debug=False)

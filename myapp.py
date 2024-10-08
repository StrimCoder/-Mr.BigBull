import urllib
import xlrd
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import seaborn as sns
import plotly.graph_objs as go
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
import matplotlib.pyplot as plt
plt.style.use('bmh')
import sqlite3
conn=sqlite3.connect('Data.db')
c=conn.cursor()
import quandl
import matplotlib.animation as ani
import altair as alt

########################################################################################################################

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def remove_all_user(username, password):
    c.execute('DELETE FROM userstable', )
    conn.commit()


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


def main():
    """Login App"""
    # st.title("Login App")
    menu = ["Home", "Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        readme_text = st.markdown(get_file_content_as_string("README.md"))
        # st.subheader("Home")
    elif choice == "Login":
        # st.subheader("Login Section")
        readme_text = st.markdown(get_file_content_as_string("README.md"))
        # name = st.sidebar.text_input("Name")
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login") or (password == '1234' and username == 'sayak'):
            # if password=='1234' and username=='sayak':
            create_usertable()
            result = 0
            result = login_user(username, password)
            readme_text.empty()
            st.success("Logged In As {}".format(username))
            mainfunc()
            if result:
                if username[-1] == '@':
                    st.success("Logged In As {}".format(username))
                    task = st.selectbox("Task", ["Home", 'Help', 'Profile'])
                    if task == "Home":
                        st.subheader("Welcome to Home")
                    elif task == "Help":
                        st.subheader("Help")
                    elif task == 'Profile':
                        st.subheader("User Profiles")
                        user_result = view_all_users()
                        clean_db = pd.DataFrame(user_result, columns=['Username', 'Password'])
                        st.dataframe(clean_db)

                else:
                    st.success("Logged In As {}".format(username))
                    mainfunc()
                    # task = st.selectbox("Task", ["Home", 'Help'])
                    # if task == "Home":
                    #     mainfunc()
                    # elif task == "Help":
                    #     st.subheader("Help")

        else:
            st.warning(" Incorrect Username or Password")

    elif choice == "Signup":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        new_con_password = st.text_input("Confirm Password", type='password')
        # if new_passowrd.isnull():
        #  st.warning("enter password")
        # if new_con_passowrd.isnull():
        # st.warning("enter Confirm Password")
        if st.button("Signup"):
            if (new_password == new_con_password):
                create_usertable()
                add_userdata(new_user, new_password)
                st.success("You Have Successfully Created an Account")
                st.info("Go to Login Menu to Login")
            else:
                st.warning("Password and Confirm Password Don't match")


#########################################################################################################
def mainfunc():

    st.sidebar.header("What To Do")
    app_mode = st.selectbox("Select the app mode", ["Home", "Data Analysis", "Prediction", "Show the Code"])

    if app_mode == "Home":
        st.success("Select Data Analysis or prediction to move on")
        readme_text = st.markdown(get_file_content_as_string("README.md"))
    elif app_mode == "Data Analysis":
        # readme_text.empty()
        data_analysis()
    elif app_mode == "Prediction":
        # readme_text.empty()
        prediction()
    elif app_mode == "Show the Code":
        # readme_text.empty()
        st.code(get_file_content_as_string("myapp.py"))

#####################################################################################################################

companies = {}
xls = xlrd.open_workbook("cname.xls")
sh = xls.sheet_by_index(0)
for i in range(505):
    cell_value_class = sh.cell(i, 0).value
    cell_value_id = sh.cell(i, 1).value
    companies[cell_value_class] = cell_value_id

############################################################################

def company_name():
    company = st.sidebar.selectbox("Companies", list(companies.keys()), 0)
    return company
# company = company_name()

############################################################################

def show_data():
    show = st.sidebar.selectbox("Options", ["Graphs", "Company Data"], 0)
    return show
# show_data = show_data()

############################################################################

def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/Lakshya-Ag/Streamlit-Dashboard/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

############################################################################
@st.cache(suppress_st_warning=True)
def prediction_graph(algo, confidence, cdata):
    st.header(algo + ', Confidence score is ' + str(round(confidence, 2)))
    fig6 = go.Figure(data=[go.Scatter(x=list(cdata.index), y=list(cdata.Close), name='Close'),
                           # go.Scatter(x=list(chart_data.index), y=list(chart_data.Vclose), name='Vclose'),
                           go.Scatter(x=list(cdata.index), y=list(cdata.Vpredictions),
                                      name='Predictions')])

    fig6.update_layout(width=850, height=550)
    fig6.update_xaxes(rangeslider_visible=True,
                      rangeselector=dict(
                          buttons=list([
                              dict(count=30, label="30D", step="day", stepmode="backward"),
                              dict(count=60, label="60D", step="day", stepmode="backward"),
                              dict(count=90, label="90D", step="day", stepmode="backward"),
                              dict(count=120, label="120D", step="day", stepmode="backward"),
                              dict(count=150, label="150D", step="day", stepmode="backward"),
                              dict(step="all")
                          ])
                      ))
    st.plotly_chart(fig6)

#############################################################################

def data_analysis():
    company = company_name()
    def data_download():
        data = yf.download(tickers=companies[company], period='180d', interval='1d')

        def divide(j):
            j = j / 1000000
            return j

        data['Volume'] = data['Volume'].apply(divide)
        data.rename(columns={'Volume': 'Volume (in millions)'}, inplace=True)
        return data
    data = data_download()
    show = show_data()
    df1 = data

    if show == "Graphs":
        st.header('Visualization for ' + company)
        ma = st.slider('Slide to select days for Moving Average', min_value=5, max_value=100)
        df1['MA'] = df1.Close.rolling(ma).mean()

        fig = go.Figure(data=[go.Candlestick(x=df1.index,
                                     open=df1['Open'],
                                     high=df1['High'],
                                     low=df1['Low'],
                                     close=df1['Close'],
                                     name='Market Data'),
                      go.Scatter(x=list(df1.index), y=list(df1.MA), line=dict(color='blue', width=2), name='Moving Average')])

        fig.update_layout(
            title='Live share price evolution',
            yaxis_title='Stock Price (USD per shares)', width=850, height=550)

        fig.update_xaxes(rangeslider_visible=True,
                         rangeselector=dict(
                             buttons=list([
                                 dict(count=30, label="30D", step="day", stepmode="backward"),
                                 dict(count=60, label="60D", step="day", stepmode="backward"),
                                 dict(count=90, label="90D", step="day", stepmode="backward"),
                                 dict(count=120, label="120D", step="day", stepmode="backward"),
                                 dict(count=150, label="150D", step="day", stepmode="backward"),
                                 dict(step="all")
                             ])
                         ))
        st.plotly_chart(fig)

        # ma = st.slider('Slide to select days for Moving Average', min_value=5, max_value=100)
        # df1 = yf.download(tickers=companies[company], period='1460d', interval='1d')
        # df1['MA'] = df1.Close.rolling(ma).mean()
        # fig0 = go.Figure()
        # fig0.add_trace(go.Scatter(x=list(df1.index), y=list(df1.MA)))
        # fig0.update_layout(title_text="Volume of the stock in millions")
        # fig0.update_xaxes(rangeslider_visible=True)
        # st.plotly_chart(fig0)

        st.markdown("### Volume of the stocks")
        st.markdown("Trading volume is a measure of how much of a given financial asset has traded in a period of "
                    "time. For stocks, volume is measured in the number of shares traded and, for futures and options, "
                    "it is based on how many contracts have changed hands.")

        # fig1 = go.Figure()
        # fig1.add_trace(go.Scatter(x=list(data.index), y=list(data['Volume (in millions)'])))

        fig1 = go.Figure([go.Bar(x=data.index, y=data['Volume (in millions)'])])
        fig1.update_layout(title_text="Volume of the stock in millions", width=850, height=550)
        fig1.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(
                              buttons=list([
                                  dict(count=30, label="30D", step="day", stepmode="backward"),
                                  dict(count=60, label="60D", step="day", stepmode="backward"),
                                  dict(count=90, label="90D", step="day", stepmode="backward"),
                                  dict(count=120, label="120D", step="day", stepmode="backward"),
                                  dict(count=150, label="150D", step="day", stepmode="backward"),
                                  dict(step="all")
                              ])
                          ))

        st.plotly_chart(fig1)
        st.markdown("### Opening prices of the stock")
        st.markdown("The opening price is the price at which a security first trades upon the opening of an exchange "
                    "on a trading day; for example, the National Stock Exchange (NSE) opens at precisely 9:00 a.m. "
                    "Eastern time. The price of the first trade for any listed stock is its daily opening price. The "
                    "opening price is an important marker for that day's trading activity, particularly for those "
                    "interested in measuring short-term results such as day traders.")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=list(data.index), y=list(data.Open)))
        fig2.update_layout(title_text="Opening price of the stock", width=850, height=550)
        fig2.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(
                              buttons=list([
                                  dict(count=30, label="30D", step="day", stepmode="backward"),
                                  dict(count=60, label="60D", step="day", stepmode="backward"),
                                  dict(count=90, label="90D", step="day", stepmode="backward"),
                                  dict(count=120, label="120D", step="day", stepmode="backward"),
                                  dict(count=150, label="150D", step="day", stepmode="backward"),
                                  dict(step="all")
                              ])
                          ))

        st.plotly_chart(fig2)

        st.markdown("### High price for the stock")
        st.markdown("Today's high refers to a company's intraday high trading price. Today's high is the highest "
                    "price at which a stock traded during the course of the trading day. Today's high is typically "
                    "higher than the closing or opening price. More often than not this is higher than the closing "
                    "price.")

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=list(data.index), y=list(data.High)))
        fig3.update_layout(title_text="High price of the stock", width=850, height=550)
        fig3.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(
                              buttons=list([
                                  dict(count=30, label="30D", step="day", stepmode="backward"),
                                  dict(count=60, label="60D", step="day", stepmode="backward"),
                                  dict(count=90, label="90D", step="day", stepmode="backward"),
                                  dict(count=120, label="120D", step="day", stepmode="backward"),
                                  dict(count=150, label="150D", step="day", stepmode="backward"),
                                  dict(step="all")
                              ])
                          ))

        st.plotly_chart(fig3)

        st.markdown("### Lowest price for the stock")
        st.markdown("Today’s low is a security's intraday low trading price. Today's low is the lowest price at which a"
                    " stock trades over the course of a trading day. Today's low is typically lower than the opening or"
                    " closing price, as it is unusual that the lowest price of the day would happen to occur at those "
                    "particular moments.")

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=list(data.index), y=list(data.Low)))
        fig4.update_layout(title_text="Low price of the stock", width=850, height=550)
        fig4.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(
                              buttons=list([
                                  dict(count=30, label="30D", step="day", stepmode="backward"),
                                  dict(count=60, label="60D", step="day", stepmode="backward"),
                                  dict(count=90, label="90D", step="day", stepmode="backward"),
                                  dict(count=120, label="120D", step="day", stepmode="backward"),
                                  dict(count=150, label="150D", step="day", stepmode="backward"),
                                  dict(step="all")
                              ])
                          ))

        st.plotly_chart(fig4)

        st.markdown("### Closing price of the stock")
        st.markdown("The closing price of a stock is the price at which the share closes at the end of trading hours "
                    "of the stock market. In simple terms, the closing price is the weighted average of all prices "
                    "during the last 30 minutes of the trading hours.")

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=list(data.index), y=list(data.Close)))
        fig5.update_layout(title_text="Closing price of the stock", width=850, height=550)
        fig5.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(
                              buttons=list([
                                  dict(count=30, label="30D", step="day", stepmode="backward"),
                                  dict(count=60, label="60D", step="day", stepmode="backward"),
                                  dict(count=90, label="90D", step="day", stepmode="backward"),
                                  dict(count=120, label="120D", step="day", stepmode="backward"),
                                  dict(count=150, label="150D", step="day", stepmode="backward"),
                                  dict(step="all")
                              ])
                          ))

        st.plotly_chart(fig5)

######################################################################################

    elif show == "Company Data":
        symbolticker = companies[company]
        dataticker = yf.Ticker(symbolticker)
        st.header('Information of company ' + company)
        st.markdown(dataticker.info)
        st.markdown("### Stock Price Data")
        st.dataframe(data)
        st.markdown("### International Securities Identification Number")
        st.markdown(dataticker.isin)
        # st.markdown("### Sustainability")
        st.dataframe(dataticker.sustainability)
        st.markdown("### Major Holders")
        st.dataframe(dataticker.major_holders)
        st.markdown("### Institutional Holders")
        st.dataframe(dataticker.institutional_holders)
        st.markdown("### Calendar")
        st.dataframe(dataticker.calendar)
        st.markdown("### Recommendations")
        st.dataframe(dataticker.recommendations)

###################################################################################

def prediction():
    def data_download():
        company = company_name()
        data = yf.download(tickers=companies[company], period='200d', interval='1d')

        def divide(j):
            j = j / 1000000
            return j

        data['Volume'] = data['Volume'].apply(divide)
        data.rename(columns={'Volume': 'Volume (in millions)'}, inplace=True)
        return data
    df = data_download()
    
    pred = st.sidebar.radio("Regression Type", ["Tree Prediction", "Linear Regression", "SVR Prediction",
                                                "RBF Prediction", "Polynomial Prediction", "Linear Regression 2"])

    # removing index which is date
    df['Date'] = df.index
    df.reset_index(drop=True, inplace=True)

    # rearranging the columns
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume (in millions)']]
    df['Close'] = scaler.fit_transform(df[['Close']])
    df = df[['Close']]

    # create a variable to predict 'x' days out into the future
    future_days = 50
    # create a new column( target) shifted 'x' units/days up
    df['Prediction'] = df[['Close']].shift(-future_days)

    # create the feature data set (x) and convet it to a numpy array and remove the last 'x' rows
    x = np.array(df.drop(['Prediction'], 1))[:-future_days]

    # create a new target dataset (y) and convert it to a numpy array and get all of the target values except the last'x' rows)
    y = np.array(df['Prediction'])[:-future_days]

    # split the data into 75% training and 25% testing
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

    # create the models
    # create the decision treee regressor model
    tree = DecisionTreeRegressor().fit(x_train, y_train)
    # create the linear regression model
    lr = LinearRegression().fit(x_train, y_train)

    # create the svr model
    svr_rbf = SVR(C=1e3, gamma=.1)
    svr_rbf.fit(x_train, y_train)

    # create the RBF model
    rbf_svr = SVR(kernel='rbf', C=1000.0, gamma=.85)
    rbf_svr.fit(x_train, y_train)

    # Create the polyomial model
    poly_svr = SVR(kernel='poly', C=1000.0, degree=2)
    poly_svr.fit(x_train, y_train)

    # create the linear 2 model
    lin_svr = SVR(kernel='linear', C=1000.0, gamma=.85)
    lin_svr.fit(x_train, y_train)

    # get the last x rows of the feature dataset
    x_future = df.drop(['Prediction'], 1)[:-future_days]
    x_future = x_future.tail(future_days)
    x_future = np.array(x_future)

    # show the model tree prediction
    tree_prediction = tree.predict(x_future)

    # show the model linear regression prediction
    lr_prediction = lr.predict(x_future)

    # show the model SVR prediction
    SVR_prediction = svr_rbf.predict(x_future)

    # show the model RBF prediction
    RBF_prediction = rbf_svr.predict(x_future)

    # show the model Polynomial prediction
    poly_prediction = poly_svr.predict(x_future)

    ##show thw model linear regression2 prediction
    lr2_prediction = lin_svr.predict(x_future)

    if pred == "Linear Regression":
        predictions = lr_prediction
        valid = df[x.shape[0]:]
        valid['predictions'] = predictions

        # alter
        data = {'Close': [], 'Vclose': [], 'Vpredictions': []}
        mod = pd.DataFrame(data)
        mod.set_index = 'index'
        mod.Close = df.Close
        # mod.Vclose = df.Close.loc[:747]
        # mod.Vpredictions = df.Close.loc[:747]
        # mod.Vclose.loc[148:] = valid.Close
        mod.Vpredictions.loc[148:] = valid.predictions
        # mod.Close = df.Close.loc[:150]
        chart_data = mod
        lin_confidence = lr.score(x_test, y_test)
        prediction_graph(pred, lin_confidence, chart_data)

    elif pred == "Tree Prediction":
        predictions = tree_prediction
        valid = df[x.shape[0]:]
        valid['predictions'] = predictions

        # alter
        data = {'Close': [], 'Vclose': [], 'Vpredictions': []}
        mod = pd.DataFrame(data)
        mod.set_index = 'index'
        mod.Close = df.Close

        # mod.Vclose = df.Close.loc[:747]
        # mod.Vpredictions = df.Close.loc[:747]

        # mod.Vclose.loc[148:] = valid.Close
        mod.Vpredictions.loc[148:] = valid.predictions
        # mod.Close = df.Close.loc[:150]
        chart_data = mod
        tree_confidence = tree.score(x_test, y_test)
        prediction_graph(pred, tree_confidence, chart_data)

    elif pred == "SVR Prediction":
        predictions = SVR_prediction
        valid = df[x.shape[0]:]
        valid['predictions'] = predictions

        # alter
        data = {'Close': [], 'Vclose': [], 'Vpredictions': []}
        mod = pd.DataFrame(data)
        mod.set_index = 'index'
        mod.Close = df.Close

        # mod.Vclose = df.Close.loc[:747]
        # mod.Vpredictions = df.Close.loc[:747]

        # mod.Vclose.loc[148:] = valid.Close
        mod.Vpredictions.loc[148:] = valid.predictions
        # mod.Close = df.Close.loc[:150]
        chart_data = mod
        svr_confidence = svr_rbf.score(x_test, y_test)
        prediction_graph(pred, svr_confidence, chart_data)

    elif pred == "RBF Prediction":
        predictions = RBF_prediction
        valid = df[x.shape[0]:]
        valid['predictions'] = predictions

        # alter
        data = {'Close': [], 'Vclose': [], 'Vpredictions': []}
        mod = pd.DataFrame(data)
        mod.set_index = 'index'
        mod.Close = df.Close

        # mod.Vclose = df.Close.loc[:747]
        # mod.Vpredictions = df.Close.loc[:747]

        # mod.Vclose.loc[148:] = valid.Close
        mod.Vpredictions.loc[148:] = valid.predictions
        # mod.Close = df.Close.loc[:150]
        chart_data = mod
        rbf_confidence = rbf_svr.score(x_test, y_test)
        prediction_graph(pred, rbf_confidence, chart_data)

    elif pred == "Polynomial Prediction":
        predictions = poly_prediction
        valid = df[x.shape[0]:]
        valid['predictions'] = predictions

        # alter
        data = {'Close': [], 'Vclose': [], 'Vpredictions': []}
        mod = pd.DataFrame(data)
        mod.set_index = 'index'
        mod.Close = df.Close

        # mod.Vclose = df.Close.loc[:747]
        # mod.Vpredictions = df.Close.loc[:747]

        # mod.Vclose.loc[148:] = valid.Close
        mod.Vpredictions.loc[148:] = valid.predictions
        # mod.Close = df.Close.loc[:150]
        chart_data = mod
        poly_confidence = poly_svr.score(x_test, y_test)

    elif pred == "Linear Regression 2":
        predictions = lr2_prediction
        valid = df[x.shape[0]:]
        valid['predictions'] = predictions

        # alter
        data = {'Close': [], 'Vclose': [], 'Vpredictions': []}
        mod = pd.DataFrame(data)
        mod.set_index = 'index'
        mod.Close = df.Close

        # mod.Vclose = df.Close.loc[:747]
        # mod.Vpredictions = df.Close.loc[:747]

        # mod.Vclose.loc[148:] = valid.Close
        mod.Vpredictions.loc[148:] = valid.predictions
        # mod.Close = df.Close.loc[:150]
        chart_data = mod
        linsvr_confidence = lin_svr.score(x_test, y_test)
        prediction_graph(pred, linsvr_confidence, chart_data)

##################################################################################

if __name__ == "__main__":
    main()

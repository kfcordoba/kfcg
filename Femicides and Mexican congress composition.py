#Katia Fernanda Cordoba Garcia


import os
import pandas as pd
import bokeh
from bokeh.plotting import figure, show
from bokeh.layouts import gridplot
import numpy as np
from ipywidgets import interact, interact_manual
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm



os.path
os.chdir('/Users/katiacordoba/Documents/GitHub/final-project-katia-cordoba-final-project')
os.path.abspath(os.getcwd())


def get_congress_dfs():
    csv_filelist = ['Escanios.csv', 'EscaniosNacionalYEstatal.csv', 'Local congress 2015-2018.csv', 'Mujeres_Diputadas.csv', 'Mujeres_senadoras.csv']    
    dfs = []
    for file in csv_filelist:
        df = pd.read_csv(file, encoding='latin-1')
        dfs.append(df)
    for df in dfs:
        df.columns=df.columns.str.replace('[' ',ï,»,¿]','') 
    return dfs


def rename_col():
        for df in dfs:
            df.rename(columns={"Entidad": "Entity", "Año": "Year", "Mujeres": "Women", "Hombres": "Men", "Estado": "Entity", "Fecha": "Year", "Senadores": "Men", "Senadoras": "Women", "%_mujeres": "%_Women", "%_hombres": "%_Men"}, inplace = True)
        for df in dfs:
            if df.shape[0] == 32:
                df.rename(columns={df.columns[4]: "Men"}, inplace = True)
        return df


def get_percentage():
        for df in dfs:
            df["Total"] = df["Women"] + df["Men"]
            df['%_Women'] = df['Women']/df['Total']*100
            df['%_Men'] = df['Men']/df['Total']*100
        return dfs


def merge_statedfs(): 
    frames = []
    for df in dfs:
        if df.shape[0] > 20:
            frames.append(df)
    state_dfs = pd.concat(frames, ignore_index = True)
    state_dfs = state_dfs[state_dfs.Entity != "Nacional"] 
    state_dfs.loc[:, 'Entity'] =  state_dfs['Entity'].str.strip()
    state_dfs['Entity'] = state_dfs['Entity'].replace(['Distrito Federal','MÃ©xico', 'MichoacÃ¡n', 
       'Nuevo LeÃ³n','QuerÃ©taro','San Luis PotosÃ\xad','YucatÃ¡n','Ciudad De México', 'Coahuila De Zaragoza','Estado De México',
       'Michoacán', 'Nuevo León', 'Querétaro', 'San Luis Potosí',
       'Yucatán'], ['Ciudad de Mexico','Estado de Mexico', 'Michoacan', 'Nuevo Leon', 'Queretaro', 'San Luis Potosi', 'Yucatan', 
        'Ciudad de Mexico', 'Coahuila', 'Estado de Mexico', 'Michoacan', 'Nuevo Leon', 'Queretaro', 'San Luis Potosi', 'Yucatan'])
    state_dfs = state_dfs.sort_values(by='Year', ascending=True)
    return state_dfs



def get_femicides_df():
    femicides = pd.read_csv('Tasa_bruta_homicidio.csv', encoding='latin-1')
    femicides = femicides.rename(columns={'Entidad': "Entity", "Fecha": "Year", "Tasa por cada cien mil mujeres": "Rate per 100K Women"})
    femicides.rename(columns={femicides.columns[0]: "Entity"}, inplace = True)
    femicides = femicides[femicides['Year'] >= 2003]
    return femicides


dfs = get_congress_dfs()
rename_col()
get_percentage()
merge_statedfs()
state_df = merge_statedfs()
femicides = get_femicides_df()
deputies = dfs[3]
senators = dfs[4]



def femicides_plot():
    femicides_national = femicides[femicides.Entity == "Nacional"]
    femicides_national.plot(x= "Year", y="Rate per 100K Women", kind="line", title='Femicides in Mexico')


def congress_plots():
    fig, (ax1,ax2) = plt.subplots(1,2, figsize=(10,4))  # 1 row, 2 columns
    deputies.plot(x= "Year", y=["%_Women", "%_Men"], kind="bar", stacked=True, title='Gender composition Deputies', ax=ax1)
    senators.plot(x= "Year", y=["%_Women", "%_Men"], kind="bar", stacked=True, title='Gender composition Senate', ax=ax2)
    

femicides_plot()
congress_plots()


def plot_states(state_df, Entity):
    grouped_state_df = state_df.groupby('Entity')
    plot = figure(title= ('Gender Composition in Congress: {}').format(Entity), x_axis_label='Year', y_axis_label= 'Percentage')
    data = grouped_state_df.get_group(Entity)
    plot.vbar_stack(['%_Women', '%_Men'], x='Year', width=0.9, color=['blue', 'green'], source=data, legend_label=['%_Women', '%_Men'])
    return plot


@interact(Entity=state_df['Entity'].unique())
def make_plot_for(Entity=state_df['Entity'].unique()[0]):
    plot = plot_states(state_df, Entity)
    show(plot)
    


def femicides_regression(df1, femicides):
    df1 = df1[df1['Year'] != 2019] 
    femicides_state = femicides[femicides['Year'] >= 2010] 
    femicides_state = femicides_state[femicides_state.Entity != "Nacional"]
    femicides_national = femicides[femicides.Entity == "Nacional"]
    if df1.shape[0] < 20:
         y = femicides_national
    else:
         y = femicides_state
    X = df1['%_Women'].values.reshape((-1, 1))
    y = y['Rate per 100K Women'].values.reshape((-1, 1))
    X2 = sm.add_constant(X)
    model = sm.OLS(y, X2)
    model = model.fit()
    print(model.summary())


femicides_regression(state_df, femicides)
femicides_regression(deputies, femicides)
femicides_regression(senators, femicides)



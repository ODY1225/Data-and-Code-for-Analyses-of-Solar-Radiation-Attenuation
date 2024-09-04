#%% Imported packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#%% In-situ data preparation
Root = ''
def CWA_StationData(istation_name):
    # Load data
    df = pd.read_csv(Root+istation_name+'_CWA_19802020.csv')
    
    # Time variable
    df['yyyymmddhh'] = pd.to_datetime(df['yyyymmddhh'])
    df['hour'] = df['yyyymmddhh'].apply(lambda t: t.hour)
    df['year'] = df['yyyymmddhh'].apply(lambda t: t.year)
    df['month'] = df['yyyymmddhh'].apply(lambda t: t.month)
    df['date'] = df['yyyymmddhh'].apply(lambda t: t.date())
    
    # Raw data 
    ## Extract valid data
    for ivar in ['SS02','VS01','CD11','ST09']: ## Required variable: Solar Radiaiton, Visibility, Total Cloud Amount, Obscurity
        df[ivar].loc[df[ivar]<0]=np.nan
    df['CD11'].loc[df['CD11']>10]=np.nan
    df['VS01'].loc[-((df['hour'] == 2)|(df['hour'] == 5)|(df['hour'] == 8)|(df['hour'] == 9)|(df['hour'] == 11)|(df['hour'] == 14)|(df['hour'] == 17)|(df['hour'] == 20)|(df['hour'] == 21))] = np.nan
    df['CD11'].loc[-((df['hour'] == 2)|(df['hour'] == 5)|(df['hour'] == 8)|(df['hour'] == 9)|(df['hour'] == 11)|(df['hour'] == 14)|(df['hour'] == 17)|(df['hour'] == 20)|(df['hour'] == 21))] = np.nan
    ## Transfer unit to Wm^-2
    df["SS02"] = df["SS02"]/0.0036
    
    # Cloud/Fog Group 
    ## Based on Total Cloud Amount
    ### 1:Cloudy
    ### 2:some Cloud
    ### 3:Cloud-free
    df['CLD'] = np.full(len(df), np.nan)
    df['CLD'].loc[(df['CD11'] >= 0)&(df['CD11'] <= 3)] = '3'
    df['CLD'].loc[(df['CD11'] >= 4)&(df['CD11'] <= 7)] = '2'
    df['CLD'].loc[(df['CD11'] >= 8)&(df['CD11'] <= 10)] = '1'
    ## Based on Obscurity 
    ### 1:Fog
    ### 2:Mist
    ### 3:Fog-free
    df['VIS'] = np.full(len(df), np.nan)
    df['VIS'].loc[(df['ST09'] != 1)&(df['ST09'] != 9)] = '3'
    df['VIS'].loc[df['ST09'] == 9] = '2'
    df['VIS'].loc[df['ST09'] == 1] = '1'
    df['VIS'].loc[df['VS01'] >= 10] = '3'
    df['VIS'].loc[(df['VS01'] >= 1)&(df['VS01'] < 10)] = '2'
    df['VIS'].loc[df['VS01'] < 1] = '1'

    # Season classificatoin
    df['season'] = np.full(len(df), np.nan)
    df['season'].loc[(df['month'] == 12)|(df['month'] == 1)|(df['month'] == 2)] = 'DJF'
    df['season'].loc[(df['month'] == 3)|(df['month'] == 4)|(df['month'] == 5)] = 'MAM'
    df['season'].loc[(df['month'] == 6)|(df['month'] == 7)|(df['month'] == 8)] = 'JJA'
    df['season'].loc[(df['month'] == 9)|(df['month'] == 10)|(df['month'] == 11)] = 'SON'
    
    # Weather events by Su et. al.(2018)
    weather_events = pd.read_csv(Root+'TAD_v2022_20220601.csv')
    weather_events['yyyymmdd'] = pd.to_datetime(weather_events['yyyymmdd'].map(str), format = '%Y%m%d')
    weather_events['year'] = weather_events['yyyymmdd'].apply(lambda t: t.year)
    weather_events = weather_events[(weather_events['year'] >= 1980) & (weather_events['year'] <= 2020)].reset_index(drop=True)
    weather_events_df = weather_events.loc[weather_events.index.repeat(24)].reset_index(drop=True)    
    for iweather in ['CS', 'TYW', 'TC100', 'TC200', 'TC300', 'TC500', 'FT', 'NE', 'SNE', 'SWF', 'SSWF', 'DS']:
        df[iweather] = weather_events_df[iweather].values[:]
    
    # Extract required time period
    df = df[(df['year'] >= 1980) & (df['year'] <= 2020)].reset_index(drop=True)
    # Extract required variable
    df = df[(['yyyymmddhh', 'date', 'hour','season', 'year', 'SS02', 'VS01', 'ST09', 'VIS', 'CD11', 'CLD', 'PP01', 'SWF', 'NE'])]

    # Remove rainy data
    df = df[df['PP01'] == 0]
    return df
# CWA Station Data
CWAStation = {'Alishan':{'data':CWA_StationData('Alishan'), 'color':'green', 'type':'MCF'},
              'Chiayi':{'data':CWA_StationData('Chiayi'), 'color':'black', 'type':'no forest'},
              'Zhuzihu':{'data':CWA_StationData('Zhuzihu'), 'color':'#EE9A00', 'type':'other forest'},
              'Yilan':{'data':CWA_StationData('Yilan'), 'color':'blue'}}
CWAVariable = {'SS02':{'long_name':'Solar Radiation', 'unit':'Wm$^{-2}$', 'yticks':np.arange(0, 1100, 100), 'ylim':[-5, 1100]},
               'VS01':{'long_name':'Visibility', 'unit':'km', 'yticks':np.arange(0, 34, 2), 'ylim':[-0.5, 36]},
               'CD11':{'long_name':'Total Cloud Amount', 'unit':'out of 10', 'yticks':np.arange(0, 11, 1), 'ylim':[-0.5, 11.5]},
               'ST09':{'long_name':'Obscurity'}}
#%% Figure 1.1 Annual diurnal cycle (rainy data has been excluded) of solar radiation from CWA Chiayi station, Zhuzihu and Alishan station.
ivariable = 'SS02'
plt.figure(figsize = (5.1, 6), dpi = 300)
plt.title('In-situ Radiation\n(remove rainy data)', loc = 'left', weight = 'bold', fontsize = 14)
plt.title('\n' + 'Time: 2000-2020', loc = 'right', fontsize = 14)
for istation in ['Chiayi', 'Zhuzihu', 'Alishan']:
    idf = CWAStation[istation]['data']
    idf = idf[((idf['year']>=2000)&(idf['year']<=2020))] #time period: 2000-2020
    Diurnalmean = idf[ivariable].groupby(idf.hour).apply(lambda g: g.mean(skipna = True)) #mean
    DiurnalQ25 = idf[ivariable].groupby(idf.hour).apply(lambda g: g.quantile(0.25)) #percentile25
    DiurnalQ75 = idf[ivariable].groupby(idf.hour).apply(lambda g: g.quantile(0.75)) #percentile75
    plt.fill_between(Diurnalmean.index, DiurnalQ25, DiurnalQ75, color = CWAStation[istation]['color'], alpha = 0.15)
    plt.plot(Diurnalmean.index, Diurnalmean, 
             color = CWAStation[istation]['color'], label = istation+' ('+CWAStation[istation]['type']+')', 
             linestyle = '-', alpha = 1, linewidth = 2.5) 
plt.xlabel('Time[hour]', weight = 'bold', fontsize = 14)
plt.ylabel(CWAVariable[ivariable]['long_name']+'['+CWAVariable[ivariable]['unit']+']', weight = 'bold', fontsize = 14)
plt.xticks(np.arange(0, 24, 3), fontsize = 14)
plt.yticks(np.arange(0, 1400, 100), fontsize = 14)
plt.xlim(0, 23)
plt.ylim(-20, 1000)
plt.legend(fontsize = 11, loc = 'upper center', ncol = 2)
plt.grid()
plt.tight_layout()
#%% Figure 1.2 Effects of cloud-fog on solar radiation (rainy data has been excluded).
#%%% Top two figures: Annual diurnal cycle of solar radiation at CWA Alishan station under different total cloud amount and visibility conditions, respectively.
ivariable = 'SS02'
condition_parameters = {'1':{'CLD':'8 ≤ CLD ≤ 10', 'VIS':'VIS < 1 km', 'color':'darkgreen'}, 
                        '2':{'CLD':'4 ≤ CLD ≤ 7', 'VIS':'1 ≤ VIS < 10 km', 'color':'steelblue'}, 
                        '3':{'CLD':'0 ≤ CLD ≤ 3', 'VIS':'VIS ≥ 10 km', 'color':'grey'},
                        'Criteria':{'CLD':[5, 5, 5], 'VIS':[5, 5, 10]}, #criteria for hour count per day
                        'Name':{'CLD':'Cloud', 'VIS':'Visibility'}}
def PLOT_CloudFogGroupDiurnal(istation, iGroup): #istation: Alishan, Chiayi, Zhuzihu, Yilan; iGroup: CLD(based on total cloud amount), VIS(based on obsurity)
    idf = CWAStation[istation]['data']
    idf_solar = idf[((idf['hour']>=8)&(idf['hour']<=17))&((idf['year']>=2000)&(idf['year']<=2020))] #time period: 2000-2020, 08-17 LT
    Diurnal_dict = {'1':np.nan, '2':np.nan, '3':np.nan} #dictionary for visualization 
    for icondition in ['1', '2', '3']:
        idf_icondition = idf_solar[(idf_solar[iGroup] == icondition)]
        count = idf_icondition.groupby(['date']).apply(lambda g: g.count()) #count for its condition
        iDate = count['date'][count['date']>=condition_parameters['Criteria'][iGroup][int(icondition)-1]] #only exceed criteria for its condition can be assigned to corresponding group
        iDatedf = pd.DataFrame()
        for d in iDate.index:
            iDatedf = pd.concat([iDatedf, idf[idf['date'] == d]])
        Diurnalmean = iDatedf[ivariable].groupby(iDatedf.hour).apply(lambda g: g.mean(skipna = True)) #mean
        DiurnalQ25 = iDatedf[ivariable].groupby(iDatedf.hour).apply(lambda g: g.quantile(0.25)) #percentile25
        DiurnalQ75 = iDatedf[ivariable].groupby(iDatedf.hour).apply(lambda g: g.quantile(0.75)) #percentile75
        DiurnalCount = int(len(iDate)) #sample size
        Diurnal_dict[icondition] = {'mean':Diurnalmean, 'Q25':DiurnalQ25, 'Q75':DiurnalQ75, 'count':DiurnalCount}
    fig = plt.figure(figsize = (6, 5), dpi = 300)
    plt.title(CWAVariable[ivariable]['long_name']+'\nin 3 '+condition_parameters['Name'][iGroup]+' Conditions', loc = 'left', weight = 'bold', fontsize = 14)
    plt.title('CWA '+istation+' Station\nTime: 2000-2020', loc = 'right', fontsize = 14)
    plt.text(14, 1000, '(remove rainy data)', weight = 'bold', fontsize = 12)
    for icondition in ['3', '2', '1']:
        plt.fill_between(Diurnal_dict[icondition]['mean'].index, Diurnal_dict[icondition]['Q25'], Diurnal_dict[icondition]['Q75'],
                         color = condition_parameters[icondition]['color'], alpha = 0.2)
        plt.plot(Diurnal_dict[icondition]['mean'].index, Diurnal_dict[icondition]['mean'], 
                 label = condition_parameters[icondition][iGroup]+'\n('+str(Diurnal_dict[icondition]['count'])+' days)', 
                 color = condition_parameters[icondition]['color'], linewidth = 2.5)
    plt.xticks(np.arange(0, 24, 3), fontsize = 14)
    plt.yticks(np.arange(0, 1400, 100), fontsize = 14)
    plt.xlim(0, 23)
    plt.ylim([-20, 1050])
    plt.xlabel('Time[hour]', fontsize = 14, weight = 'bold')
    plt.ylabel(CWAVariable[ivariable]['long_name']+'['+CWAVariable[ivariable]['unit']+']', fontsize = 14, weight = 'bold')
    plt.grid()
    plt.legend(loc = 'upper left', fontsize = 11.5, ncol = 1)
    plt.tight_layout() 
PLOT_CloudFogGroupDiurnal('Alishan', 'CLD')
PLOT_CloudFogGroupDiurnal('Alishan', 'VIS')
#%%% Bottom two figures: Relationship between solar radiation and total cloud amount and visibility [km], respectively.
ivariable = 'SS02'
relationship_parameters = {'CWAvar':{'CLD':'CD11', 'VIS':'VS01'},
                           'Name':{'CLD':'Cloud', 'VIS':'Visibility'}}
def PLOT_Relationship(istation, iGroup, itime, icriteria): #istation: Alishan, Chiayi, Zhuzihu, Yilan; iGroup: CLD(y-axis to be total cloud amount) or VIS(y-axis to be visibility); itime: 8, 9, 11, 14, 17; icriteria: criteria for smaple size per quantity 
    idf = CWAStation[istation]['data']
    idf_itime = idf[(idf['hour'] == itime)&((idf['year']>=2000)&(idf['year']<=2020))] #time period: 2000-2020, 11 LT
    
    XY = pd.concat([idf_itime[relationship_parameters['CWAvar'][iGroup]], idf_itime[ivariable]], axis=1)
    Group_XY = np.array(XY.groupby(relationship_parameters['CWAvar'][iGroup]))
    Group_XY = Group_XY[np.array([len(Group_XY[i,1]) for i in range(len(Group_XY))]) > icriteria] #only exceed criteria can be visualized
    
    Relationship = np.zeros((len(Group_XY), 5)) #for visualization 
    for vis in range(len(Group_XY)):
        Relationship[vis,0] = Group_XY[vis,0]
        Relationship[vis,1] = np.nanmean(Group_XY[vis,1][ivariable]) #mean
        Relationship[vis,2] = np.nanmedian(Group_XY[vis,1][ivariable]) #median
        Relationship[vis,3] = np.nanquantile(Group_XY[vis,1][ivariable], 0.25) #percentile25
        Relationship[vis,4] = np.nanquantile(Group_XY[vis,1][ivariable], 0.75) #percentile75
    fig = plt.figure(figsize = (4.5, 5), dpi = 300)
    plt.title('Relationship between '+CWAVariable[relationship_parameters['CWAvar'][iGroup]]['long_name']+'\nand '+CWAVariable[ivariable]['long_name']+' at '+str(itime)+':00 LT\n\n', 
              loc = 'left', weight = 'bold', fontsize = 12)
    plt.title('CWB Alishan Station\nTime: 2000-2020', loc = 'right', fontsize = 12)
    plt.vlines(Relationship[:,0], Relationship[:,3], Relationship[:,4], label = "IQR")
    plt.plot(Relationship[:,0], Relationship[:,2], linestyle = '', marker = "o", markerfacecolor = "k", label = "median", markersize = 5)
    plt.plot(Relationship[:,0], Relationship[:,1], linestyle = '', marker = "o", markerfacecolor = "w", label = "mean", markersize = 5)
    plt.yticks(np.arange(0, 1400, 100), size = 12)
    plt.ylim(0, 1000)
    plt.xlabel(CWAVariable[relationship_parameters['CWAvar'][iGroup]]['long_name']+'['+CWAVariable[relationship_parameters['CWAvar'][iGroup]]['unit']+']', fontsize = 12, weight = "bold")
    plt.ylabel(CWAVariable[ivariable]['long_name']+'['+CWAVariable[ivariable]['unit']+']', weight = 'bold', fontsize = 12)
    if iGroup == 'VIS':
        plt.legend(loc = 'upper left')
        plt.xscale('log') #log sale for x-axis in visibility
    else:
        plt.legend(loc = 'lower left')
    plt.grid()
    plt.tight_layout()  
PLOT_Relationship('Alishan', 'VIS', 11, 3)
PLOT_Relationship('Alishan', 'CLD', 11, 3)
#%% Figure 3.2 Solar radiation attenuation characteristics under different weather events (rainy data has been excluded). 
#%%% The right figures: Diurnal cycle of solar radiation for four reference CWA stations: Chiayi, Alishan, Zhuzihu, and Yilan. 
ivariable = 'SS02'
def PLOT_WeatherDiurnal(iweather, iseason): #iweather: NE(north-easterlies), SWF(south-westerlies); iseason: DJF(winter), MAM(spring), JJA(summer), SON(autumn)
    plt.figure(figsize = (5, 5), dpi = 300)
    plt.title('In-situ Radiation', loc = 'left', weight = 'bold', fontsize = 14)
    plt.title('\n' + 'Time: 2011-2019', loc = 'right', fontsize = 14)
    for istation in ['Chiayi', 'Zhuzihu', 'Yilan', 'Alishan']:
        idf = CWAStation[istation]['data']
        idf_iweather_iseason = idf[(idf[iweather] == 1)&(idf['season'] == iseason)&((idf['year']>=2011)&(idf['year']<=2019))] #time period: 2011-2019
        Diurnalmean = idf_iweather_iseason[ivariable].groupby(idf_iweather_iseason.hour).apply(lambda g: g.mean(skipna = True)) #mean
        DiurnalQ25 = idf_iweather_iseason[ivariable].groupby(idf_iweather_iseason.hour).apply(lambda g: g.quantile(0.25)) #percentile25
        DiurnalQ75 = idf_iweather_iseason[ivariable].groupby(idf_iweather_iseason.hour).apply(lambda g: g.quantile(0.75)) #percentile75
        plt.fill_between(Diurnalmean.index, DiurnalQ25, DiurnalQ75, color = CWAStation[istation]['color'], alpha = 0.15)
        plt.plot(Diurnalmean.index, Diurnalmean, color = CWAStation[istation]['color'], label = istation, 
                 linestyle = '-', alpha = 1, linewidth = 2.5) 
    plt.xlabel('Time[hour]', weight = 'bold', fontsize = 14)
    plt.ylabel(CWAVariable[ivariable]['long_name']+'['+CWAVariable[ivariable]['unit']+']', weight = 'bold', fontsize = 14)
    plt.xticks(np.arange(0, 24, 3), fontsize = 14)
    plt.yticks(np.arange(0, 1400, 100), fontsize = 14)
    plt.xlim(0, 23)
    plt.ylim(-20, 1000)
    plt.legend(fontsize = 11, loc = 'upper left', ncol = 1)
    plt.grid()
    plt.tight_layout()
PLOT_WeatherDiurnal('SWF', 'JJA')
PLOT_WeatherDiurnal('NE', 'DJF')
#%% Figure S3 Diurnal cycle (rainy data has been excluded) of solar radiation [Wm-2], total cloud amount [out of 10] and visibility [km] for four CWA stations: Chiayi, Alishan, Zhuzihu, and Yilan.
def PLOT_WinterSummerDiurnal(ivariable, istation): #ivariable: SS02, CD11, VS01; istation: Alishan, Chiayi, Zhuzihu, Yilan
    plt.figure(figsize = (5, 5), dpi = 300)
    plt.title(CWAVariable[ivariable]['long_name']+'\n(remove rainy data)', loc = 'left', weight = 'bold', fontsize = 14)
    plt.title('CWA '+ istation + ' Station\n' + 'Time: 2000-2020', loc = 'right', fontsize = 14) 
    season_parameters = {'JJA':'red',
                         'DJF':'blue'}
    for iseason in ['DJF', 'JJA']:
        idf = CWAStation[istation]['data'][CWAStation[istation]['data']['season'] == iseason]
        idf_iseason = idf[(idf['season'] == iseason)&((idf['year']>=2000)&(idf['year']<=2020))] #time period: 2000-2020
        iDates = idf_iseason.groupby(idf_iseason.date).apply(lambda g: g.count()) #sample size
        Diurnalmean = idf_iseason[ivariable].groupby(idf_iseason.hour).apply(lambda g: g.mean(skipna = True)) #mean
        DiurnalQ25 = idf_iseason[ivariable].groupby(idf_iseason.hour).apply(lambda g: g.quantile(0.25)) #percentile25
        DiurnalQ75 = idf_iseason[ivariable].groupby(idf_iseason.hour).apply(lambda g: g.quantile(0.75)) #percentile75
        nan_mask = ~np.isnan(Diurnalmean)
        plt.fill_between(Diurnalmean.index[nan_mask], DiurnalQ25[nan_mask], DiurnalQ75[nan_mask], color = season_parameters[iseason], alpha = 0.15)
        plt.plot(Diurnalmean.index[nan_mask], Diurnalmean[nan_mask], color = season_parameters[iseason], label = iseason +'('+str(len(iDates))+' days)',
                 linestyle = "-", alpha = 1, linewidth = 2.5)  
    plt.xlabel('Time[hour]', weight = 'bold', fontsize = 12)
    plt.ylabel(CWAVariable[ivariable]['long_name']+'['+CWAVariable[ivariable]['unit']+']', weight = 'bold', fontsize = 12)
    plt.xticks(np.arange(0, 24, 3), fontsize = 12)
    if ivariable == 'CD11' or ivariable == 'VS01':
        plt.xticks([2, 5, 8, 9, 11, 14, 17, 20, 21], fontsize = 12)
    plt.yticks(CWAVariable[ivariable]['yticks'], fontsize = 12)
    plt.xlim(0, 23)
    plt.ylim(CWAVariable[ivariable]['ylim'])
    plt.legend(fontsize = 12, loc = 'upper center', ncol = 2)
    plt.grid()
    plt.tight_layout()
PLOT_WinterSummerDiurnal('CD11', 'Alishan')



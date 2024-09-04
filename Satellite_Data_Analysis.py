#%% Imported packages
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import netCDF4 as nc
from datetime import datetime, timedelta
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
#%% Satellite data preparation
Root = ''

# Terrain
dem20 = nc.Dataset(Root+'dem20_TCCIPInsolation.nc')
lon = dem20.variables['lon'][:]
lat = dem20.variables['lat'][:]
ele = dem20.variables['dem20'][:,:]
ele_group = np.tile('              ', reps = (525, 575))
for iele in range(0, 3750, 250):
    ele_group[(ele>=iele)&(ele<int(iele+250))] = str(iele)+'-'+str(int(iele+250))+' m'
ele_group[(ele>=3500)] = 'Above 3500 m'
Landmask = ~np.isnan(ele) ## mask of land areas
Mountmask = ele>500 ## mask of mountainous areas
# Month
Month = {1:{'name':'January','color':'navy'}, 2:{'name':'February','color':'blue'}, 3:{'name':'March','color':'springgreen'}, 
         4:{'name':'April','color':'green'}, 5:{'name':'May','color':'limegreen'}, 6:{'name':'June','color':'greenyellow'},
         7:{'name':'July','color':'gold'}, 8:{'name':'August','color':'orange'}, 9:{'name':'September','color':'orangered'}, 
         10:{'name':'October','color':'red'}, 11:{'name':'November','color':'aqua'}, 12:{'name':'December','color':'dodgerblue'}}
## Before replace lower outliers
MonthHour_pot_before = np.load(Root+'MonthHour_pot_20112019_Before.npy')
MonthHour_mean_before = np.load(Root+'MonthHour_mean_20112019_Before.npy')
## After replace lower outliers
MonthHour_pot = np.load(Root+'MonthHour_pot_20112019.npy')
MonthHour_mean = np.load(Root+'MonthHour_mean_20112019.npy')
# Information for CWA Station (based on https://e-service.cwa.gov.tw/wdps/obs/state.htm) 
CWAStation = {'Alishan':{'lon':120.813242, 'lat':23.508208, 'color':'green', 'type':'MCF'},
              'Chiayi':{'lon':120.432906, 'lat':23.495925, 'color':'black', 'type':'no forest'},
              'Zhuzihu':{'lon':121.544547, 'lat':25.162078, 'color':'#EE9A00', 'type':'other forest'},
              'Yilan':{'lon':121.756528,'lat':24.763975, 'color':'blue'}}
#%% Radiation Difference preparation
RadDiff = np.load(Root+'RadiationDifference_daily_20112019.npy')

# Radiation Difference without rainy data
Rain = nc.Dataset(Root+'rain.20112019.daily.1km-grid-v2.nc')
Rain = Rain.variables['rain'][:,:,:]
RadDiff_norain = np.ma.array(RadDiff, mask = Rain <= 0)

# Weather events dataframe
RadDiff_df = pd.DataFrame({'yyyymmdd': pd.date_range(start='2011-01-01',end='2019-12-31')})
RadDiff_df['month'] = RadDiff_df['yyyymmdd'].apply(lambda t: t.month)
weather_events = pd.read_csv(Root+'TAD_v2022_20220601.csv') ## Taiwan Atmospheric Event Database from Su et al.(2018)(https://osf.io/4zutj/)
weather_events['yyyymmdd'] = pd.to_datetime(weather_events['yyyymmdd'].map(str), format = '%Y%m%d')
weather_events['year'] = weather_events['yyyymmdd'].apply(lambda t: t.year)
weather_events = weather_events[(weather_events['year'] >= 2011) & (weather_events['year'] <= 2019)].reset_index(drop=True)
RadDiff_df['NE'] = weather_events['NE'].values
RadDiff_df['SWF'] = weather_events['SWF'].values
#%% Figure S4 The diurnal cycle of monthly potential radiation [Wm-2] boxplots. Apply TCCIP gridded satellite-retrieved shortwave radiation data to create boxplots of potential radiation for all land grid points in Taiwan.
for mm in range(1, 13):
    plt.figure(figsize = (5, 5), dpi = 300)
    plt.title('Potential Radiation\n('+Month[mm]['name']+')', fontsize = 14, weight = 'bold', loc = 'left')
    plt.title('Time: 2011-2019', fontsize = 14, loc = 'right')
    boxDiurnal = [] #for visualization  
    for hh in range(6, 20):
        boxDiurnal.append(MonthHour_pot_before[(mm-1)*14+(hh-6),:,:][Landmask]) #extract land data 
    plt.boxplot(boxDiurnal, showmeans = True, widths = np.tile(1, 14), flierprops = dict(marker ='o', markersize = 5))
    plt.xticks(np.arange(1, 15), np.arange(6, 20), fontsize = 13)
    plt.yticks(np.arange(0, 1400, 100), fontsize = 13)
    plt.xlim(0.5, 14.5)
    plt.ylim(-20, 1200)
    plt.xlabel('Time[hour]', fontsize = 14, weight = 'bold')
    plt.ylabel('Solar Radiation[Wm$^{-2}$]', fontsize = 14, weight = 'bold')
    plt.grid()
    plt.tight_layout()
#%% Figure S5 Monthly lower outliers of potential radiation [Wm-2] map. The color bar represents the occurrence time of lower outliers of potential radiation [Wm-2], and the grayscale represents the digital elevation model of Taiwan.
for mm in range(1, 13):
    fig, ax = plt.subplots(figsize = (5.5, 5.5), subplot_kw = {'projection': ccrs.PlateCarree()}, dpi = 300)
    ax.set_title('Lower Outliers Map\n('+Month[mm]['name']+')', fontsize = 14, weight = 'bold', loc = 'left')
    # Ticks 
    ax.tick_params(labelsize = 'medium')
    ax.set_xticks(np.arange(119, 122.5, 0.5), crs = ccrs.PlateCarree())
    ax.set_xticks(np.arange(119, 122.5, 0.25), minor = True, crs = ccrs.PlateCarree())
    ax.set_yticks(np.arange(21.5, 26, 0.5), crs = ccrs.PlateCarree())
    ax.set_yticks(np.arange(21.5, 26, 0.25), minor = True, crs = ccrs.PlateCarree())
    # Axis
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    # Extent
    ax.set_extent([119.8, 122.2, 21.8, 25.7])
    # Grid
    ax.gridlines(crs = ccrs.PlateCarree(), color = 'black', linestyle = 'dotted', draw_labels = False, xlocs = np.arange(118, 123, 0.5), ylocs = np.arange(21, 26, 0.5), alpha = 0.3)
    # Land border
    ax.contour(lon, lat, Landmask, levels = np.arange(0.5, 1.5, 0.5), colors = 'black', linewidths = 0.3, linestyles = 'solid', zorder = 0) 
    # Digital elevation model
    ax.contourf(lon, lat, ele, levels = np.arange(0, 4000, 100), cmap = 'Greys', linewidths = 0.1, zorder = 0)    
    for hh in range(11, 17):
        hh = int(27-hh) #reversed hour order
        Plot_data = MonthHour_pot_before[(mm-1)*14+(hh-6),:,:] #load specific hour data
        iqr = np.subtract(*np.percentile(Plot_data[Landmask], [75, 25])) #interquartile range
        loMask = Plot_data < (np.quantile(Plot_data[Landmask], 0.25) - 1.5*iqr) #lower outliers
        Plot_data = np.where(loMask, np.tile(hh, (525, 575)), np.nan) #extract area of lower outliers 
        maskPlot_data = np.where(Landmask, Plot_data, np.nan) #extract land area 
        cmap = plt.cm.get_cmap('jet', 6)
        PLOT = ax.pcolormesh(lon, lat, maskPlot_data, shading = 'auto', vmin = 11, vmax = 16, cmap = cmap, alpha = 0.6)
    CBAR = fig.colorbar(PLOT, ticks = np.linspace(11, 16, 13))
    CBAR.ax.set_yticklabels(['', '11', '', '12', '', '13', '', '14', '', '15', '', '16', '']) 
    CBAR.ax.tick_params(labelsize = 14)   
    ax.text(122.35, 25.8, 'Time', fontsize = 14, weight = 'bold')
    plt.tight_layout() 
#%% Figure 2.1 The schematic plot of radiation difference method, taking CWA Alishan station as an example.
iStation = 'Alishan'
ilon = np.argmin(np.absolute(lon - CWAStation[iStation]['lon'])) 
ilat = np.argmin(np.absolute(lat - CWAStation[iStation]['lat']))
PlotdataJJA_pot = np.tile(np.nan, (14))
PlotdataJJA_obs = np.tile(np.nan, (14))
for hh in range(6, 20):
    Hour_pot = np.tile(np.nan, (12))
    Hour_obs = np.tile(np.nan, (12))
    for mm in [6,7,8]: 
        Hour_pot[(mm-1)] = MonthHour_pot[(hh-6)+14*(mm-1),ilat,ilon]
        Hour_obs[(mm-1)] = MonthHour_mean[(hh-6)+14*(mm-1),ilat,ilon]
    PlotdataJJA_pot[(hh-6)] = np.nanmean(Hour_pot)
    PlotdataJJA_obs[(hh-6)] = np.nanmean(Hour_obs)
plt.figure(figsize = (6, 5), dpi = 300)
plt.title('TCCIP\nSatellite-retrived Radiation', loc = 'left', weight = 'bold', fontsize = 13)
plt.title('CWA '+iStation+' Station', loc = 'right', fontsize = 13)
plt.plot(np.arange(0, 24),np.hstack([np.zeros(6),PlotdataJJA_pot,np.zeros(4)]), color = 'black', label = 'Potential(JJA)', linestyle = '--', alpha = 1)
plt.plot(np.arange(0, 24),np.hstack([np.zeros(6),PlotdataJJA_obs,np.zeros(4)]), color = 'black', label = 'Observed(JJA)', linestyle = '-', alpha = 1)    
plt.xlabel('Time[hour]', weight = 'bold', fontsize = 12)
plt.ylabel('Solar Radiation[Wm$^{-2}$]', weight = 'bold', fontsize = 12)
plt.xticks(np.arange(0, 24, 1), fontsize = 12)
plt.yticks(np.arange(0, 1400, 100), fontsize = 12)
plt.xlim(5, 20)
plt.ylim(-10, 1100)
plt.legend(fontsize = 11, loc = 'upper center', ncol = 2)
plt.grid()
plt.tight_layout()
#%% Figure 3.1 Mean radiation difference [%] pattern in four seasons. The color bar represents the mean radiation difference [%] for the maps, foggy regions (map: black cross mask; scatter plot: blue dots) represent regions above 90 percentile of MODIS ground fog frequency, and fogless regions (map: grey horizontal stripes mask; scatter plot: red dots) represent regions below 10 percentile of MODIS ground fog frequency. black cross dot represents the four reference CWA stations: Chiayi, Alishan, Zhuzihu, and Yilan.
#%% Figure 3.2 Solar radiation attenuation characteristics under different weather events. The left figures are the radiation difference map, the middle figures are the boxplots of radiation difference for different elevation interval. The right figures are the diurnal cycle of solar radiation [Wm-2] for four reference CWA stations: Chiayi, Alishan, Zhuzihu, and Yilan. The top figures are for southwesterly wind events and the bottom figures are for the northeasterly wind events, weather events classification is adapted from Su et. al., (2018).
#%%% Radiation Difference Map
period_parameters = {
    'JJA':((RadDiff_df['month'] == 6)|(RadDiff_df['month'] == 7)|(RadDiff_df['month'] == 8)), 
    'SON':((RadDiff_df['month'] == 9)|(RadDiff_df['month'] == 10)|(RadDiff_df['month'] == 11)),
    'DJF':((RadDiff_df['month'] == 12)|(RadDiff_df['month'] == 1)|(RadDiff_df['month'] == 2)),
    'MAM':((RadDiff_df['month'] == 3)|(RadDiff_df['month'] == 4)|(RadDiff_df['month'] == 5)),
    'DJF_NE':(RadDiff_df['NE'] == 1)&((RadDiff_df['month'] == 12)|(RadDiff_df['month'] == 1)|(RadDiff_df['month'] == 2)),
    'JJA_SWF':(RadDiff_df['SWF'] == 1)&((RadDiff_df['month'] == 6)|(RadDiff_df['month'] == 7)|(RadDiff_df['month'] == 8))
    }
for iperiod in list(period_parameters.keys()):
    try: 
        FogFreq_iperiod = nc.Dataset(Root+'Regrid_freq_'+iperiod+'_WGS84.nc')
        maskFogFreq_iperiod = np.ma.array(FogFreq_iperiod.variables['fog'][:,:], mask = ~Landmask)
        freqQ90 = maskFogFreq_iperiod >= np.nanquantile(maskFogFreq_iperiod[Landmask], 0.9)
        freqQ10 = maskFogFreq_iperiod <= np.nanquantile(maskFogFreq_iperiod[Landmask], 0.1)
    except:
        pass
    Plot_data = np.nanmean(RadDiff_norain[period_parameters[iperiod],:,:], axis = 0)*100
    maskPlot_data = np.ma.array(Plot_data, mask = ~Landmask)
    
    fig, ax = plt.subplots(figsize = (5.5, 5.5), subplot_kw = {'projection': ccrs.PlateCarree()}, dpi = 300)
    ax.set_title('Mean Radiation Difference Map\n', fontsize = 14, weight = 'bold', loc = 'left')
    ax.set_title(iperiod + ' (' + str(len(RadDiff_norain[period_parameters[iperiod],:,:])) + 'days)', fontsize = 14, loc = 'left')
    ax.set_title(iperiod, fontsize = 14, loc = 'left')
    # Ticks 
    ax.tick_params(labelsize = 'medium')
    ax.set_xticks(np.arange(119, 122.5, 0.5), crs = ccrs.PlateCarree())
    ax.set_xticks(np.arange(119, 122.5, 0.25), minor = True, crs = ccrs.PlateCarree())
    ax.set_yticks(np.arange(21.5, 26, 0.5), crs = ccrs.PlateCarree())
    ax.set_yticks(np.arange(21.5, 26, 0.25), minor = True, crs = ccrs.PlateCarree())
    # Axis
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    # Extent
    ax.set_extent([119.8, 122.2, 21.8, 25.7])
    # Grid
    ax.gridlines(crs = ccrs.PlateCarree(), color = 'black', linestyle = 'dotted', draw_labels = False, xlocs = np.arange(118, 123, 0.5), ylocs = np.arange(21, 26, 0.5), alpha = 0.3)
    # Land border
    ax.contour(lon, lat, Landmask, levels = np.arange(0.5, 1.5, 0.5), colors = 'black', linewidths = 0.3, linestyles = 'solid', zorder = 0) 
    # Mountain border
    ax.contour(lon, lat, Mountmask, levels = np.arange(0.5, 1.5, 0.5), colors = 'black', linewidths = 0.75, linestyles = 'dashed', label = '500 m isohypse', zorder = 1)
    ax.scatter([121.544547, 121.756528, 120.432906, 120.813242], [25.162078, 24.763975, 23.495925, 23.508208], s = 10, color = 'black', marker = 'X', linewidths = 0.25, edgecolors = 'white')

    PLOT = ax.contourf(lon, lat, maskPlot_data, levels = np.arange(15, 92.5, 2.5), cmap = 'jet', extend = 'both', alpha = 1, zorder = 1)    
    CBAR = fig.colorbar(PLOT, ticks = np.arange(15, 92.5, 5))
    CBAR.ax.tick_params(labelsize = 14)    
    try:
        freq_iperiod = nc.Dataset(Root+'Regrid_freq_'+iperiod+'_WGS84.nc')
        mpl.rcParams['hatch.linewidth'] = 0.2
        mpl.rcParams['hatch.color'] = 'black'
        ax.contour(lon, lat, freqQ90, levels = np.arange(0.5, 1.5, 0.5), colors = 'black', linewidths = 0.2, linestyles = 'solid',
                   label = 'Ground Fog Frequency Q90: '+str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.9), 3)), zorder = 3)
        ax.contourf(lon, lat, freqQ90, levels = np.arange(0.5, 1.5, 0.5), colors = 'black', alpha = 0, hatches = ['xxxxxxxx'], 
                    label = 'Ground Fog Frequency Q90: '+str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.9), 3)), zorder = 3)
        mpl.rcParams['hatch.color'] = '#0F0F0F'    
        ax.contour(lon, lat, freqQ10, levels = np.arange(0.5, 1.5, 0.5), colors = '#0F0F0F', linewidths = 0.2, linestyles = 'solid',
                   label = 'Ground Fog Frequency Q10: '+str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.1), 3)), zorder = 3)
        ax.contourf(lon, lat, freqQ10, levels = np.arange(0.5, 1.5, 0.5), colors = '#0F0F0F', alpha = 0, hatches = ['------'], 
                    label = 'Ground Fog Frequency Q10: '+str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.1), 3)), zorder = 3)
        TEXT = ax.text(119.9, 25.35, 'Ground Fog Frequency\n'+'Q10: '+str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.1), 3))+'     Q90: '+str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.9), 3)))
        TEXT.set_bbox(dict(facecolor = 'white', edgecolor = 'black'))
    except:
        pass
    plt.tight_layout()
#%%% Scatter Plot
for iperiod in list(period_parameters.keys())[:-2]:
    FogFreq_iperiod = nc.Dataset(Root+'Regrid_freq_'+iperiod+'_WGS84.nc')
    maskFogFreq_iperiod = np.ma.array(FogFreq_iperiod.variables['fog'][:,:], mask = ~Landmask)
    freqQ90 = maskFogFreq_iperiod >= np.nanquantile(maskFogFreq_iperiod[Landmask], 0.9)
    freqQ10 = maskFogFreq_iperiod <= np.nanquantile(maskFogFreq_iperiod[Landmask], 0.1)

    Plot_data = np.nanmean(RadDiff_norain[period_parameters[iperiod],:,:], axis = 0)*100
    PlotGroup = []
    for g in ['0-250 m', '250-500 m', '500-750 m', '750-1000 m', '1000-1250 m', '1250-1500 m', '1500-1750 m', '1750-2000 m', 
     '2000-2250 m', '2250-2500 m', '2500-2750 m', '2750-3000 m', '3000-3250 m', '3250-3500 m', 'Above 3500 m']:
        PlotGroup.append(Plot_data[ele_group == g])
    plt.figure(figsize = (3, 5), dpi = 300)
    plt.tick_params(axis='y',direction='in', pad = -35)
    plt.title('Comparison of\nRadiation Difference and Elevation\n' , fontsize = 14, weight = 'bold', loc = 'center')
    plt.title('2011-2019', fontsize = 14, loc = 'right')
    plt.title(iperiod, fontsize = 14, loc = 'left')

    plt.scatter(Plot_data[Landmask], ele[Landmask], s = 0.2, color = 'grey')
    plt.scatter(Plot_data[freqQ90], ele[freqQ90], s = 0.2, color = 'blue', label = '≥ Q90 (' +str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.9), 3)) + ')')
    plt.scatter(Plot_data[freqQ10], ele[freqQ10], s = 0.2, color = 'red', label = '≤ Q10 (' +str(round(np.nanquantile(maskFogFreq_iperiod[Landmask], 0.1), 3)) + ')')
    
    plt.xlabel('Radiation Difference[%]', weight = 'bold', fontsize = 12)
    plt.ylabel('Elevation[m]', weight = 'bold', fontsize = 12)
    plt.xticks(np.arange(15, 90, 5), 
               labels = [15, '', '', '', '', '', '', 50, '', '', '', '', '', '', 85], 
               rotation = 90, fontsize = 12)
    plt.yticks(np.arange(0, 4000, 250), 
               labels = ['', '', 500, '', 1000, '', 1500, '', 2000, '', 2500, '', 3000, '', 3500, ''], 
               fontsize = 12)
    plt.xlim(15, 85)
    plt.ylim(-20, 3750)
    lgnd = plt.legend(fontsize = 11, loc = 'best')
    lgnd.legendHandles[0]._sizes = [20]
    lgnd.legendHandles[1]._sizes = [20]
    plt.grid(alpha = 0.5)
    plt.tight_layout()
#%%% Boxplot
for iperiod in list(period_parameters.keys())[4:]:
    Plot_data = np.nanmean(RadDiff_norain[period_parameters[iperiod],:,:], axis = 0)*100
    PlotGroup = []
    for g in ['0-250 m', '250-500 m', '500-750 m', '750-1000 m', '1000-1250 m', '1250-1500 m', '1500-1750 m', '1750-2000 m', 
     '2000-2250 m', '2250-2500 m', '2500-2750 m', '2750-3000 m', '3000-3250 m', '3250-3500 m', 'Above 3500 m']:
        PlotGroup.append(Plot_data[ele_group == g])
    plt.figure(figsize = (3, 5), dpi = 300)
    plt.tick_params(axis='y',direction='in', pad = -35)
    plt.title('Comparison of\nRadiation Difference and Elevation\n' , fontsize = 14, weight = 'bold', loc = 'center')
    plt.title('2011-2019', fontsize = 14, loc = 'right')
    plt.title(iperiod, fontsize = 14, loc = 'left')
    
    plt.boxplot(PlotGroup, vert = False, showmeans = True, widths = 0.75)

    plt.xlabel('Radiation Difference[%]', weight = 'bold', fontsize = 14)
    plt.ylabel('Elevation[m]', weight = 'bold', fontsize = 14)
    plt.xticks(np.arange(15, 95, 5), 
               labels = [15, '', '', '', '', '', '', 50, '', '', '', '', '', '', '', 90], 
               rotation = 90, fontsize = 12)
    plt.yticks(np.arange(0.5, 15.5, 1)[1:], np.arange(0, 3750, 250)[1:], fontsize = 12)
    plt.xlim(15, 90)
    plt.ylim(0.4, 15.5)
    plt.grid(alpha = 0.5)
    plt.tight_layout()
#%% Figure 3.3 Summer/winter comparison of radiation pattern in foggy and fogless region. Figures on the left/right side are in summer (JJA) / winter (DJF). The top figures are the boxplots of radiation difference for foggy and fogless region. The middle figures are the surrounding radiation difference map for CWA Alishan/Yilan station. The bottom figures are the diurnal cycle of TCCIP satellite-retrieved radiation for CWA Alishan and Yilan station.
Month = {'JJA':[6,7,8],'DJF':[12,1,2]}
for iseason in ['JJA', 'DJF']:
    plt.figure(figsize = (5, 5), dpi = 300)
    plt.title('TCCIP Radiation', loc = 'left', weight = 'bold', fontsize = 14)
    plt.title('\n' + 'Time: 2011-2019', loc = 'right', fontsize = 14)
    for iStation in ['Alishan', 'Yilan']:
        Plotdata_pot = np.tile(0, (24))
        Plotdata_mean = np.tile(0, (24))
        ilon = np.argmin(np.absolute(lon - CWAStation[iStation]['lon'])) 
        ilat = np.argmin(np.absolute(lat - CWAStation[iStation]['lat']))
        for hh in range(6, 20):
            Hour_pot = np.tile(np.nan, (12))
            Hour_mean = np.tile(np.nan, (12))
            for mm in Month[iseason]: 
                Hour_pot[(mm-1)] = MonthHour_pot[(hh-6)+14*(mm-1),ilat,ilon]
                Hour_mean[(mm-1)] = MonthHour_mean[(hh-6)+14*(mm-1),ilat,ilon]
            Plotdata_pot[hh] = np.nanmean(Hour_pot)
            Plotdata_mean[hh] = np.nanmean(Hour_mean)
        plt.plot(np.arange(24),Plotdata_pot, color = 'black', label = 'Potential', linestyle = '--', alpha = 1)
        plt.plot(np.arange(24),Plotdata_pot, color = CWAStation[iStation]['color'], linestyle = '--', alpha = 1)
        plt.plot(np.arange(24),Plotdata_mean, color = CWAStation[iStation]['color'], label = iStation, linestyle = '-', alpha = 1)  
    plt.xlabel('Time[hour]', weight = 'bold', fontsize = 14)
    plt.ylabel('Solar Radiation[Wm$^{-2}$]', weight = 'bold', fontsize = 14)
    plt.xticks(np.arange(0, 24, 3), fontsize = 14)
    plt.yticks(np.arange(0, 1400, 100), fontsize = 14)
    plt.xlim(0, 23)
    plt.ylim(-20, 1200)
    plt.legend(fontsize = 11, loc = 'upper center', ncol = 2)
    plt.grid()
    plt.tight_layout()
#%% Figure S6 Comparison of radiation pattern in foggy and fogless region in four seasons. Figures on the top are the boxplots of radiation difference for foggy and fogless region. Figures on the bottom are the diurnal cycle of TCCIP satellite-retrieved radiation for foggy and fogless region, solid lines represent mean and shading represents the range from the 1st percentile to the 99th percentile.
MonthHour_mean_df = pd.DataFrame({"month":np.asarray([np.tile(month, 14) for month in range(1, 13)]).flatten(), 
                                  "hour":np.tile(np.arange(6, 20), 12).flatten()})
season_parameters = {'JJA':((MonthHour_mean_df['month'] == 6)|(MonthHour_mean_df['month'] == 7)|(MonthHour_mean_df['month'] == 8)), 
                     'SON':((MonthHour_mean_df['month'] == 9)|(MonthHour_mean_df['month'] == 10)|(MonthHour_mean_df['month'] == 11)),
                     'DJF':((MonthHour_mean_df['month'] == 12)|(MonthHour_mean_df['month'] == 1)|(MonthHour_mean_df['month'] == 2)),
                     'MAM':((MonthHour_mean_df['month'] == 3)|(MonthHour_mean_df['month'] == 4)|(MonthHour_mean_df['month'] == 5)),
                     }
for iseason in list(season_parameters.keys()):   
    FogFreq_iseason = nc.Dataset(Root+'Regrid_freq_'+iseason+'_WGS84.nc')
    maskFogFreq_iseason = np.ma.array(FogFreq_iseason.variables['fog'][:,:], mask = ~Landmask)
    freqQ90 = maskFogFreq_iseason >= np.nanquantile(maskFogFreq_iseason[Landmask], 0.9)
    freqQ10 = maskFogFreq_iseason <= np.nanquantile(maskFogFreq_iseason[Landmask], 0.1)
    iseasonData = MonthHour_mean[season_parameters[iseason],:,:].reshape(3, 14, 525, 575)
    Plot_data = np.nanmean(iseasonData, axis = 0)
    FoggyData = []
    FoglessData = []
    for h in range(14):
        FoggyData.append(np.ma.array(Plot_data[h,:,:], mask = ~Landmask)[freqQ90])
        FoglessData.append(np.ma.array(Plot_data[h,:,:], mask = ~Landmask)[freqQ10])
        
    plt.figure(figsize = (4.4, 3), dpi = 300)
    plt.title('TCCIP\nsatellite-retrieved radiation', loc = 'left', weight = 'bold', fontsize = 8)
    plt.title('Time: 2011-2019, '+iseason, loc = 'right', fontsize = 8)
    fog_parameters = {'Foggy':[FoggyData, 'blue', '≥ Q90', 0.9], 'Fogless':[FoglessData, 'red', '≤ Q10', 0.1]}
    for ifog in list(fog_parameters.keys()):
        idata = fog_parameters[ifog][0]
        q01 = [np.nanquantile(idata[hour], 0.01) for hour in range(14)]
        q99 = [np.nanquantile(idata[hour], 0.99) for hour in range(14)]
        Mean = [np.nanmean(idata[hour]) for hour in range(14)]     
        plt.fill_between(np.arange(6, 20), q01, q99, color = fog_parameters[ifog][1], alpha = 0.3)
        plt.plot(np.arange(6, 20), Mean, color = fog_parameters[ifog][1], label = fog_parameters[ifog][2]+' (' +str(round(np.nanquantile(maskFogFreq_iseason[Landmask], fog_parameters[ifog][3]), 3)) + ')') 
    plt.xticks(np.arange(0, 22, 3))
    plt.xlim(0, 23)
    plt.xlabel('')
    plt.yticks(np.arange(0, 1100, 100))
    plt.ylim(0, 800)
    plt.grid()
    plt.xlabel('Time[hour]', weight = 'bold')
    plt.ylabel('Solar Radiation[Wm$^{-2}$]', weight = 'bold')
    plt.legend(fontsize = 9, loc = 'upper left')
    plt.tight_layout()
    
    fog_iseason = np.where(Landmask, FogFreq_iseason.variables['fog'][:,:], np.nan)    
    RadDiffdata_iseason = np.nanmean(RadDiff[period_parameters[iseason],:,:], axis = 0)
    RadDiff_iseason = np.where(Landmask, RadDiffdata_iseason, np.nan)
    fogQ10mask = fog_iseason <= np.nanquantile(maskFogFreq_iseason[Landmask], 0.1)
    fogQ90mask = fog_iseason >= np.nanquantile(maskFogFreq_iseason[Landmask], 0.9)
    
    fig = plt.figure(figsize = (4, 3), dpi = 300)
    plt.title(iseason, loc = 'left', fontsize = 14)
    plt.boxplot([RadDiffdata_iseason[fogQ10mask]*100, RadDiffdata_iseason[fogQ90mask]*100], 
                labels = ['≤ Q10 ('+str(round(np.nanquantile(maskFogFreq_iseason[Landmask], 0.1), 3))+')' , '≥ Q90 ('+str(round(np.nanquantile(maskFogFreq_iseason[Landmask], 0.9), 3))+')'], 
                showmeans = True, flierprops = dict(markersize = 4))
    plt.ylim(20, 80)
    plt.yticks(np.arange(20, 90, 10))
    plt.ylabel('Radiation Difference[%]', weight = 'bold', fontsize = 10)
    plt.grid()
    plt.tight_layout()
    plt.show()

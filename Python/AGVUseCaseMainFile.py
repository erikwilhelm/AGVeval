# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 10:24:05 2023

Copyright 2023 Erik Wilhelm

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.


The overarching goal of the model is to enable the economic feasibility of a 
wide variety of autonomous ground vehicle projects to be objectively evaluated.
To achieve this goal, the model aims to answer the following questions:

1. What is the net present value of an investment in an automated ground 
vehicle for a specific application use case compared to the business as usual case?
2. What is the sensitivity of the amortization period to the input assumptions?
In other words, which input assumptions have the greatest effect on the
amortization period for the project?
3. Which implications do the deployment of automated ground robots have on
manpower needs? In other words, where can human resources be more effectively allocated?

@author: ew
"""

# Imports
import numpy as np
import pandas as pd
import warnings
import numpy_financial as npf
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from AGVUseCaseFunctions import *
plt.close('all')
plt.rcParams['axes.autolimit_mode'] = 'round_numbers'

## Assumptions
# Financial
discountRate = 0.05  # Five percent per annum
# Energy
electricityPrice = 0.23 # EUR/kWh
dieselPrice = 1.79 #EUR/L
dieselEnergy = 9.6 # kWh/L
# Data
dataCarriage = 0.7 #EUR/MB
# Lifecycle
YearsOfOperation=7.0 #Years that the robotic system is in operation
# Technology Readiness
TechnologyReadiness = 5.0 #Technology validated in relevant environment (industrially relevant environment in the case of key enabling technologies)
# Company Acceptance
CompanyAcceptance = 0.7 #represents a 'good' level of AGV acceptance within a company
# Mission Similarity
MissionSimilarity = 0.8 #represents an 'excellent' level of mission similarity
# Mission Determinism
MissionDeterminism = 0.6 #represents a 'sufficient' level of mission determinism

Assumptions={}
Assumptions['discountRate']=discountRate
Assumptions['electricityPrice']=electricityPrice
Assumptions['dieselPrice']=dieselPrice
Assumptions['dieselEnergy']=dieselEnergy
Assumptions['dataCarriage']=dataCarriage
Assumptions['YearsOfOperation']=YearsOfOperation
Assumptions['TechnologyReadiness']=TechnologyReadiness
Assumptions['CompanyAcceptance']=CompanyAcceptance
Assumptions['MissionSimilarity']=MissionSimilarity
Assumptions['MissionDeterminism']=MissionDeterminism


"""
BASELINE Inputs 

For the baseline case, we reach assumptinos resulting in an almost-zero Net
Present Value for a project replacing a human-driven vehicle with an autonomous 
version.

To Select these inputs, copy ALL text between "COPY START" and "COPY END" to
the "INSERT START" and "INSERT END" block

########### COPY START ############
#  CURRENT Mission Inputs
MissionLength=2 #km driven per misson round moving material
MaterialToMove=200 #amount of material (kg, m^3 etc) required to be moved from A to B for the mission
YearlyOperationDays = 212 #operating days per year. Note: differentiate availability for AGV vs human using max shift length

##  CURRENT Operator driven vehicle use inputs

VehicleCost=74000 #EUR
VehicleEnergyConsumption = 6.5 #L/100km
OperatorHourlyWage = 51 #EUR/hr
VehicleMaintenance = 120 #EUR/month
VehicleEOLCost = 1800 #EUR for end of life disposal
VehicleAverageSpeed=12 #km/hr
VehicleMaterialCapacity = 40 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
VehicleMaxShiftLength = 8 #hrs max which the vehicle can operate

##  CURRENT AGV use inputs
AGVCost = 115000 #EUR/vehicle  Note - set to zero if Leasing cost is set (Default 115000)
AGVLeasing = 0 #EUR/vehicle/year  Note - set to zero if AGV cost is set (Default 7000)
AGVMaintenance = 200 #EUR/month
AGVEOLCost = 4000 #EUR for end of life disposal
AGVAverageSpeed= 3 #km/hr (including all stop and blocked time caused by obstacles)
AGVChargeRate= 3 #kW
AGVDisengagementPerKm = 0.01 #disengagements per driven km
AGVDisengagementTime = 5 #minutes per disengagement
AGVMaterialCapacity = 20 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
AGVEnergyConsumption = 0.14 #kWh/km
AGVMaxShiftLength = 24 #if the AGV is unable to operate 24/7, an additional penalty can be added here
AGVDataUse = 4 #MB/day
########### COPY END ############

"""

########### INSERT START ############
#  CURRENT Mission Inputs
MissionLength=2 #km driven per misson round moving material
MaterialToMove=200 #amount of material (kg, m^3 etc) required to be moved from A to B for the mission
YearlyOperationDays = 212 #operating days per year. Note: differentiate availability for AGV vs human using max shift length

#  CURRENT Operator driven vehicle use inputs

VehicleCost=74000 #EUR
VehicleEnergyConsumption = 6.5 #L/100km
OperatorHourlyWage = 51 #EUR/hr
VehicleMaintenance = 120 #EUR/month
VehicleEOLCost = 1800 #EUR for end of life disposal
VehicleAverageSpeed=12 #km/hr
VehicleMaterialCapacity = 40 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
VehicleMaxShiftLength = 8 #hrs max which the vehicle can operate

#  CURRENT AGV use inputs
AGVCost = 115000 #EUR/vehicle  Note - set to zero if Leasing cost is set (Default 115000)
AGVLeasing = 0 #EUR/vehicle/year  Note - set to zero if AGV cost is set (Default 7000)
AGVMaintenance = 200 #EUR/month
AGVEOLCost = 4000 #EUR for end of life disposal
AGVAverageSpeed= 3 #km/hr (including all stop and blocked time caused by obstacles)
AGVChargeRate= 3 #kW
AGVDisengagementPerKm = 0.01 #disengagements per driven km
AGVDisengagementTime = 5 #minutes per disengagement
AGVMaterialCapacity = 20 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
AGVEnergyConsumption = 0.14 #kWh/km
AGVMaxShiftLength = 24 #if the AGV is unable to operate 24/7, an additional penalty can be added here
AGVDataUse = 4 #MB/day
########### INSERT END ############

### Structure Inputs and Assumptions
Inputs={}
Inputs['MissionLength']=MissionLength
Inputs['MaterialToMove']=MaterialToMove
Inputs['YearlyOperationDays']=YearlyOperationDays
Vehicle={}
Vehicle['VehicleAverageSpeed']=VehicleAverageSpeed
Vehicle['VehicleMaterialCapacity']=VehicleMaterialCapacity
Vehicle['VehicleMaxShiftLength']=VehicleMaxShiftLength
Vehicle['VehicleCost']=VehicleCost
Vehicle['VehicleEnergyConsumption']=VehicleEnergyConsumption
Vehicle['OperatorHourlyWage']=OperatorHourlyWage
Vehicle['VehicleMaintenance']=VehicleMaintenance
Vehicle['VehicleEOLCost']=VehicleEOLCost
Inputs['Vehicle']=Vehicle
AGV={}

AGV['AGVCost']=AGVCost
AGV['AGVLeasing']=AGVLeasing
AGV['AGVMaintenance']=AGVMaintenance
AGV['AGVEOLCost']=AGVEOLCost
AGV['AGVAverageSpeed']=AGVAverageSpeed
AGV['AGVChargeRate']=AGVChargeRate
AGV['AGVDisengagementPerKm']=AGVDisengagementPerKm
AGV['AGVDisengagementTime']=AGVDisengagementTime
AGV['AGVMaterialCapacity']=AGVMaterialCapacity
AGV['AGVEnergyConsumption']=AGVEnergyConsumption
AGV['AGVMaxShiftLength']=AGVMaxShiftLength
AGV['AGVDataUse']=AGVDataUse
Inputs['AGV']=AGV




##### MAIN CODE SECTION #####
##### BASELINE calculation
outputsBaseline=ModelAGVUseCase(Assumptions,Inputs)
## Plot the BASELINE results
figs=PlotCaseResults(Assumptions,Inputs,outputsBaseline,'BASELINE')

##### CHEAPER AGV calculation
Inputs['AGV']['AGVCost'] = 0.75 * Inputs['AGV']['AGVCost'] #reduced AGV cost
outputsCheaper=ModelAGVUseCase(Assumptions,Inputs)
## Plot the CHEAPER AGV results
figsCheaper=PlotCaseResults(Assumptions,Inputs,outputsCheaper,'CHEAPER AGV')
Inputs['AGV']['AGVCost'] =  Inputs['AGV']['AGVCost'] / 0.75  #return AGV cost to original value

###### SLOW VEHICLE calculation
Inputs['Vehicle']['VehicleAverageSpeed'] = 0.25 * Inputs['Vehicle']['VehicleAverageSpeed']
outputsSlower=ModelAGVUseCase(Assumptions,Inputs)
## Plot the SLOW VEHICLE results
figsSlower=PlotCaseResults(Assumptions,Inputs,outputsSlower,'SLOW VEHICLE')
Inputs['Vehicle']['VehicleAverageSpeed'] = Inputs['Vehicle']['VehicleAverageSpeed']/0.25 #return vehicle speed back to original value

######## Sensitivity analysis
npvVectors=[]
minMaxVectors=[]
minMaxPercent = 50 # the maximum and minimum percentage to consider
numLevels = 30 #the number of levels of discretization to consider
figSense = plt.figure(figsize=(18,14))
ax = figSense.add_subplot()

#Generate all keys list
allkeys=[]
allkeys=allkeys+list(Assumptions.keys())
allkeys=allkeys+list(Inputs['Vehicle'].keys())
allkeys=allkeys+list(Inputs['AGV'].keys())
allkeys=allkeys+['MissionLength','MaterialToMove','YearlyOperationDays']
allkeys.remove('dieselEnergy') #no need to handle sensitivity here
allkeys.remove('TechnologyReadiness') # is treated in a later sensitivity analysis
allkeys.remove('CompanyAcceptance') # is treated in a later sensitivity analysis
allkeys.remove('MissionSimilarity') # is treated in a later sensitivity analysis
allkeys.remove('MissionDeterminism') # is treated in a later sensitivity analysis

df_slope = pd.DataFrame(columns=['slope'])

#Iterate through all keys to perform the sensitivitiy analysis
for key in allkeys:
    minMaxVec,minMaxVals,npvVec=SenstivityAnalysis(key,minMaxPercent,numLevels,Assumptions,Inputs)
    npvVectors.append(npvVec)
    minMaxVectors.append(minMaxVals)
    ax.plot(minMaxVec*100,npvVec,label=key+'from %.2f to %.2f' % (minMaxVals[0],minMaxVals[1]))
    plt.text(minMaxVec[-1]*100, npvVec[-1], key)
    df_slope.at[key,'slope']=np.round((npvVec[-1]-npvVec[0])/2*minMaxPercent,2)


#Plot Sensitivity graph
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5)
ax.set_title('Sensitivity to % Change from Baseline')
ax.set_xlabel("% Change from Baseline")
ax.set_ylabel("NPV (EUR)")

#Slope table
df_slope['abs_slope']=np.abs(df_slope['slope'])
df_slope.sort_values('abs_slope', inplace=True,ascending=False)
df_slope['rank']=np.linspace(1,len(df_slope),len(df_slope))
df_slope.drop(columns=['abs_slope'], inplace=True)

figSlope = plt.figure(figsize=(12,12))
ax = figSlope.add_subplot()
ax.axis('off')
table = pd.plotting.table(ax, df_slope.head(10).round(2), loc='center',
                          cellLoc='center', colWidths=list([.3, .3]))
ax.set_title('Ranking of most sensitive parameters and their slopes')


########## Mission analysis 

minMaxVec = np.linspace(0.1,1,10) # build the sensitivity range
figMissionSense = plt.figure(figsize=(22,14))
ax = figMissionSense.add_subplot()
#Generate all keys list
MissionKeys=['TechnologyReadiness','CompanyAcceptance','MissionSimilarity','MissionDeterminism']

figModelMission, axsModel = plt.subplots(2, 2,figsize=(14,14))


for key in MissionKeys:
    origVal=Assumptions[key]
    origSpeed=Inputs['AGV']['AGVAverageSpeed']
    origDisengagements=Inputs['AGV']['AGVDisengagementPerKm']
    origTimePerDisengagement=Inputs['AGV']['AGVDisengagementTime']
    npvVectorsMission=[]
    speedVecMission=[]
    disTimeMission=[]
    disPerKmMission=[]
    minMaxKey=[]
    for perc in minMaxVec:
        Assumptions[key]=perc # step through the values from 0.1 up to 1
        if key=='TechnologyReadiness': #if the parameter is tech readiness, multiply by 10
            Assumptions[key]=Assumptions[key]*10
        minMaxKey.append(Assumptions[key])
        ModAverageSpeed,ModDisengagementsPerKm,ModTimePerDisengagement= ModelAGVMission(Assumptions,Inputs)
        Inputs['AGV']['AGVAverageSpeed']=ModAverageSpeed
        Inputs['AGV']['AGVDisengagementPerKm']=ModDisengagementsPerKm
        Inputs['AGV']['AGVDisengagementTime']=ModTimePerDisengagement
        outputsMission=ModelAGVUseCase(Assumptions,Inputs)
        npvVectorsMission.append(outputsMission['npv'])
        speedVecMission.append(ModAverageSpeed)
        disTimeMission.append(ModTimePerDisengagement)
        disPerKmMission.append(ModDisengagementsPerKm)
        Inputs['AGV']['AGVAverageSpeed']=origSpeed #return the value to its original value
        Inputs['AGV']['AGVDisengagementPerKm']=origDisengagements #return the value to its original value
        Inputs['AGV']['AGVDisengagementTime']=origTimePerDisengagement #return the value to its original value
        Assumptions[key]=origVal #return the value to its original value
    axsModel[0, 0].plot(minMaxVec, speedVecMission)
    axsModel[0, 0].plot(minMaxVec, origSpeed*np.ones([len(minMaxVec)]),'k--')
    axsModel[0, 0].set_title('Ave. Speed')
    axsModel[0, 0].set_xlabel('Level')
    axsModel[0, 0].set_ylabel('km/hr')
    axsModel[0, 1].plot(minMaxVec, disTimeMission)
    axsModel[0, 1].plot(minMaxVec, origTimePerDisengagement*np.ones([len(minMaxVec)]),'k--')
    axsModel[0, 1].set_title('Dis. Time')
    axsModel[0, 1].set_xlabel('Level')
    axsModel[0, 1].set_ylabel('min')
    axsModel[1, 0].plot(minMaxVec, disPerKmMission)
    axsModel[1, 0].plot(minMaxVec, origDisengagements*np.ones([len(minMaxVec)]),'k--')
    axsModel[1, 0].set_title('Dis./km')
    axsModel[1, 0].set_xlabel('Level')
    axsModel[1, 0].set_ylabel('Number')
    axsModel[1, 1].plot(minMaxVec, np.zeros([len(minMaxVec)]),label=key)
    axsModel[1, 1].legend(loc=2)
    axsModel[1, 1].axis('off')
        
    ax.plot(minMaxVec,npvVectorsMission,label=key+' from %.2f to %.2f' % (minMaxKey[0],minMaxKey[-1]))

axsModel[1, 1].plot(minMaxVec, np.zeros([len(minMaxVec)]),label='Baseline')
ax.plot(minMaxVec,outputsBaseline['npv']*np.ones([len(minMaxVec)]),'k--',label='Baseline') #add the baseline case for reference
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5)
ax.set_title('Sensitivity to Model input assumptions')
ax.set_xlabel("Input Value")
ax.set_ylabel("NPV (EUR)")

# Save results
pp = PdfPages('AGVUseCaseModelResults.pdf')
pp.savefig(figs[0])
pp.savefig(figs[1])
pp.savefig(figs[2])
pp.savefig(figSense)
pp.savefig(figSlope)
#can add additional modified cases here
#CHEAPER AGV
pp.savefig(figsCheaper[0])
pp.savefig(figsCheaper[1])
pp.savefig(figsCheaper[2])
#SLOW VEHICLE
pp.savefig(figsSlower[0])
pp.savefig(figsSlower[1])
pp.savefig(figsSlower[2])

pp.savefig(figModelMission)
pp.savefig(figMissionSense)
pp.close()











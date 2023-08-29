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
import numpy_financial as npf
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
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
YearsOfOperation=7 #Years that the robotic system is in operation
# Technology Readiness
TechnologyReadiness = 5
# Company Acceptance
CompanyAcceptance = 0.7
# Mission Similarity
MissionSimilarity = 0.8
# Mission Determinism
MissionDeterminism = 0.6

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
VehicleAverageSpeed=12 #km/hr
VehicleMaterialCapacity = 40 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
VehicleMaxShiftLength = 8 #hrs max which the vehicle can operate
VehicleCost=74000 #EUR
VehicleEnergyConsumption = 6.5 #L/100km
OperatorHourlyWage = 51 #EUR/hr
VehicleMaintenance = 120 #EUR/month
VehicleEOLCost = 1800 #EUR for end of life disposal

##  CURRENT AGV use inputs
AGVAverageSpeed= 3 #km/hr (including all stop and blocked time caused by obstacles)
AGVChargeRate= 3 #kW
AGVMaterialCapacity = 20 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
AGVEnergyConsumption = 0.14 #kWh/km
AGVMaxShiftLength = 24 #if the AGV is unable to operate 24/7, an additional penalty can be added here
AGVDataUse = 4 #MB/day
AGVCost = 115000 #EUR/vehicle
AGVDisengagementPerKm = 0.01 #disengagements per driven km
AGVDisengagementTime = 5 #minutes per disengagement
AGVMaintenance = 200 #EUR/month
AGVEOLCost = 4000 #EUR for end of life disposal
########### COPY END ############

"""

########### INSERT START ############
#  CURRENT Mission Inputs
MissionLength=2 #km driven per misson round moving material
MaterialToMove=200 #amount of material (kg, m^3 etc) required to be moved from A to B for the mission
YearlyOperationDays = 212 #operating days per year. Note: differentiate availability for AGV vs human using max shift length

#  CURRENT Operator driven vehicle use inputs
VehicleAverageSpeed=12 #km/hr
VehicleMaterialCapacity = 40 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
VehicleMaxShiftLength = 8 #hrs max which the vehicle can operate
VehicleCost=74000 #EUR
VehicleEnergyConsumption = 6.5 #L/100km
OperatorHourlyWage = 51 #EUR/hr
VehicleMaintenance = 120 #EUR/month
VehicleEOLCost = 1800 #EUR for end of life disposal

#  CURRENT AGV use inputs
AGVAverageSpeed= 3 #km/hr (including all stop and blocked time caused by obstacles)
AGVChargeRate= 3 #kW
AGVMaterialCapacity = 20 #amount of material (kg, m^3 etc) which can be moved from A to B for the mission
AGVEnergyConsumption = 0.14 #kWh/km
AGVMaxShiftLength = 24 #if the AGV is unable to operate 24/7, an additional penalty can be added here
AGVDataUse = 4 #MB/day
AGVCost = 115000 #EUR/vehicle
AGVDisengagementPerKm = 0.01 #disengagements per driven km
AGVDisengagementTime = 5 #minutes per disengagement
AGVMaintenance = 200 #EUR/month
AGVEOLCost = 4000 #EUR for end of life disposal
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
AGV['AGVAverageSpeed']=AGVAverageSpeed
AGV['AGVChargeRate']=AGVChargeRate
AGV['AGVMaterialCapacity']=AGVMaterialCapacity
AGV['AGVEnergyConsumption']=AGVEnergyConsumption
AGV['AGVMaxShiftLength']=AGVMaxShiftLength
AGV['AGVDataUse']=AGVDataUse
AGV['AGVCost']=AGVCost
AGV['AGVDisengagementPerKm']=AGVDisengagementPerKm
AGV['AGVDisengagementTime']=AGVDisengagementTime
AGV['AGVMaintenance']=AGVMaintenance
AGV['AGVEOLCost']=AGVEOLCost
Inputs['AGV']=AGV


def ModelAGVMission(Assumptions,Inputs):
    """This function enables the modeling of AGV speed and disengagement rates
    to enable accurate project costs and therefore profitability
    Inputs:
        MissionLength= distance traveled in one round
        MaterialToMove= amount of material required to be moved per round
        AGVMaterialCapacity= amount of material capable of being moved
    Outputs:
        AverageSpeed= Average speed of one round, based on driving assumptions
        DisengagementsPerKm= Estimated number of disengagements per km
        TimePerDisengagement= Amount of time spent per disengagement
    
    Assumptions:
        The driving assumptions which guide this model are:
        TechnologyReadiness= maturity of the company producing the vehicles,
        which results in an estimation of the disengagements per km, and minutes 
        See:  https://github.com/erikwilhelm/AGVeval/blob/main/Excel/AGVUseCaseModel.xlsx 
        (TAB: TechMaturity)
        CompanyAcceptance= nature of the automated task - allowing an estimation
        of how much the human workers will collaborate and assist the robots mission
        MissionSimilarity= how similar are the tasks the robot runs, enabling it 
        to operate more rapidly
        MissionDeterminism=  how many stochastic elements are in the environment 
        (how busy is the overall environment) which indicates how difficult 
        the task will be for a robot
    """
    #Sanity check input assumptions
    Assumptions['CompanyAcceptance']=np.clip(Assumptions['CompanyAcceptance'],0.1,1) #restrict company acceptance between 0.1 and 1
    Assumptions['MissionSimilarity']=np.clip(Assumptions['MissionSimilarity'],0.1,1) #restrict mission similarity between 0.1 and 1
    Assumptions['MissionDeterminism']=np.clip(Assumptions['MissionDeterminism'],0.1,1) #restrict mission determinism between 0.1 and 1
    AverageSpeed= 0.5 * 0.7544 * np.exp(0.517*Assumptions['TechnologyReadiness']) * Assumptions['MissionSimilarity'] * Assumptions['MissionDeterminism'] #km/hr - average speed is half of the max speed, scaled by mission similarity and determinism
    TimePerDisengagement=243.16 * np.exp(-0.679*Assumptions['TechnologyReadiness']) #minutes
    ##Disengagements depend on technology readiness, scaled by mission determinism and company acceptance
    DisengagementsPerKm = 5.133 * np.exp(-1.083*Assumptions['TechnologyReadiness']) / Assumptions['CompanyAcceptance'] / Assumptions['MissionDeterminism'] #disengagements/km
    
    #Sanity check outputs
    AverageSpeed=np.clip(AverageSpeed,0.5,64) #km/hr
    DisengagementsPerKm=np.clip(DisengagementsPerKm,0.0008,2) #km/hr
    TimePerDisengagement=np.clip(TimePerDisengagement,0.5,120) #minutes
    
    return AverageSpeed,DisengagementsPerKm,TimePerDisengagement



def ModelAGVUseCase(Assumptions,Inputs):
    #Sanity check input assumptions
    Inputs['YearlyOperationDays']=np.clip(Inputs['YearlyOperationDays'],1,365) #restrict operation days to the max days in a year
    Assumptions['dieselEnergy']=np.clip(Assumptions['dieselEnergy'],0.95,0.97) #restrict diesel energy to the max energy available
    
    ## HUMAN operated vehicle
    # Vehicle mission running
    VehicleDailyMissions=np.round(Inputs['MaterialToMove']/Inputs['Vehicle']['VehicleMaterialCapacity']) #number of missions driven per day
    VehicleDailyDistance = Inputs['MissionLength'] * VehicleDailyMissions #km/day
    VehicleDailyTime = VehicleDailyDistance/Inputs['Vehicle']['VehicleAverageSpeed'] #hr/day
    NumberOfVehicles=np.ceil(VehicleDailyTime/Inputs['Vehicle']['VehicleMaxShiftLength']) #Number of Vehicles needed to acheive mission
    # Human Cost inputs
    VehiclePurchasePrice=NumberOfVehicles * Inputs['Vehicle']['VehicleCost'] #EUR
    # Energy
    VehicleEnergyCost= Inputs['Vehicle']['VehicleEnergyConsumption']/100 * Assumptions['dieselPrice'] * VehicleDailyDistance * Inputs['YearlyOperationDays'] #EUR/year
    # Operator cost
    VehicleOperatorCost = VehicleDailyTime * Inputs['Vehicle']['OperatorHourlyWage'] * Inputs['YearlyOperationDays'] #EUR/year
    
    VehicleAnnualOperationCost = VehicleEnergyCost+VehicleOperatorCost
    VehicleAnnualMaintenanceCost = Inputs['Vehicle']['VehicleMaintenance'] *12 #EUR/year
    VehicleAnnualCost = NumberOfVehicles * (VehicleAnnualOperationCost + VehicleAnnualMaintenanceCost)
    VehicleEndOfLifeCost= NumberOfVehicles * Inputs['Vehicle']['VehicleEOLCost'] #EUR
    
    ## AGV 
    # AGV missions
    AGVDailyMissions = np.round(Inputs['MaterialToMove']/Inputs['AGV']['AGVMaterialCapacity']) #number of missions driven per day
    AGVDailyDistance = Inputs['MissionLength'] * AGVDailyMissions #km/day
    AGVDailyEnergy = AGVDailyDistance * Inputs['AGV']['AGVEnergyConsumption'] #kWh
    AGVDailyTime = AGVDailyDistance/Inputs['AGV']['AGVAverageSpeed'] + AGVDailyEnergy/Inputs['AGV']['AGVChargeRate'] #hours required by the AGV to acheive its mission
    #Number of AGVs needed to acheive mission
    NumberOfAGVs=np.ceil(AGVDailyTime/Inputs['AGV']['AGVMaxShiftLength'])
    
    ## AGV cost inputs
    AGVPurchasePrice = NumberOfAGVs * Inputs['AGV']['AGVCost'] #EUR
    # Energy
    AGVEnegyCost = Assumptions['electricityPrice'] * Inputs['AGV']['AGVEnergyConsumption'] * AGVDailyDistance * Inputs['YearlyOperationDays'] #EUR/year
    # Data Carriage
    AGVDataCost = Assumptions['dataCarriage'] * Inputs['AGV']['AGVDataUse'] * Inputs['YearlyOperationDays'] #EUR/year
    # Human intervention (disengagements)
    AGVCostPerDisengagement = Inputs['AGV']['AGVDisengagementTime'] / 60 * Inputs['Vehicle']['OperatorHourlyWage']
    AGVDisengagementCost = Inputs['AGV']['AGVDisengagementPerKm'] * AGVCostPerDisengagement * AGVDailyDistance * Inputs['YearlyOperationDays'] #EUR/year
    # Total costs
    AGVAnnualOperationCost = AGVEnegyCost + AGVDataCost + AGVDisengagementCost #EUR/year
    AGVAnnualMaintenanceCost = Inputs['AGV']['AGVMaintenance'] * 12 #EUR/year
    AGVAnnualCost = NumberOfAGVs * (AGVAnnualOperationCost + AGVAnnualMaintenanceCost)
    AGVEndOfLifeCost= NumberOfAGVs * Inputs['AGV']['AGVEOLCost'] #EUR
    
    
    #Initial investment price
    InvestmentCost = VehiclePurchasePrice - AGVPurchasePrice # EUR
    
    AnnualSavings = VehicleAnnualCost - AGVAnnualCost # EUR/year
    
    EndOfLifePrice = VehicleEndOfLifeCost - AGVEndOfLifeCost # EUR
    
    # Establish cash flows
    cashFlows = [InvestmentCost]+ [AnnualSavings] * (YearsOfOperation-1) + [AnnualSavings + EndOfLifePrice] 
    
    ## Return outputs
    #calculate the project net present value
    npv = npf.npv(discountRate, cashFlows)
    #calculate the project minimum yearly savings to be profitable
    minSavings=npf.pmt(discountRate,YearsOfOperation,InvestmentCost)
    #calculate the project payback period
    nper=npf.nper(discountRate, AnnualSavings, InvestmentCost)
    
    outputs={}
    outputs['AnnualSavings'] = AnnualSavings
    outputs['CumulativeVehicleAnnualCost'] = VehicleAnnualOperationCost * Assumptions['YearsOfOperation']
    outputs['CumulativeAGVAnnualCost'] = AGVAnnualOperationCost * Assumptions['YearsOfOperation']
    outputs['cashFlows'] = cashFlows
    outputs['npv'] = npv
    outputs['minSavings'] = minSavings
    outputs['nper'] = nper
    return outputs


def PlotCaseResults(Assumptions,Inputs,outputs,CaseName):
    #plots the basic use case model outputs
    figEcon,axes = plt.subplots(2,figsize=(10, 10))
    ax = axes[0]
    
    figEcon.subplots_adjust(top=0.85)
    BaselineTotal=Inputs['Vehicle']['VehicleCost']+outputs['CumulativeVehicleAnnualCost']+Inputs['Vehicle']['VehicleEOLCost']
    AGVTotal=Inputs['AGV']['AGVCost']+outputs['CumulativeAGVAnnualCost']+Inputs['AGV']['AGVEOLCost']
    totalCosts=[BaselineTotal,AGVTotal]
    ax.bar(['Vehicle','AGV'],totalCosts)
    ax.set_title('%s Comparison of Undiscounted Lifetime costs' % CaseName)
    ax.set_ylabel('CHF Lifetime Cost (no discounting)')
    ax2=axes[1]
    ax2.axis([0, 12, 0, 12])
    ax2.text(0,10, "%s Discounted net present value of the investment: %3.2f EUR" % (CaseName,outputs['npv']), fontsize=15)
    
    if outputs['npv'] < 0: 
        ax2.text(0,7,"%s Project has a negative net present value,\n savings must be %3.2f EUR/year to be profitable \n presently the savings are only %3.2f EUR/year" % (CaseName, np.abs(outputs['minSavings']),outputs['AnnualSavings']), fontsize=15)
    
    ax2.text(0,3,"%s Return on the robotic investment requires: %3.2f years" % (CaseName,outputs['nper']), fontsize=15)
    ax2.axis('off')
    
    # Plot the cash flows for the project
    plotDF = pd.DataFrame()
    plotDF['cashFlows'] = outputs['cashFlows']
    plotDF['CFpos'] = plotDF['cashFlows'] > 0
    figFlow = plt.figure()
    ax = figFlow.add_subplot()
    plotDF['cashFlows'].plot(ax = ax, kind='bar',
                                  color=plotDF.CFpos.map({True: 'k', False: 'r'}))
    ax.set_xlabel("Operation Year")
    ax.set_ylabel("EUR")
    ax.set_title("%s Project Cash Flows" % CaseName)
    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(np.round(start/1000)*1000, np.round(end/1000)*1000, 5000))
    figFlow = plt.gcf()
    figFlow.set_figwidth(15)
    
    # Plot the fraction of the costs for the baseline and autonomous case
    figShare, (ax1,ax2) = plt.subplots(1,2,figsize=(14,6)) #ax1,ax2 refer to your two pies
    labels = ['VehiclePurchasePrice', 'CumulativeVehicleAnnualCost', 'VehicleEndOfLifeCost']
    costsBaseline = [Inputs['Vehicle']['VehicleCost'], outputs['CumulativeVehicleAnnualCost'], Inputs['Vehicle']['VehicleEOLCost']]
    ax1.pie(costsBaseline, labels=labels, autopct='%1.1f%%')
    ax1.set_title('%s Baseline (Human operator) Lifetime Cost Share' % CaseName)
    costsAGV = [Inputs['AGV']['AGVCost'], outputs['CumulativeAGVAnnualCost'], Inputs['AGV']['AGVEOLCost']]
    ax2.pie(costsAGV, labels=labels, autopct='%1.1f%%')
    ax2.set_title('%s Autonomous Ground Vehicle Lifetime Costs Share' % CaseName)
    figs=[figEcon,figFlow,figShare]
    return figs
    

def SenstivityAnalysis(key,minMaxPerc,numLevels,Assumptions,Inputs):
    #performs a sensitivity analysis on the variable in the dict 'key' in either the assumptions or inputs dict
    #Inputs: 
    # key - the name of the dictionary key in the inputs and assumptinos for which the analysis is performed
    # minMaxPerc - scalar value of the minimum / maximum percent to vary the key
    # numLevels - the discretization of the analysis
    # Assumptions - dictionary of assumptions to be tested
    # Inputs - dictionary of the inputs to be tested
    #Outputs:
    # minMaxVec - vector of minMax percentages based on the inputs
    # npvVec - vector of npv calculated across the range specified by minMaxPerc
    
    npvVec = []
    valVec= []
    minMaxVec = np.linspace(-minMaxPerc,minMaxPerc,numLevels)/100 # build the sensitivity range
    minMaxVec = np.insert(minMaxVec,int(numLevels/2),0)
    if key in Assumptions:
        origKey = Assumptions[key] 
    elif key in Inputs:
        origKey = Inputs[key] 
    elif key in Inputs['Vehicle']:
        origKey = Inputs['Vehicle'][key]
    elif key in Inputs['AGV']:
        origKey = Inputs['AGV'][key]
    else:
        raise Exception('Key not found, check input and assumption variable names')

    for perc in minMaxVec: #iterate all inputs
        if key in Assumptions:
            Assumptions[key] = origKey * (1+perc)
            valVec.append(Assumptions[key])
        elif key in Inputs:
            Inputs[key] = origKey * (1+perc)
            valVec.append(Inputs[key])
        elif key in Inputs['Vehicle']:
            Inputs['Vehicle'][key] = origKey * (1+perc)
            valVec.append(Inputs['Vehicle'][key])
        elif key in Inputs['AGV']:
            Inputs['AGV'][key] = origKey * (1+perc)
            valVec.append(Inputs['AGV'][key])

        outputs=ModelAGVUseCase(Assumptions,Inputs)
        npvVec.append(outputs['npv'])
        minMaxVals=[min(valVec),max(valVec)]

    if key in Assumptions:
        Assumptions[key] = origKey
    elif key in Inputs:
        Inputs[key] = origKey
    elif key in Inputs['Vehicle']:
        Inputs['Vehicle'][key] = origKey
    elif key in Inputs['AGV']:
        Inputs['AGV'][key] = origKey
        
    return minMaxVec,minMaxVals,npvVec


##### MAIN CODE SECTION #####
##### BASELINE calculation
outputs=ModelAGVUseCase(Assumptions,Inputs)
## Plot the BASELINE results
figs=PlotCaseResults(Assumptions,Inputs,outputs,'BASELINE')

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
figSense = plt.figure(figsize=(14,14))
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
figMissionSense = plt.figure(figsize=(14,14))
ax = figMissionSense.add_subplot()
#Generate all keys list
MissionKeys=['TechnologyReadiness','CompanyAcceptance','MissionSimilarity','MissionDeterminism']

figModelMission, axsModel = plt.subplots(2, 2,figsize=(14,14))


for key in MissionKeys:
    origVal=Assumptions[key]
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
        origSpeed=Inputs['AGV']['AGVAverageSpeed']
        origDisengagements=Inputs['AGV']['AGVDisengagementPerKm']
        origTimePerDisengagement=Inputs['AGV']['AGVDisengagementTime']
        Inputs['AGV']['AGVAverageSpeed']=ModAverageSpeed
        Inputs['AGV']['AGVDisengagementPerKm']=ModDisengagementsPerKm
        Inputs['AGV']['AGVDisengagementTime']=ModTimePerDisengagement
        outputsMission=ModelAGVUseCase(Assumptions,Inputs)
        npvVectorsMission.append(outputsMission['npv'])
        speedVecMission.append(ModAverageSpeed)
        disTimeMission.append(ModDisengagementsPerKm)
        disPerKmMission.append(ModTimePerDisengagement)
        Inputs['AGV']['AGVAverageSpeed']=origSpeed
        Inputs['AGV']['AGVDisengagementPerKm']=origDisengagements
        Inputs['AGV']['AGVDisengagementTime']=origTimePerDisengagement
        Assumptions[key]=origVal #return the value to its original value
    axsModel[0, 0].plot(minMaxVec, speedVecMission)
    axsModel[0, 0].set_title('Ave. Speed')
    axsModel[0, 0].set_xlabel('Level')
    axsModel[0, 0].set_ylabel('km/hr')
    axsModel[0, 1].plot(minMaxVec, disTimeMission)
    axsModel[0, 1].set_title('Dis. Time')
    axsModel[0, 1].set_xlabel('Level')
    axsModel[0, 1].set_ylabel('min')
    axsModel[1, 0].plot(minMaxVec, disPerKmMission)
    axsModel[1, 0].set_title('Dis./km')
    axsModel[1, 0].set_xlabel('Level')
    axsModel[1, 0].set_ylabel('Number')
    axsModel[1, 1].plot(minMaxVec, np.zeros([len(minMaxVec)]),label=key)
    axsModel[1, 1].legend(loc=2)
    axsModel[1, 1].axis('off')
        
    ax.plot(minMaxVec,npvVectorsMission,label=key+' from %.2f to %.2f' % (minMaxKey[0],minMaxKey[-1]))



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
pp.close()











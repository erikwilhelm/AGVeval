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
        See:  https://github.com/erikwilhelm/AGVeval/blob/main/Excel/AGVUseCaseModel.xlsx 
        (TAB: MissionModel)
        MissionSimilarity= how similar are the tasks the robot runs, enabling it 
        to operate more rapidly
        See:  https://github.com/erikwilhelm/AGVeval/blob/main/Excel/AGVUseCaseModel.xlsx 
        (TAB: MissionModel)
        MissionDeterminism=  how many stochastic elements are in the environment 
        (how busy is the overall environment) which indicates how difficult 
        the task will be for a robot
        See:  https://github.com/erikwilhelm/AGVeval/blob/main/Excel/AGVUseCaseModel.xlsx 
        (TAB: MissionModel)
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
    DisengagementsPerKm=np.clip(DisengagementsPerKm,0.0008,2) # dis./km
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
    AGVLeasingPrice = NumberOfAGVs * Inputs['AGV']['AGVLeasing'] #EUR
    if AGVPurchasePrice>0 and AGVLeasingPrice>0:
        warnings.warn("Warning: AGV purchase and leasing price are both set, only one should be set")
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
    AGVAnnualCost = NumberOfAGVs * (AGVAnnualOperationCost + AGVAnnualMaintenanceCost) + AGVLeasingPrice
    AGVEndOfLifeCost= NumberOfAGVs * Inputs['AGV']['AGVEOLCost'] #EUR
    
    
    #Initial investment price
    if VehiclePurchasePrice<AGVPurchasePrice:
        InvestmentCost = VehiclePurchasePrice - AGVPurchasePrice # EUR
    else:
        InvestmentCost = 0 # EUR Handles the case where AGVs are leased, and therefore not part of the overall cost
    
    AnnualSavings = VehicleAnnualCost - AGVAnnualCost # EUR/year
    
    EndOfLifePrice = VehicleEndOfLifeCost - AGVEndOfLifeCost # EUR
    
    # Establish cash flows
    
    cashFlows = [InvestmentCost]+ [AnnualSavings] * (int(Assumptions['YearsOfOperation'])-1) + [AnnualSavings + EndOfLifePrice] 

    ## Return outputs
    #calculate the project net present value
    npv = npf.npv(Assumptions['discountRate'], cashFlows)
    #calculate the project minimum yearly savings to be profitable
    minSavings=npf.pmt(Assumptions['discountRate'],Assumptions['YearsOfOperation'],InvestmentCost)
    #calculate the project payback period
    nper=npf.nper(Assumptions['discountRate'], AnnualSavings, InvestmentCost)
    
    outputs={}
    outputs['AnnualSavings'] = AnnualSavings
    outputs['CumulativeVehicleAnnualCost'] = VehicleAnnualOperationCost * Assumptions['YearsOfOperation']
    outputs['CumulativeAGVAnnualCost'] = AGVAnnualOperationCost * Assumptions['YearsOfOperation']
    outputs['cashFlows'] = cashFlows
    outputs['npv'] = npv
    outputs['minSavings'] = minSavings
    outputs['nper'] = nper
    outputs['numRobots'] = NumberOfAGVs
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
    
    ax2.text(0,5, "%s Number of robots to match human performance: %d units" % (CaseName,outputs['numRobots']), fontsize=15)
    
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

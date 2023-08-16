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
## Assumptions
# Financial
discountRate = 0.05; # Five percent per annum
# Energy
electricityPrice = 0.23 # EUR/kWh
dieselPrice = 1.79 #EUR/L
dieselEnergy = 9.6 # kWh/L
# Data
dataCarriage = 0.7 #EUR/MB
# Lifecycle
YearsOfOperation=7 #Years that the robotic system is in operation

## Inputs
# Mission Inputs
MissionLength=2 #km driven per misson round
DailyMissions=15 #number of missions driven per day (TODO - calculate this from load factor)
YearlyOperationDays = 212 #operating days per year (TODO - differentiate operating days for AGV vs human)

#Operator driven vehicle use inputs
VehicleAverageSpeed=20 #km/hr
VehicleOperatingTime = MissionLength*DailyMissions/VehicleAverageSpeed #hr/day

## Operator driven vehicle use inputs
# Human Cost inputs
VehiclePurchasePrice=74000 #EUR
# Energy
VehicleEnergyConsumption = 6.5 #L/100km
VehicleEnergyCost= VehicleEnergyConsumption/100 * dieselPrice*MissionLength*DailyMissions*YearlyOperationDays #EUR/year
# Operator cost
OperatorHourlyWage = 21 #EUR/hr
VehicleOperatorCost = VehicleOperatingTime * OperatorHourlyWage * YearlyOperationDays #EUR/year

VehicleAnnualOperationCost = VehicleEnergyCost+VehicleOperatorCost
VehicleAnnualMaintenanceCost = 120 *12 #EUR/year
VehicleAnnualCost = VehicleAnnualOperationCost + VehicleAnnualMaintenanceCost
VehicleEndOfLifeCost=1800 #EUR

## AGV cost inputs
AGVPurchasePrice=115000 #EUR
# Energy
AGVEnergyConsumption=0.14 #kWh/km
AGVEnegyCost=electricityPrice*AGVEnergyConsumption*MissionLength*DailyMissions*YearlyOperationDays #EUR/year
# Data Carriage
AGVDataUse = 4 #MB/day
AGVDataCost= dataCarriage*AGVDataUse*YearlyOperationDays #EUR/year
# Human intervention (disengagements)
AGVDisengagementPerKm = 0.01 #disengagements per driven km
AGVDisengagementTime = 5 # minutes per disengagement
AGVCostPerDisengagement = AGVDisengagementTime / 60 * OperatorHourlyWage
AGVDisengagementCost = AGVDisengagementPerKm*AGVCostPerDisengagement*MissionLength*DailyMissions*YearlyOperationDays #EUR/year
# Total costs
AGVAnnualOperationCost = AGVEnegyCost+AGVDataCost+AGVDisengagementCost #EUR/year
AGVAnnualMaintenanceCost = 200*12 #EUR/year
AGVAnnualCost = AGVAnnualOperationCost + AGVAnnualMaintenanceCost
AGVEndOfLifeCost=4000 #EUR


#AGV use inputs
AGVAverageSpeed=6 #km/hr
AGVChargeRate=3 #kW

#Number of AGVs needed to replace a human driver
NumberOfAGVs=1 #TODO - calculate from load factor


#Initial investment price
InvestmentCost = VehiclePurchasePrice - NumberOfAGVs*AGVPurchasePrice # EUR

AnnualSavings = VehicleAnnualCost - NumberOfAGVs*AGVAnnualCost # EUR/year

EndOfLifePrice = VehicleEndOfLifeCost - NumberOfAGVs*AGVEndOfLifeCost # EUR

# Establish cash flows
cashFlows = [InvestmentCost]+ [AnnualSavings] * (YearsOfOperation-1) + [AnnualSavings + EndOfLifePrice] 

## Outputs
figEcon = plt.figure()
ax = figEcon.add_subplot()
ax.axis([0, 10, 0, 10])
figEcon.subplots_adjust(top=0.85)
#calculate the project net present value
npv = npf.npv(discountRate, cashFlows)
ax.text(0, 10, "Net present value of the investment:%3.2f EUR" % npv, fontsize=15)
#calculate the project minimum yearly savings to be profitable
if npv < 0: 
    minSavings=npf.pmt(discountRate,YearsOfOperation,InvestmentCost)
    ax.text(0, 8,"Project has a negative net present value,\n savings must be %3.2f EUR/year to be profitable" % np.abs(minSavings), fontsize=15)
#calculate the project payback period
ax.text(0, 6,"Return on the \n robotic investment requires: %3.2f years" % npf.nper(discountRate, -AnnualSavings, InvestmentCost), fontsize=15)
plt.axis('off')

# Plot the cash flows for the project
plotDF = pd.DataFrame()
plotDF['cashFlows'] = cashFlows
plotDF['CFpos'] = plotDF['cashFlows'] > 0
figFlow = plt.figure()
ax = figFlow.add_subplot()
plotDF['cashFlows'].plot(ax = ax, kind='bar',
                              color=plotDF.CFpos.map({True: 'k', False: 'r'}))
ax.set_xlabel("Operation Year")
ax.set_ylabel("EUR")
start, end = ax.get_ylim()
ax.yaxis.set_ticks(np.arange(np.round(start/1000)*1000, np.round(end/1000)*1000, 5000))
figFlow = plt.gcf()
figFlow.set_figwidth(15)

# Plot the fraction of the costs for the baseline and autonomous case
figShare, (ax1,ax2) = plt.subplots(1,2,figsize=(14,6)) #ax1,ax2 refer to your two pies
labels = ['VehiclePurchasePrice', 'CumulativeVehicleAnnualCost', 'VehicleEndOfLifeCost']
costsBaseline = [VehiclePurchasePrice, VehicleAnnualCost*YearsOfOperation, VehicleEndOfLifeCost]
ax1.pie(costsBaseline, labels=labels, autopct='%1.1f%%')
ax1.set_title('Baseline (Human operator)')

costsAGV = [NumberOfAGVs*AGVPurchasePrice, NumberOfAGVs*AGVAnnualCost*YearsOfOperation, NumberOfAGVs*AGVEndOfLifeCost]
ax2.pie(costsAGV, labels=labels, autopct='%1.1f%%')
ax2.set_title('Autonomous Ground Vehicle')


# Sensitivity
#TODO - add sensitivity analysis here





pp = PdfPages('AGVUseCaseModelResults.pdf')
pp.savefig(figEcon)
pp.savefig(figFlow)
pp.savefig(figShare)
pp.close()







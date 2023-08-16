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
import numpy_financial as npf


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
AGVPurchasePrice=155000 #EUR
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



# Outputs
npv = npf.npv(discountRate, cashFlows)

print("Net present value of the investment:%3.2f" % npv)

if npv < 0: 
    minSavings=npf.pmt(discountRate,YearsOfOperation,InvestmentCost)
    print("Project has a negative net present value, savings must be %3.2f per year to be profitable" % np.abs(minSavings))


# Sensitivity
#TODO - add sensitivity analysis here
print("Number of years to return on the robotic investment:%3.2f" % npf.nper(discountRate, -AnnualSavings, InvestmentCost))


















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
from typing import List
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from AGVUseCaseFunctions import (
    Assumption,
    Input,
    Vehicle,
    Agv,
    ModelAGVMission,
    ModelAGVUseCase,
    PlotCaseResults,
    SenstivityAnalysis,
    read_input_values_from_excel,
    read_assumption_values_from_excel,
)
from dataclasses import fields

plt.close("all")
plt.rcParams["axes.autolimit_mode"] = "round_numbers"

## Assumptions
# Financial
DISCOUNT_RATE = 0.05  # Five percent per annum
# Energy
ELECTRICITY_PRICE = 0.23  # EUR/kWh
DIESEL_PRICE = 1.79  # EUR/L
DIESEL_ENERGY = 9.6  # kWh/L
# Data
DATA_CARRIAGE = 0.7  # EUR/MB
# Lifecycle
YEARS_OF_OPERATION = 7.0  # Years that the robotic system is in operation
# Technology Readiness
TECHNOLOGY_READINESS = 8  # Technology validated in relevant environment (industrially relevant environment in the case of key enabling technologies)
# Company Acceptance
COMPANY_ACCEPTANCE = 0.7  # represents a 'good' level of AGV acceptance within a company
# Mission Similarity
MISSION_SIMILARITY = 0.8  # represents an 'excellent' level of mission similarity
# Mission Determinism
MISSION_DETERMINISM = 0.6  # represents a 'sufficient' level of mission determinism


assumptions = Assumption(
    discount_rate=DISCOUNT_RATE,
    electricity_price=ELECTRICITY_PRICE,
    diesel_price=DIESEL_PRICE,
    diesel_energy=DIESEL_ENERGY,
    data_carriage=DATA_CARRIAGE,
    years_of_operation=YEARS_OF_OPERATION,
    technology_readiness=TECHNOLOGY_READINESS,
    company_acceptance=COMPANY_ACCEPTANCE,
    mission_similarity=MISSION_SIMILARITY,
    mission_determinism=MISSION_DETERMINISM,
)

# FIXME: we need to discuss how we want to handle this
assumptions = read_assumption_values_from_excel("../Excel/AGVUseCaseModel.xlsx")


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
MissionLength = 2  # km driven per misson round moving material
MaterialToMove = 200  # amount of material (kg, m^3 etc) required to be moved from A to B for the mission
YearlyOperationDays = 212  # operating days per year. Note: differentiate availability for AGV vs human using max shift length

#  CURRENT Operator driven vehicle use inputs

VehicleCost = 74000  # EUR
VehicleEnergyConsumption = 6.5  # L/100km
OperatorHourlyWage = 51  # EUR/hr
VehicleMaintenance = 120  # EUR/month
VehicleEOLCost = 1800  # EUR for end of life disposal
VehicleAverageSpeed = 12  # km/hr
VehicleMaterialCapacity = 40  # amount of material (kg, m^3 etc) which can be moved from A to B for the mission
VehicleMaxShiftLength = 8  # hrs max which the vehicle can operate

#  CURRENT AGV use inputs
AGVCost = (
    115000  # EUR/vehicle  Note - set to zero if Leasing cost is set (Default 115000)
)
AGVLeasing = 0  # EUR/vehicle/year  Note - set to zero if AGV cost is set (Default 7000)
AGVMaintenance = 200  # EUR/month
AGVEOLCost = 4000  # EUR for end of life disposal
AGVAverageSpeed = 3  # km/hr (including all stop and blocked time caused by obstacles)
AGVChargeRate = 3  # kW
AGVDisengagementPerKm = 0.01  # disengagements per driven km
AGVDisengagementTime = 5  # minutes per disengagement
AGVMaterialCapacity = 20  # amount of material (kg, m^3 etc) which can be moved from A to B for the mission
AGVEnergyConsumption = 0.14  # kWh/km
AGVMaxShiftLength = (
    24  # if the AGV is unable to operate 24/7, an additional penalty can be added here
)
AGVDataUse = 4  # MB/day
########### INSERT END ############

### Structure Inputs and Assumptions
inputs = Input(
    mission_length=MissionLength,
    material_to_move=MaterialToMove,
    yearly_operation_days=YearlyOperationDays,
    vehicle=Vehicle(
        vehicle_cost=VehicleCost,
        vehicle_energy_consumption=VehicleEnergyConsumption,
        operator_hourly_wage=OperatorHourlyWage,
        vehicle_maintainance=VehicleMaintenance,
        vehicle_eol_cost=VehicleEOLCost,
        vehicle_average_speed=VehicleAverageSpeed,
        vehicle_material_capacity=VehicleMaterialCapacity,
        vehicle_max_shift_length=VehicleMaxShiftLength,
    ),
    agv=Agv(
        agv_cost=AGVCost,
        agv_leasing=AGVLeasing,
        agv_maintenance=AGVMaintenance,
        agv_eol_cost=AGVEOLCost,
        agv_average_speed=AGVAverageSpeed,
        agv_charge_rate=AGVChargeRate,
        agv_disengagement_per_km=AGVDisengagementPerKm,
        agv_disengagement_time=AGVDisengagementTime,
        agv_material_capacity=AGVMaterialCapacity,
        agv_energy_consumption=AGVEnergyConsumption,
        agv_max_shift_length=AGVMaxShiftLength,
        agv_data_use=AGVDataUse,
    ),
)

# FIXME: we need to discuss how we want to handle this
inputs = read_input_values_from_excel("../Excel/AGVUseCaseModel.xlsx")

##### MAIN CODE SECTION #####
##### BASELINE calculation
outputsBaseline = ModelAGVUseCase(assumptions, inputs)
## Plot the BASELINE results
figs = PlotCaseResults(assumptions, inputs, outputsBaseline, "BASELINE")

##### CHEAPER AGV calculation
inputs.agv.agv_cost = int(0.75 * inputs.agv.agv_cost)  # reduced AGV cost
outputsCheaper = ModelAGVUseCase(assumptions, inputs)
## Plot the CHEAPER AGV results
figsCheaper = PlotCaseResults(assumptions, inputs, outputsCheaper, "CHEAPER AGV")
inputs.agv.agv_cost = int(
    inputs.agv.agv_cost / 0.75
)  # return AGV cost to original value

###### SLOW VEHICLE calculation
inputs.vehicle.vehicle_average_speed = int(0.25 * inputs.vehicle.vehicle_average_speed)
outputsSlower = ModelAGVUseCase(assumptions, inputs)
## Plot the SLOW VEHICLE results
figsSlower = PlotCaseResults(assumptions, inputs, outputsSlower, "SLOW VEHICLE")
inputs.vehicle.vehicle_average_speed = int(
    inputs.vehicle.vehicle_average_speed / 0.25
)  # return vehicle speed back to original value

######## Sensitivity analysis
npvVectors = []
minMaxVectors = []
minMaxPercent = 50  # the maximum and minimum percentage to consider
numLevels = 30  # the number of levels of discretization to consider
figSense = plt.figure(figsize=(18, 14))
ax = figSense.add_subplot()

# Generate all keys list
allkeys: List[str] = []
allkeys = allkeys + list(map(lambda x: x.name, fields(assumptions)))
allkeys = allkeys + list(map(lambda x: x.name, fields(inputs.vehicle)))
allkeys = allkeys + list(map(lambda x: x.name, fields(inputs.agv)))
allkeys = allkeys + ["mission_length", "material_to_move", "yearly_operation_days"]
allkeys.remove("diesel_energy")  # no need to handle sensitivity here
allkeys.remove("technology_readiness")  # is treated in a later sensitivity analysis
allkeys.remove("company_acceptance")  # is treated in a later sensitivity analysis
allkeys.remove("mission_similarity")  # is treated in a later sensitivity analysis
allkeys.remove("mission_determinism")  # is treated in a later sensitivity analysis

df_slope = pd.DataFrame(columns=["slope"])

# Iterate through all keys to perform the sensitivitiy analysis
for key in allkeys:
    minMaxVec, minMaxVals, npvVec = SenstivityAnalysis(
        key, minMaxPercent, numLevels, assumptions, inputs
    )
    npvVectors.append(npvVec)
    minMaxVectors.append(minMaxVals)
    ax.plot(
        minMaxVec * 100,
        npvVec,
        label=key + "from %.2f to %.2f" % (minMaxVals[0], minMaxVals[1]),
    )
    plt.text(minMaxVec[-1] * 100, npvVec[-1], key)
    df_slope.at[key, "slope"] = np.round(
        (npvVec[-1] - npvVec[0]) / 2 * minMaxPercent, 2
    )


# Plot Sensitivity graph
box = ax.get_position()
ax.set_position((box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9))
ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5
)
ax.set_title("Sensitivity to % Change from Baseline")
ax.set_xlabel("% Change from Baseline")
ax.set_ylabel("NPV (EUR)")

# Slope table
df_slope["abs_slope"] = np.abs(df_slope["slope"])
df_slope.sort_values("abs_slope", inplace=True, ascending=False)
df_slope["rank"] = np.linspace(1, len(df_slope), len(df_slope))
df_slope.drop(columns=["abs_slope"], inplace=True)

figSlope = plt.figure(figsize=(12, 12))
ax = figSlope.add_subplot()
ax.axis("off")
table = pd.plotting.table(
    ax,
    df_slope.head(10).round(2),
    loc="center",
    cellLoc="center",
    colWidths=list([0.3, 0.3]),
)
ax.set_title("Ranking of most sensitive parameters and their slopes")


########## Mission analysis

minMaxVec = np.linspace(0.1, 1, 10)  # build the sensitivity range for acceptance params
minMaxVecTR = np.linspace(1, 9, 9)  # build the sensitivity range for technology readiness
figMissionSense = plt.figure(figsize=(22, 14))
ax = figMissionSense.add_subplot()
# Generate all keys list
MissionKeys = [
    "technology_readiness",
    "company_acceptance",
    "mission_similarity",
    "mission_determinism",
]

figModelMission, axsModel = plt.subplots(2, 2, figsize=(14, 14))


for key in MissionKeys:
    origVal = getattr(assumptions, key)
    origSpeed = inputs.agv.agv_average_speed
    origDisengagements = inputs.agv.agv_disengagement_per_km
    origTimePerDisengagement = inputs.agv.agv_disengagement_time
    npvVectorsMission = []
    speedVecMission = []
    disTimeMission = []
    disPerKmMission = []
    minMaxKey = []
    if (
        key == "technology_readiness"
        ):  
        for perc in minMaxVecTR:
            setattr(assumptions, key, perc)  # step through the values from 1 up to 9
            minMaxKey.append(getattr(assumptions, key))
            (
                ModAverageSpeed,
                ModDisengagementsPerKm,
                ModTimePerDisengagement,
            ) = ModelAGVMission(assumptions, inputs)
            inputs.agv.agv_average_speed = ModAverageSpeed
            inputs.agv.agv_disengagement_per_km = ModDisengagementsPerKm
            inputs.agv.agv_disengagement_time = ModTimePerDisengagement
            outputsMission = ModelAGVUseCase(assumptions, inputs)
            npvVectorsMission.append(outputsMission.npv)
            speedVecMission.append(ModAverageSpeed)
            disTimeMission.append(ModTimePerDisengagement)
            disPerKmMission.append(ModDisengagementsPerKm)
            inputs.agv.agv_average_speed = (
                origSpeed  # return the value to its original value
            )
            inputs.agv.agv_disengagement_per_km = (
                origDisengagements  # return the value to its original value
            )
            inputs.agv.agv_disengagement_time = (
                origTimePerDisengagement  # return the value to its original value
            )
            setattr(assumptions, key, origVal)  # return the value to its original value
        axsModel[0, 0].plot(minMaxVecTR/10, speedVecMission)
        axsModel[0, 0].plot(minMaxVecTR/10, origSpeed * np.ones([len(minMaxVecTR)]), "k--")
        axsModel[0, 0].set_title("Ave. Speed")
        axsModel[0, 0].set_xlabel("Level")
        axsModel[0, 0].set_ylabel("km/hr")
        axsModel[0, 1].plot(minMaxVecTR/10, disTimeMission)
        axsModel[0, 1].plot(
            minMaxVecTR/10, origTimePerDisengagement * np.ones([len(minMaxVecTR)]), "k--"
        )
        axsModel[0, 1].set_title("Dis. Time")
        axsModel[0, 1].set_xlabel("Level")
        axsModel[0, 1].set_ylabel("min")
        axsModel[1, 0].plot(minMaxVecTR/10, disPerKmMission)
        axsModel[1, 0].plot(
            minMaxVecTR/10, origDisengagements * np.ones([len(minMaxVecTR)]), "k--"
        )
        axsModel[1, 0].set_title("Dis./km")
        axsModel[1, 0].set_xlabel("Level")
        axsModel[1, 0].set_ylabel("Number")
        axsModel[1, 1].plot(minMaxVecTR/10, np.zeros([len(minMaxVecTR)]), label=key+'/10')
        axsModel[1, 1].legend(loc=2)
        axsModel[1, 1].axis("off")
        
        ax.plot(
            minMaxVecTR/10,
            npvVectorsMission,
            label=key + " from %.2f to %.2f" % (minMaxKey[0], minMaxKey[-1]),
        )
    else:
        for perc in minMaxVec:
            setattr(assumptions, key, perc)  # step through the values from 0.1 up to 1
            minMaxKey.append(getattr(assumptions, key))
            (
                ModAverageSpeed,
                ModDisengagementsPerKm,
                ModTimePerDisengagement,
            ) = ModelAGVMission(assumptions, inputs)
            inputs.agv.agv_average_speed = ModAverageSpeed
            inputs.agv.agv_disengagement_per_km = ModDisengagementsPerKm
            inputs.agv.agv_disengagement_time = ModTimePerDisengagement
            outputsMission = ModelAGVUseCase(assumptions, inputs)
            npvVectorsMission.append(outputsMission.npv)
            speedVecMission.append(ModAverageSpeed)
            disTimeMission.append(ModTimePerDisengagement)
            disPerKmMission.append(ModDisengagementsPerKm)
            inputs.agv.agv_average_speed = (
                origSpeed  # return the value to its original value
            )
            inputs.agv.agv_disengagement_per_km = (
                origDisengagements  # return the value to its original value
            )
            inputs.agv.agv_disengagement_time = (
                origTimePerDisengagement  # return the value to its original value
            )
            setattr(assumptions, key, origVal)  # return the value to its original value
        axsModel[0, 0].plot(minMaxVec, speedVecMission)
        axsModel[0, 0].plot(minMaxVec, origSpeed * np.ones([len(minMaxVec)]), "k--")
        axsModel[0, 0].set_title("Ave. Speed")
        axsModel[0, 0].set_xlabel("Level")
        axsModel[0, 0].set_ylabel("km/hr")
        axsModel[0, 1].plot(minMaxVec, disTimeMission)
        axsModel[0, 1].plot(
            minMaxVec, origTimePerDisengagement * np.ones([len(minMaxVec)]), "k--"
        )
        axsModel[0, 1].set_title("Dis. Time")
        axsModel[0, 1].set_xlabel("Level")
        axsModel[0, 1].set_ylabel("min")
        axsModel[1, 0].plot(minMaxVec, disPerKmMission)
        axsModel[1, 0].plot(
            minMaxVec, origDisengagements * np.ones([len(minMaxVec)]), "k--"
        )
        axsModel[1, 0].set_title("Dis./km")
        axsModel[1, 0].set_xlabel("Level")
        axsModel[1, 0].set_ylabel("Number")
        axsModel[1, 1].plot(minMaxVec, np.zeros([len(minMaxVec)]), label=key)
        axsModel[1, 1].legend(loc=2)
        axsModel[1, 1].axis("off")

        ax.plot(
            minMaxVec,
            npvVectorsMission,
            label=key + " from %.2f to %.2f" % (minMaxKey[0], minMaxKey[-1]),
        )

axsModel[1, 1].plot(minMaxVec, np.zeros([len(minMaxVec)]), label="Baseline")
ax.plot(
    minMaxVec,
    outputsBaseline.npv * np.ones([len(minMaxVec)]),
    "k--",
    label="Baseline",
)  # add the baseline case for reference
box = ax.get_position()
ax.set_position((box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9))
ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5
)
ax.set_title("Sensitivity to Model input assumptions")
ax.set_xlabel("Input Value")
ax.set_ylabel("NPV (EUR)")

# Save results
pp = PdfPages("AGVUseCaseModelResults.pdf")
pp.savefig(figs[0])
pp.savefig(figs[1])
pp.savefig(figs[2])
pp.savefig(figSense)
pp.savefig(figSlope)
# can add additional modified cases here
# CHEAPER AGV
pp.savefig(figsCheaper[0])
pp.savefig(figsCheaper[1])
pp.savefig(figsCheaper[2])
# SLOW VEHICLE
pp.savefig(figsSlower[0])
pp.savefig(figsSlower[1])
pp.savefig(figsSlower[2])

pp.savefig(figModelMission)
pp.savefig(figMissionSense)
pp.close()

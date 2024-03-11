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
from typing import Any, List, Tuple, Union
from matplotlib.figure import Figure
import numpy as np
from numpy.typing import NDArray
import pandas as pd
import warnings
import numpy_financial as npf
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from dataclasses import dataclass, field


@dataclass
class Assumption:
    discount_rate: float = field(metadata={"unit": "%"})
    electricity_price: float = field(metadata={"unit": "CHF/kWh"})
    diesel_price: float = field(metadata={"unit": "CHF/L"})
    diesel_energy: float = field(metadata={"unit": "kWh/L"})
    data_carriage: float = field(metadata={"unit": "CHF/MB"})
    years_of_operation: float = field(metadata={"unit": "years"})
    technology_readiness: int = field(metadata={"unit": "TRL"})
    company_acceptance: float = field(metadata={"unit": "CompanyAcceptance"})
    mission_similarity: float = field(metadata={"unit": "MissionSimilarity"})
    mission_determinism: float = field(metadata={"unit": "MissionDeterminism"})


@dataclass
class Vehicle:
    """
    A human operated vehicle
    """

    vehicle_cost: int = field(metadata={"unit": "CHF"})
    vehicle_energy_consumption: float = field(metadata={"unit": "L/100km"})
    operator_hourly_wage: int = field(metadata={"unit": "CHF/hr"})
    vehicle_maintainance: int = field(metadata={"unit": "CHF/month"})
    vehicle_eol_cost: int = field(metadata={"unit": "CHF for end of life disposal"})
    vehicle_average_speed: int = field(metadata={"unit": "km/hr"})
    vehicle_material_capacity: int = field(metadata={"unit": "units"})
    vehicle_max_shift_length: int = field(metadata={"unit": "hours"})


@dataclass
class Agv:
    """An autonomous guided vehicle"""

    agv_cost: int = field(metadata={"unit": "CHF"})
    agv_leasing: int = field(metadata={"unit": "CHF/vehicle/year"})
    agv_maintenance: int = field(metadata={"unit": "CHF/month"})
    agv_eol_cost: int = field(metadata={"unit": "CHF for end of life disposal"})
    agv_average_speed: int = field(metadata={"unit": "km/hr"})
    agv_charge_rate: int = field(metadata={"unit": "kW"})
    agv_disengagement_per_km: float = field(
        metadata={"unit": "disengagements per driven km"}
    )
    agv_disengagement_time: int = field(metadata={"unit": "minutes per disengagement"})
    agv_material_capacity: int = field(metadata={"unit": "units"})
    agv_energy_consumption: float = field(metadata={"unit": "kWh/km"})
    agv_max_shift_length: int = field(metadata={"unit": "hours"})
    agv_data_use: int = field(metadata={"unit": "MB/day"})


@dataclass
class Input:
    mission_length: float = field(metadata={"unit": "km"})
    material_to_move: int = field(metadata={"unit": "units"})
    yearly_operation_days: int = field(metadata={"unit": "days"})
    vehicle: Vehicle
    agv: Agv


@dataclass
class Output:
    annual_savings: float
    cumulative_vehicle_annual_cost: float
    cumulative_agv_annual_cost: float
    cash_flows: List[Union[float, int]]
    npv: float
    min_savings: NDArray[Any]
    nper: NDArray[Any]
    num_robots: int


def read_assumption_values_from_excel(path: str) -> Assumption:
    df = pd.read_excel(io=path, sheet_name="Inp_Custom")

    assumption = Assumption(
        discount_rate=float(df.iat[1, 1]),
        electricity_price=float(df.iat[2, 1]),
        diesel_price=float(df.iat[3, 1]),
        diesel_energy=float(df.iat[4, 1]),
        data_carriage=float(df.iat[5, 1]),
        years_of_operation=float(df.iat[6, 1]),
        technology_readiness=int(df.iat[7, 1]),
        company_acceptance=float(df.iat[8, 1]),
        mission_similarity=float(df.iat[9, 1]),
        mission_determinism=float(df.iat[10, 1]),
    )

    return assumption


def read_input_values_from_excel(path: str) -> Input:
    df = pd.read_excel(io=path, sheet_name="Inp_Custom")

    input = Input(
        mission_length=float(df.iat[13, 1]),
        material_to_move=int(df.iat[14, 1]),
        yearly_operation_days=int(df.iat[15, 1]),
        vehicle=Vehicle(
            vehicle_cost=int(df.iat[18, 1]),
            vehicle_energy_consumption=float(df.iat[19, 1]),
            operator_hourly_wage=int(df.iat[20, 1]),
            vehicle_maintainance=int(df.iat[21, 1]),
            vehicle_eol_cost=int(df.iat[22, 1]),
            vehicle_average_speed=int(df.iat[23, 1]),
            vehicle_material_capacity=int(df.iat[24, 1]),
            vehicle_max_shift_length=int(df.iat[25, 1]),
        ),
        agv=Agv(
            agv_cost=int(df.iat[28, 1]),
            agv_leasing=int(df.iat[29, 1]),
            agv_maintenance=int(df.iat[30, 1]),
            agv_eol_cost=int(df.iat[31, 1]),
            agv_average_speed=int(df.iat[32, 1]),
            agv_charge_rate=int(df.iat[33, 1]),
            agv_disengagement_per_km=float(df.iat[34, 1]),
            agv_disengagement_time=int(df.iat[35, 1]),
            agv_material_capacity=int(df.iat[36, 1]),
            agv_energy_consumption=float(df.iat[37, 1]),
            agv_max_shift_length=int(df.iat[38, 1]),
            agv_data_use=int(df.iat[39, 1]),
        ),
    )

    return input


def ModelAGVMission(assumptions: Assumption, inputs: Input):
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
    # Sanity check input assumptions
    assumptions.company_acceptance = np.clip(
        assumptions.company_acceptance, 0.1, 1
    )  # restrict company acceptance between 0.1 and 1
    assumptions.mission_similarity = np.clip(
        assumptions.mission_similarity, 0.1, 1
    )  # restrict mission similarity between 0.1 and 1
    assumptions.mission_determinism = np.clip(
        assumptions.mission_determinism, 0.1, 1
    )  # restrict mission determinism between 0.1 and 1
    AverageSpeed = (
        0.5
        * 0.7544
        * np.exp(0.517 * assumptions.technology_readiness)
        * assumptions.mission_similarity
        * assumptions.mission_determinism
    )  # km/hr - average speed is half of the max speed, scaled by mission similarity and determinism
    TimePerDisengagement = 243.16 * np.exp(
        -0.679 * assumptions.technology_readiness
    )  # minutes
    ##Disengagements depend on technology readiness, scaled by mission determinism and company acceptance
    DisengagementsPerKm = (
        5.133
        * np.exp(-1.083 * assumptions.technology_readiness)
        / assumptions.company_acceptance
        / assumptions.mission_determinism
    )  # disengagements/km

    # Sanity check outputs
    AverageSpeed = np.clip(AverageSpeed, 0.5, 64)  # km/hr
    DisengagementsPerKm = np.clip(DisengagementsPerKm, 0.0008, 2)  # dis./km
    TimePerDisengagement = np.clip(TimePerDisengagement, 0.5, 120)  # minutes

    return AverageSpeed, DisengagementsPerKm, TimePerDisengagement


def ModelAGVUseCase(assumptions: Assumption, inputs: Input) -> Output:
    # Sanity check input assumptions
    inputs.yearly_operation_days = int(
        np.clip(inputs.yearly_operation_days, 1, 365)
    )  # restrict operation days to the max days in a year
    assumptions.diesel_energy = np.clip(
        assumptions.diesel_energy, 0.95, 0.97
    )  # restrict diesel energy to the max energy available

    ## HUMAN operated vehicle
    # Vehicle mission running
    VehicleDailyMissions: int = np.ceil(
        inputs.material_to_move / inputs.vehicle.vehicle_material_capacity
    )  # number of missions driven per day
    VehicleDailyDistance = inputs.mission_length * VehicleDailyMissions  # km/day
    VehicleDailyTime = (
        VehicleDailyDistance / inputs.vehicle.vehicle_average_speed
    )  # hr/day
    NumberOfVehicles: int = np.ceil(
        VehicleDailyTime / inputs.vehicle.vehicle_max_shift_length
    )  # Number of Vehicles needed to acheive mission
    # Human Cost inputs
    VehiclePurchasePrice = NumberOfVehicles * inputs.vehicle.vehicle_cost  # CHF
    # Energy
    VehicleEnergyCost = (
        inputs.vehicle.vehicle_energy_consumption
        / 100
        * assumptions.diesel_price
        * VehicleDailyDistance
        * inputs.yearly_operation_days
    )  # CHF/year
    # Operator cost
    VehicleOperatorCost = (
        VehicleDailyTime
        * inputs.vehicle.operator_hourly_wage
        * inputs.yearly_operation_days
    )  # CHF/year

    VehicleAnnualOperationCost = VehicleEnergyCost + VehicleOperatorCost
    VehicleAnnualMaintenanceCost = inputs.vehicle.vehicle_maintainance * 12  # CHF/year
    VehicleAnnualCost = NumberOfVehicles * (
        VehicleAnnualOperationCost + VehicleAnnualMaintenanceCost
    )
    VehicleEndOfLifeCost = NumberOfVehicles * inputs.vehicle.vehicle_eol_cost  # CHF

    ## AGV
    # AGV missions
    AGVDailyMissions: int = np.ceil(
        inputs.material_to_move / inputs.agv.agv_material_capacity
    )  # number of missions driven per day
    AGVDailyDistance = inputs.mission_length * AGVDailyMissions  # km/day
    AGVDailyEnergy = AGVDailyDistance * inputs.agv.agv_energy_consumption  # kWh
    AGVDailyTime = (
        AGVDailyDistance / inputs.agv.agv_average_speed
        + AGVDailyEnergy / inputs.agv.agv_charge_rate
    )  # hours required by the AGV to acheive its mission
    # Number of AGVs needed to acheive mission
    NumberOfAGVs: int = np.ceil(AGVDailyTime / inputs.agv.agv_max_shift_length)

    ## AGV cost inputs
    AGVPurchasePrice = NumberOfAGVs * inputs.agv.agv_cost  # CHF
    AGVLeasingPrice = NumberOfAGVs * inputs.agv.agv_leasing  # CHF
    if AGVPurchasePrice > 0 and AGVLeasingPrice > 0:
        warnings.warn(
            "Warning: AGV purchase and leasing price are both set, only one should be set"
        )
    # Energy
    AGVEnegyCost = (
        assumptions.electricity_price
        * inputs.agv.agv_energy_consumption
        * AGVDailyDistance
        * inputs.yearly_operation_days
    )  # CHF/year
    # Data Carriage
    AGVDataCost = (
        assumptions.data_carriage
        * inputs.agv.agv_data_use
        * inputs.yearly_operation_days
    )  # CHF/year
    # Human intervention (disengagements)
    AGVCostPerDisengagement = (
        inputs.agv.agv_disengagement_time / 60 * inputs.vehicle.operator_hourly_wage
    )
    AGVDisengagementCost = (
        inputs.agv.agv_disengagement_per_km
        * AGVCostPerDisengagement
        * AGVDailyDistance
        * inputs.yearly_operation_days
    )  # CHF/year
    # Total costs
    AGVAnnualOperationCost = (
        AGVEnegyCost + AGVDataCost + AGVDisengagementCost
    )  # CHF/year
    AGVAnnualMaintenanceCost = inputs.agv.agv_maintenance * 12  # CHF/year
    AGVAnnualCost = (
        NumberOfAGVs * (AGVAnnualOperationCost + AGVAnnualMaintenanceCost)
        + AGVLeasingPrice
    )
    AGVEndOfLifeCost = NumberOfAGVs * inputs.agv.agv_eol_cost  # CHF

    # Initial investment price
    if VehiclePurchasePrice < AGVPurchasePrice:
        InvestmentCost = VehiclePurchasePrice - AGVPurchasePrice  # CHF
    else:
        InvestmentCost = 0  # CHF Handles the case where AGVs are leased, and therefore not part of the overall cost

    AnnualSavings = VehicleAnnualCost - AGVAnnualCost  # CHF/year

    EndOfLifePrice = VehicleEndOfLifeCost - AGVEndOfLifeCost  # CHF

    # Establish cash flows

    cashFlows = (
        [InvestmentCost]
        + [AnnualSavings] * (int(assumptions.years_of_operation) - 1)
        + [AnnualSavings + EndOfLifePrice]
    )

    ## Return outputs
    # calculate the project net present value
    npv: float = npf.npv(assumptions.discount_rate, cashFlows)
    # calculate the project minimum yearly savings to be profitable
    minSavings = npf.pmt(
        assumptions.discount_rate, assumptions.years_of_operation, InvestmentCost
    )
    # calculate the project payback period
    nper = npf.nper(assumptions.discount_rate, AnnualSavings, InvestmentCost)

    outputs = Output(
        annual_savings=AnnualSavings,
        cumulative_vehicle_annual_cost=(
            VehicleAnnualOperationCost * assumptions.years_of_operation
        ),
        cumulative_agv_annual_cost=(
            AGVAnnualOperationCost * assumptions.years_of_operation
        ),
        cash_flows=cashFlows,
        npv=npv,
        min_savings=minSavings,
        nper=nper,
        num_robots=NumberOfAGVs,
    )
    return outputs


def PlotCaseResults(
    Assumptions: Assumption, inputs: Input, outputs: Output, CaseName: str
) -> List[Figure]:
    # plots the basic use case model outputs
    figEcon, axes = plt.subplots(2, figsize=(10, 10))
    ax = axes[0]

    figEcon.subplots_adjust(top=0.85)
    BaselineTotal = (
        inputs.vehicle.vehicle_cost
        + outputs.cumulative_vehicle_annual_cost
        + inputs.vehicle.vehicle_eol_cost
    )
    AGVTotal = (
        inputs.agv.agv_cost
        + outputs.cumulative_agv_annual_cost
        + inputs.agv.agv_eol_cost
    )
    totalCosts = [BaselineTotal, AGVTotal]
    ax.bar(["Manual Vehicle", "AGV"], totalCosts)
    #ax.set_title("%s Comparison of Undiscounted Lifetime costs" % CaseName)
    ax.set_title("Comparison of Undiscounted Lifetime costs")
    ax.set_ylabel("CHF Lifetime Cost (no discounting)")
    ax.grid(axis = 'y')
    ax2 = axes[1]
    ax2.axis([0, 12, 0, 12])
    ax2.text(
        0,
        11,
        "Discounted net present value of the investment: %3.2f CHF"
        % outputs.npv,
        fontsize=15,
    )

    if outputs.npv < 0:
        ax2.text(
            0,
            10,
            "%s Project has a negative net present value,\n savings must be %3.2f CHF/year to be profitable \n presently the savings are only %3.2f CHF/year"
            % (CaseName, np.abs(outputs.min_savings), outputs.annual_savings),
            fontsize=15,
        )

    ax2.text(
        0,
        9,
        "Number of robots to match human performance: %d units"
        % outputs.num_robots,
        fontsize=15,
    )

    ax2.text(
        0,
        8,
        "Return on the robotic investment requires: %3.2f years"
        % outputs.nper,
        fontsize=15, 
        weight='bold',
    )
    ax2.axis("off")
    
    ax2.text(
        0,
        6,
        "Annual operation cost* AGV: %3.2f CHF"
        % (outputs.cumulative_agv_annual_cost/Assumptions.years_of_operation),
        fontsize=15,
    )
    
    ax2.text(
        0,
        5,
        "Annual operation cost* manual vehicle: %3.2f CHF"
        % (outputs.cumulative_vehicle_annual_cost/Assumptions.years_of_operation),
        fontsize=15,
    )
    
    ax2.text(
        0,
        3,
        "*Annual operation cost includes energy and data consumption, maintenance costs and expenses for an operator and disengagements"
        % (outputs.cumulative_vehicle_annual_cost/Assumptions.years_of_operation),
        fontsize=8,
    )

    # Plot the cash flows for the project
    plotDF = pd.DataFrame()
    plotDF["cashFlows"] = outputs.cash_flows
    plotDF["CFpos"] = plotDF["cashFlows"] > 0
    figFlow = plt.figure()
    ax = figFlow.add_subplot()
    plotDF["cashFlows"].plot(
        ax=ax, kind="bar", color=plotDF.CFpos.map({True: "k", False: "r"})
    )
    ax.set_xlabel("Operation Year")
    ax.set_ylabel("CHF")
    ax.set_title("Project Cash Flows")
    ax.grid(axis = 'y')
    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(
        np.arange(np.round(start / 1000) * 1000, np.round(end / 1000) * 1000, 10000)
    )
    figFlow = plt.gcf()
    figFlow.set_figwidth(15)
    figFlow.set_figheight(10)

    # Plot the fraction of the costs for the baseline and autonomous case
    figShare, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 6)
    )  # ax1,ax2 refer to your two pies
    labels = [
        "VehiclePurchasePrice",
        "CumulativeVehicleAnnualCost",
        "VehicleEndOfLifeCost",
    ]
    costsBaseline = [
        inputs.vehicle.vehicle_cost,
        outputs.cumulative_vehicle_annual_cost,
        inputs.vehicle.vehicle_eol_cost,
    ]
    ax1.pie(costsBaseline, labels=labels, autopct="%1.1f%%")
    ax1.set_title("%s Baseline (Human operator) Lifetime Cost Share" % CaseName)
    costsAGV = [
        inputs.agv.agv_cost,
        outputs.cumulative_agv_annual_cost,
        inputs.agv.agv_eol_cost,
    ]
    ax2.pie(costsAGV, labels=labels, autopct="%1.1f%%")
    ax2.set_title("%s Autonomous Ground Vehicle Lifetime Costs Share" % CaseName)
    figs = [figEcon, figFlow, figShare]
    return figs


def SenstivityAnalysis(
    key: str, minMaxPerc: int, numLevels: int, assumptions: Assumption, inputs: Input
) -> Tuple[NDArray[Any], List[Any], List[Any]]:  # FIXME: add correct list types
    # performs a sensitivity analysis on the variable in the dict 'key' in either the assumptions or inputs dict
    # Inputs:
    # key - the name of the dictionary key in the inputs and assumptinos for which the analysis is performed
    # minMaxPerc - scalar value of the minimum / maximum percent to vary the key
    # numLevels - the discretization of the analysis
    # Assumptions - dictionary of assumptions to be tested
    # Inputs - dictionary of the inputs to be tested
    # Outputs:
    # minMaxVec - vector of minMax percentages based on the inputs
    # npvVec - vector of npv calculated across the range specified by minMaxPerc

    npvVec = []
    valVec = []
    minMaxVec = (
        np.linspace(-minMaxPerc, minMaxPerc, numLevels) / 100
    )  # build the sensitivity range
    minMaxVec = np.insert(minMaxVec, int(numLevels / 2), 0)
    if hasattr(assumptions, key):
        origKey = getattr(assumptions, key)
    elif hasattr(inputs, key):
        origKey = getattr(inputs, key)
    elif hasattr(inputs.vehicle, key):
        origKey = getattr(inputs.vehicle, key)
    elif hasattr(inputs.agv, key):
        origKey = getattr(inputs.agv, key)
    else:
        raise Exception("Key not found, check input and assumption variable names")

    for perc in minMaxVec:  # iterate all inputs
        if hasattr(assumptions, key):
            setattr(assumptions, key, origKey * (1 + perc))
            valVec.append(getattr(assumptions, key))
        elif hasattr(inputs, key):
            setattr(inputs, key, origKey * (1 + perc))
            valVec.append(getattr(inputs, key))
        elif hasattr(inputs.vehicle, key):
            setattr(inputs.vehicle, key, origKey * (1 + perc))
            valVec.append(getattr(inputs.vehicle, key))
        elif hasattr(inputs.agv, key):
            setattr(inputs.agv, key, origKey * (1 + perc))
            valVec.append(getattr(inputs.agv, key))

        outputs = ModelAGVUseCase(assumptions, inputs)
        npvVec.append(outputs.npv)
        minMaxVals = [min(valVec), max(valVec)]

    if hasattr(assumptions, key):
        setattr(assumptions, key, origKey)
    elif hasattr(inputs, key):
        setattr(inputs, key, origKey)
    elif hasattr(inputs.vehicle, key):
        setattr(inputs.vehicle, key, origKey)
    elif hasattr(inputs.agv, key):
        setattr(inputs.agv, key, origKey)

    return minMaxVec, minMaxVals, npvVec

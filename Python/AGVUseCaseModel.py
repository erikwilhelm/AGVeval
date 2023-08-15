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

# Inputs

PurchasePrice=75000 #EUR
AnnualSavings=12962 #→EUR
YearsOfOperation=7 #Years that the robotic system is in operation

cashFlows = [-PurchasePrice]+ [AnnualSavings] * YearsOfOperation # create main list of cash flows

# Assumptions
discountRate = 0.05; # Five percent per annum


# Outputs

npv = npf.npv(discountRate, cashFlows)

print("Net present value of the investment:%3.2f" % npv)

if npv < 0: 
    minSavings=npf.pmt(discountRate,YearsOfOperation,PurchasePrice)
    print("Project has a negative net present value, savings must be %3.2f per year to be profitable" % np.abs(minSavings))


# Sensitivity
#TODO - add sensitivity analysis here
print("Number of years to return on the robotic investment:%3.2f" % npf.nper(discountRate, -AnnualSavings, PurchasePrice))


















# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 14:26:30 2020

@author: aashi
"""

import numpy as np
import sympy as sym
import statsmodels.api as sm

sym.init_printing()
endog = sym.var('r, w, l, c, k, z, c_LEAD, r_LEAD')
Lags = sym.var('r_LAG, w_LAG, l_LAG, c_LAG, k_LAG, z_LAG, c_LEAD_LAG, r_LEAD_LAG')
exog = [sym.var('epsilon_z')]
eta = sym.var('eta_c, eta_r')

params = sym.var('beta, theta, varphi, alpha, delta, phi, Psi')

# Optimal Conditions  & state transition
inter   = r - (z*alpha*(k/l)**(alpha-1))
wage    = w - (1-alpha)*z*(k/l)**alpha
labor   = Psi*varphi*l**(varphi-1)-w*(c**(-theta))
euler   = c**(-theta) -(c_LEAD**(-theta))*beta*(1+r_LEAD)
capital = k - (1-delta)*k_LAG - z_LAG*(k_LAG**alpha)*(l_LAG**(1-alpha)) + c_LAG
tech    = z - phi*z_LAG - epsilon_z
cpred   = c - c_LEAD_LAG - eta_c
rpred   = r - r_LEAD_LAG - eta_r

optcon  = sym.Matrix([inter, wage, labor, euler, capital, tech, cpred, rpred])

# Steady State Equation needed to be calculated by hand
rstar   = beta**(-1) - 1
kls     = ((rstar+delta)/alpha)**(1/(alpha-1))
wstar   = (1-alpha)*(kls)**alpha
clstar  = kls**alpha - delta*kls
lstar   = 8/24
kstar   = kls*lstar
cstar   = clstar*lstar
zstar   = 1
Ystar   = (kstar**alpha)*(lstar**(1-alpha))
ss_eq   = sym.Matrix([rstar, wstar, lstar, cstar, kstar, zstar, cstar, rstar])

# 
lss   = Psi*(varphi*1/3**(varphi-1))- (clstar*1/3**theta)*(1-alpha)*(kls**alpha)

class DSGE(object):
    def __init__(self, endog_var, exog_var, models, param):        
        # Save argments  
        self.endog_var = endog_var
        self.exog_var  = exog_var
        self.models    = models
        self.params    = params
        # Detect forward looking variables
        strLeads       = [Lead.name for Lead in endog_var if '_LEAD' in Lead.name]
        self.Leads     = sym.var(strLeads)
        self.Jumps     = sym.var([strLead.replace('_LEAD','') for strLead in strLeads])
        # Define prediction error
        self.eta       = sym.var(['eta_' + Jump.name for Jump in self.Jumps]) 
        # Define lagged variables
        strLags        = [Lag.name + '_LAG' for Lag in endog_var]
        self.Lags      = sym.var(strLags)
    
    def log_linearize(self):
        # Differentiation
        jopt       = self.models.jacobian(self.endog_var).\
                        subs([(Lag,self.endog_var[i]) for i, Lag in enumerate(self.Lags)]).\
                        subs([(Lead,self.Jumps[i]) for i, Lead in enumerate(self.Leads)])
        jopt_Lag   = -self.models.jacobian(self.Lags).subs([(Lag,self.endog_var[i]) for i, Lag in enumerate(self.Lags)]).\
                        subs([(Lead,self.Jumps[i]) for i, Lead in enumerate(self.Leads)])
        jopt_exog  = self.models.jacobian(self.exog_var)
        jopt_eta   = self.models.jacobian(self.eta)
        fcoef      = sym.lambdify([self.params,self.endog_var],jopt)
        fcoef_Lag  = sym.lambdify([self.params,self.endog_var],jopt_Lag)
        fcoef_exog = sym.lambdify([self.params],jopt_exog)
        fcoef_eta = sym.lambdify([self.params],jopt_eta)
        return fcoef, fcoef_Lag, fcoef_exog, fcoef_eta
    
    def steady_state(self, steady_models):
        fss = sym.lambdify([self.params],steady_models)
        return fss
    
    def canonical_form(self, vparam, steady_models):
        fcoef, fcoef_Lag, fcoef_exog, fcoef_eta = self.log_linearize()
        fss = self.steady_state(steady_models)
        ss  = fss(vparams)
        g0  = np.matrix(fcoef(vparams,ss)*ss, dtype='float')
        g1  = np.matrix(fcoef_Lag(vparams,ss)*ss, dtype='float')
        g2  = np.matrix(fcoef_exog(vparams)*ss, dtype='float')
        g3  = np.matrix(fcoef_eta(vparams)*ss, dtype='float')
        return g0, g1, g2, g3

a = DSGE(endog,exog,optcon,params)        
#
lev = lss.subs([(beta,0.99), (theta,1.5) ,(varphi,2) , (alpha,0.3), (delta,0.025)])
vPsi = sym.solve(lev,Psi)[0]

# Evaluate steady state and each derivative in terms of % deviations from ss
vparams = np.array([0.99, 1.5 ,2 , 0.3, 0.025, 0.8, 1])
b=a.canonical_form(vparams,ss_eq)

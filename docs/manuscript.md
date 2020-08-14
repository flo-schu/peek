---
title: "Stabilizing Mechanisms of Artificial Ecological Communities under Environmental and Chemical Stress"
date: "13.08.2020"
author: Florian Schunck

documentclass: scrartcl
classoption: [onecolumn]
geometry: [a4paper, bindingoffset=0mm, inner=30mm, outer=30mm, top=30mm, bottom=30mm]
language: en-US

bibliography:
  - references.bib
link-citations: true

abstract: |
  This is the abstract

---
<!--
check https://pandoc.org/MANUAL.html for meta data variables
pandoc --filter pandoc-citeproc -s manuscript.md -o manuscript.pdf
-->



# Introduction

## Motivation

Species have varying sensitivity to chemical and environmental stress.
If stress is recurring and time for recovery is not sufficient, resilient
species will outcompete the other [@Liess.2013] in ecosystems which are
under default conditions stable for both species.

Sokolova urges to consider the effect of temperatures in all studies of the
effects of multiple stressors in natural populations

We know that pesticides are applied multiple times throughout the year,
starting in spring and moving on towards harvest. During this time temperatures
cyclically increase and decrease, with peaks in summer. By additionally
avoiding feeding in the water column the system is governed by the dynamic of
primary production and community competition for a shared food resource.

Thus we aim to approximate a natural pond system very closely and thus identify
the interaction between temperature, resource availability / competition,
chemical pollution and community structure.
and identify states and possibly times when communities are particularly vulnerable

## Background information

Culex pipeens larvae thrive in stagnant water with high input of organic material

## Recent Findings

[@Gessner.2016] context dependency in stress-effect analyses has until 2016
been under researched.

check research of gardeström et al (2016). They made a research of communities
in streams and the dependence of outcome on the contamination legacy.
This may be important for the second part of the current nanocosm experiment
repeated contamination with low dose pesticide after initial contamination with
esfenvalerate of different dose

[@Wood.2017] show how neonicotinoides are flushed into rivers after peak rain
events. This shows that repeated pulse exposures are a much more meaningful
approach to testing the effect of pesticides in contrast to continuous exposure,
which practically does not take place. It would be interesting to have a small
background exposure present at all times.

[@ArenasSanchez.2019] conducted a microcosm experiment with zooplancton community
and insecticide (lufenuron) and two temperature treatments. Hence, temperature +
pesticide alone is not really a novel approach, also in nanocosms. The experiment lasted
for three months. Invasive sampling method was applied.

## Research Questions

(1) Identify the drivers of community change. Candidates are: Stressors (Pesticides,
    Environmental Variables, Community Structure - Competition, Timing)

(2) When are communities resilient to pesticides and environmental stress? And
    when are they particularly vulnerable?

(3) Can organisms be detected and quantified with machine learning algorithms
    -> upscaling of non invasive techniques.

(4) Genetic variation in population during time course or after stress events

(5) Contamination history relevance for reaction to contaminating event

(6) PICT questions in relation to selection of resistant individuals
    sample individuals from nanocosms over different time points and make experiments
    with offspring. Will tolerances in populations emerge and do they have an
    effect on community tolerance

(7) Can locations of attractors be estimated from environmental parameters

(8) Can multi species consumer resource systems realistically be modeled?

## Hypotheses

(1) Communities converge towards a cyclic attractor after initialization.
    - measure environmental variables.
    - Find relations between variables and attractors in phase diagram.
    - Drivers of community states can thus be identified

(2) Communities can recover from small perturbations but ecosystems will change
    after larger perturbations occurred
    -

(2) Environmental stress affects the stability of the attractors

(3) Refuges and renewal of population would generally stabilize the communities
    -





# Method

#### Start Population:
Populate Nanocosms from offspring of one individual?!

#### Treatments:
In the shelves, 40 nanocosms can be placed, if arranged in single rows.
Double rows it could be 80 but this would be a large increase in workload
and inconvenience in handling during the experiment duration.
start with 100 to allow for losses

minimum n for treatments (5-10)

Factors:
+ temp / - temp (2)


Two environmental settings (green shelf + normal shelf)


- How many pesticide concentrations? Control, low, high? I am not so interested
  in dose response relationships as in the interplay between environmental effects
  and pesticides.

#### Nanocosm design:
- 3-4 cm of Sediment (does not need to be as much as we have now.)
- aeration U-tubes located at 45° to not interfere with camera.
- Hoses from above with some room for movement of the tanks for taking photos.
- Black pond foil (buy new)

#### Analyses:
- Pesticide concentration (Twisters?)
- photosynthesis activity
- Take samples with syringes
- Store water samples?
- Temperature:
  - Continuous monitoring of lab temperature
  - weekly monitoring of tank temperature
- water quality parameters (pH, Conductivity, NO32-, NO3-, NH3, P, cell counter)
- Carbon [@ArenasSanchez.2019]
- sampling of neonates from nanocosms in spaced intervals (once every two months)
  for storing of data and potential determination of DNA

#### Temperature:
- Water immersed heaters. How many do we have? Since I have to install all
  of them in the nanocosms. Could there be a conflict with the streams
- also get enough electric sockets

#### Light:
- Install dimmer of left hand shelves to adjust light conditions of all
  shelves to the same level.


#### Image Detection:
- How to shoot photographs of the upper nanocosms


#### Routine
- capture images two times per week (Friday, Tuesday)
- analysis once per week. Should be set up mostly automated. Cluster?
- water quality parameters - every two weeks
- temperature: More often (in Situ)
- replace glucose solution sponges twice per week
- replenish water reservoir every two weeks

#### Workload distribution
- Can Franz assist me in some of the recurring tasks?
- Bachelor / Master thesis for recurring lab tasks

# References

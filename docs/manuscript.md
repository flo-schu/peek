---
title: "Mechanisms of Degradation of Artificial Ecological Communities under Environmental and Chemical Stress"
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

## Introduction

### Motivation

Species have varying sensitivity to chemical and environmental stress.
If stress is recurring and time for recovery is not sufficient, resilient
species will outcompete the other [@Liess.2013] in ecosystems which are
under default conditions stable for both species.

Sokolova urges to consider the effect of temperatures in all studies of the
effects of multiple stressors in natural populations [@Sokolova.2013]

We know that pesticides are applied multiple times throughout the year,
starting in spring and moving on towards harvest. During this time temperatures
cyclically increase and decrease, with peaks in summer. By additionally
avoiding feeding in the water column the system is governed by the dynamic of
primary production and community competition for a shared food resource.

Thus we aim to approximate a natural pond system very closely and thus identify
the interaction between temperature, resource availability / competition,
chemical pollution and community structure.
and identify states and possibly times when communities are particularly vulnerable

### Background information

Culex pipeens larvae thrive in stagnant water with high input of organic material

### Recent Findings

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

[@Ashauer.2020] showed that sampling timing of sampling is an important determinant 
of risk assessment, since average concentrations do not capture possible effects of
high peak concentrations

### Research Questions

#### Main content questions

(1) Interactions between Temperature, and Pesticides in small aquatic communities of
    consumer resource systems type

(2) Do Refuges stabilize communities under stress

(3) Reliability of environmental cues [@Bonamour.2019] would be interesting, but could be hard to study
    Nevertheless, if food concentration is studied and pop development is studied
    as well, it could be shown that offspring is produced in high numbers due to temp rise
    and not necessarily due to food rise, which may develop simultaneously.

(3) Identify the drivers of community change. Candidates are: Stressors (Pesticides,
    Environmental Variables, Community Structure - Competition)
    Timing: is only relevant if stressors follow a different application patterns
            at the moment it seems that this question will be hard to answer in this setting

(4) When are communities resilient to pesticides and environmental stress? And
    when are they particularly vulnerable? Related to this question is the question of
    whether patterns of environmental conditions (e.g. low food, high temp, existed
    which increased the likelihood of collapse)
    (a) Can locations of attractors be estimated from environmental parameters

(5) Genetic variation in population during time course or after stress events (Opt)

(6) Contamination history relevance for reaction to contaminating event.
    This question is not really possible to answer with the first part of the
    experiment, but could perhaps be answered after part 1 has been finished. Meaning
    that afterwards, communities subject to different intensities of pesticide
    treatments could be subject to one single treatment and effects could be studied.

(7) PICT questions in relation to selection of resistant individuals
    sample individuals from nanocosms over different time points and make experiments
    with offspring. Will tolerances in populations emerge and do they have an
    effect on community tolerance

(8) Can collapsed systems be colonized again

#### Method questions

(1) Can multi species consumer resource systems realistically be modeled?

(2) Can organisms be detected and quantified with machine learning algorithms
    -> upscaling of non invasive techniques.

### Hypotheses

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

## Method

### Experiment design

#### Start Population

Populate Nanocosms from offspring of one individual?!

#### Pre-Tests

+ semi-acute tests with individuals with small amounts of sediments.
  this is helpful, since pesticides will sorb to sediments. Nanocosm test
  with three containers and three concentrations

#### Treatments

it is preferable to increase the effect size than to increase the sample size because
standard error scales faster with effect size than with sample size

In the shelves, 40 nanocosms can be placed, if arranged in single rows.
Double rows it could be 80 but this would be a large increase in workload
and inconvenience in handling during the experiment duration.
start with 100 to allow for losses

minimum n for treatments (5-10)

Factors:

+ temp / - temp (2)

Two environmental settings (green shelf + normal shelf)

+ How many pesticide concentrations? Control, low, high? I am not so interested
  in dose response relationships as in the interplay between environmental effects
  and pesticides. Matthias suggested to only use few containers for high pesticide treatments
  I agree. And it would be nice to draw a dose response curve over pesticide for individuals
  and nanocosms

+ repeated contaminations should be conducted to evaluate adaptation to stressors

#### Nanocosm design

+ 3-4 cm of Sediment (does not need to be as much as we have now.)
+ aeration U-tubes located at 45° to not interfere with camera.
+ Hoses from above with some room for movement of the tanks for taking photos.
+ Black pond foil (buy new)

#### Analyses

+ Pesticide concentration (Twisters?)
+ photosynthesis activity
+ Take samples with syringes
+ Store water samples?
+ Temperature:
  + Continuous monitoring of lab temperature
  + weekly monitoring of tank temperature
+ water quality parameters (pH, Conductivity, NO32-, NO3-, NH3, P, cell counter)
+ Carbon [@ArenasSanchez.2019]
  + Glühverlust in homogenized subsamples after analysis
+ sampling of neonates from nanocosms in spaced intervals (once every two months)
  for storing of data and potential determination of DNA

#### Storage

+ Storage of organisms, sediment and water samples after the end of the experiment

#### Temperature

+ Water immersed heaters. How many do we have? Since I have to install all
  of them in the nanocosms. Could there be a conflict with the streams
+ also get enough electric sockets

#### Light

+ Install dimmer of left hand shelves to adjust light conditions of all
  shelves to the same level.
+ All nanocosms will be placed in normal shelves in two rows

#### Image Detection

+ Take photographs from white chair on top of table, or use ladder

#### Routine

+ capture images two times per week (Friday, Tuesday)
+ analysis once per week. Should be set up mostly automated. Cluster?
+ water quality parameters - every two weeks.
+ pH weekly
+ temperature: More often (in Situ)
+ replace glucose solution sponges twice per week
+ replenish water reservoir every two weeks

#### Workload distribution

+ Can Franz assist me in some of the recurring tasks?
+ Bachelor / Master thesis for recurring lab tasks

### Evaluation

+ avg. life expectancy of individuals

## Results and Observations

### Observations

+ In test systems, after addition of water to fill up to required water level
  was brought into suspension. This could be used to make food available to the organisms
  At any rate, it should be avoided that some tanks are treated differently from others
  I.e. supply water slowly or stirr in all nanocosms after supplying water

## References

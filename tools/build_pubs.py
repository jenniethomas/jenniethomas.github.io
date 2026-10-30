#!/usr/bin/env python3
"""
Build publications.html for jenniethomas.github.io.

The curated list of publications lives in PUBS below. For each entry the
script queries the Crossref API to fetch the DOI, full author list, journal,
volume and pages, then renders publications.html.

Author names: many Crossref records carry only initials ("J. Stutz"). The
script expands them to full first names where possible, using
  1. MANUAL_NAME_FIXES below (hand-verified full names), then
  2. OpenAlex author profiles (https://openalex.org), fetched per DOI and
     cached in tools/openalex_cache.json.
An expansion is only applied when the candidate's first name is consistent
with the Crossref initials, so other people's names are never substituted.
Any author that still has an abbreviated first name after this is listed at
the end of the build output; verify the full name and add it to
MANUAL_NAME_FIXES.

Usage:
    python3 tools/build_pubs.py

To add a new publication: append a tuple to PUBS and re-run the script.
Crossref responses are cached in tools/crossref_cache.json, OpenAlex author
data in tools/openalex_cache.json, so re-runs are fast. Entries that do not
match anything on Crossref fall back to the curated venue/author strings.

NOTE: name your own name bolding is automatic - any author with family name
"Thomas" and a given name starting with "J" (or no given name) is bolded.
"""

import html
import json
import os
import random
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "publications.html")
CACHE = os.path.join(HERE, "crossref_cache.json")
OA_CACHE = os.path.join(HERE, "openalex_cache.json")
CONTACT = "https://github.com/jenniethomas/jenniethomas.github.io"
MAILTO = "Jennie.Thomas@univ-grenoble-alpes.fr"

# (year, title, fallback venue, fallback authors, flag)
# flag: "preprint" marks preprint / under-review items. These are listed in a
# separate "Preprints" section until Crossref reports an accepted final
# version, at which point re-running the script moves them into the year
# sections automatically.
PUBS = [
    (2026, "Reduced global atmospheric microplastic emissions from size-harmonized observations", "Research Square preprint (under review at a Nature Portfolio journal)", "I Hough, H Angot, R Price, N Dobiasova, T Segur, ...", "preprint"),
    (2026, "Marine secondary aerosols are required for modeling clouds in the Arctic", "Geophysical Research Letters 53, e2026GL121724", "R Lapere, A Haddon, R Price, L Marelle, AH Monahan, N Steiner, JC Raut, ...", ""),
    (2026, "Understanding the Spread in Climate Feedbacks and Polar Amplification Using Coordinated Multimodel Experiments and CMIP6", "Journal of Climate 39, 4049-4070", "O Linke, J Lenhardt, MT Lund, J Merikanto, T Naakka, K Nordling, ...", ""),
    (2026, "Isolating the influence of aerosols on Arctic cloud radiative effects during a polluted warm air mass intrusion", "EGUsphere (preprint)", "R Price, L Marelle, L Bastien, R Lapere, H Angot, B Heutte, J Schmale, ...", "preprint"),
    (2026, "The biogenic sulfur cycle in the coupled ocean–sea ice–atmosphere system", "Elementa: Science of the Anthropocene 14(1)", "S Ishino, M Willis, H Angot, T Bartels-Rausch, O Crabeck, B Delille, ...", ""),
    (2026, "Polar primary aerosols across the ocean-sea ice-snow-atmosphere interface: From sources to impacts", "Elementa: Science of the Anthropocene 14(1), 00065", "JM Creamean, LA Miller, M van Pinxteren, O Crabeck, NS Steiner, ...", ""),
    (2026, "Aerosol‐cloud interactions: Overcoming a barrier to projecting near‐term climate evolution and risk", "AGU Advances 7(1), e2025AV001872", "U Im, BH Samset, A Nenes, JL Thomas, H Kokkola, O Dubovik, V Amiridis, ...", ""),
    (2026, "Using the power law size distribution to extrapolate and compare microplastic number and mass concentrations in environmental media", "Preprint — under review at Microplastics and Nanoplastics", "T Segur, I Hough, N Dobiasova, D Voisin, C Richon, H Angot, JL Thomas, ...", "preprint"),
    (2025, "Sea ice, aerosols and clouds", "Chapter in: Sea Ice — Its Physics, Chemistry, Biology, Geology and Societal Importance (Wiley)", "JC Raut, JL Thomas, L Marelle, R Lapere", ""),
    (2025, "Polar winter climate change: strong local effects from sea ice loss, widespread consequences from warming seas", "Atmospheric Chemistry and Physics 25, 8127-8145", "T Naakka, D Köhler, K Nordling, P Räisänen, MT Lund, R Makkonen, ...", ""),
    (2025, "How to trace the origins of short-lived atmospheric species: an Arctic example", "Atmospheric Chemistry and Physics 25, 5331-5354", "A Da Silva, L Marelle, JC Raut, Y Gramlich, K Siegel, SL Haslett, C Mohr, ...", ""),
    (2025, "Aerosol background concentrations influence aerosol‐cloud interactions as much as the choice of aerosol‐cloud parameterization", "Geophysical Research Letters 52, e2024GL111780", "L Marelle, G Myhre, JL Thomas, JC Raut", ""),
    (2025, "Solar radiation estimation in West Africa: impact of dust conditions during the 2021 dry season", "Atmospheric Chemistry and Physics 25, 997-1021", "L Clauzel, S Anquetin, C Lavaysse, G Bergametti, C Bouet, G Siour, ...", ""),
    (2025, "Ten crucial unknowns in atmospheric chemistry in the cold", "Faraday Discussions 258, 10-22", "T Bartels-Rausch, J Creamean, JL Thomas, M Willis, P Zieger", ""),
    (2025, "The interplay between snow and polluted air masses in cold urban environments", "Faraday Discussions 258, 502-520", "J Kuhn, J Stutz, T Bartels-Rausch, JL Thomas, M Cesler-Maloney, ...", ""),
    (2024, "An Arctic Marine Source of Fluorescent Primary Biological Aerosol Particles During the Transition from Summer to Autumn at the North Pole", "Tellus B: Chemical and Physical Meteorology 76, 47-70", "J Kojoj, GP Freitas, M Muilwijk, MA Granskog, T Naakka, AML Ekman, ...", ""),
    (2024, "Modeling the contribution of leads to sea spray aerosol in the high Arctic", "Atmospheric Chemistry and Physics 24, 12107-12132", "R Lapere, L Marelle, P Rampal, L Brodeau, C Melsheimer, G Spreen, ...", ""),
    (2024, "Polar aerosol atmospheric rivers: Detection, characteristics, and potential applications", "Journal of Geophysical Research: Atmospheres 129, e2023JD039606", "R Lapere, JL Thomas, V Favier, H Angot, J Asplund, AML Ekman, ...", ""),
    (2023, "Polar oceans and sea ice in a changing climate", "Elementa: Science of the Anthropocene 11, 00056", "MD Willis, D Lannuzel, B Else, H Angot, K Campbell, O Crabeck, B Delille, ...", ""),
    (2023, "Modelling the coupled mercury-halogen-ozone cycle in the central Arctic during spring", "Elementa: Science of the Anthropocene 11, 00129", "S Ahmed, JL Thomas, H Angot, A Dommergue, SD Archer, L Bariteau, ...", ""),
    (2023, "Untangling the influence of Antarctic and Southern Ocean life on clouds", "Elementa: Science of the Anthropocene 11, 00130", "MD Mallet, RS Humphries, SL Fiddes, SP Alexander, K Altieri, H Angot, ...", ""),
    (2023, "The representation of sea salt aerosols and their role in polar climate within CMIP6", "Journal of Geophysical Research: Atmospheres 128, e2022JD038235", "R Lapere, JL Thomas, L Marelle, AML Ekman, MM Frey, MT Lund, ...", ""),
    (2022, "A mass budget and box model of global plastics cycling, degradation and dispersal in the land-ocean-atmosphere system", "Microplastics and Nanoplastics 2, 28", "JE Sonke, AM Koenig, N Yakovenko, O Hagelskjær, H Margenat, ...", ""),
    (2022, "Mercury isotope evidence for Arctic summertime re-emission of mercury from the cryosphere", "Nature Communications 13, 4956", "BF Araujo, S Osterwalder, N Szponar, D Lee, MV Petrova, JB Pernov, ...", ""),
    (2022, "Modeling an extreme dust deposition event to the French alpine seasonal snowpack in April 2018: Meteorological context and predictions of dust deposition", "Journal of Geophysical Research: Atmospheres 127, e2021JD035745", "F Baladima, JL Thomas, D Voisin, M Dumont, C Junquas, R Kumar, ...", ""),
    (2022, "Comparison of model and ground observations finds snowpack and blowing snow both contribute to Arctic tropospheric reactive bromine", "Atmospheric Chemistry and Physics 22", "WF Swanson, CD Holmes, WR Simpson, K Confer, L Marelle, JL Thomas, ...", ""),
    (2022, "The role of snow in controlling halogen chemistry and boundary layer oxidation during Arctic spring: A 1D modelling case study", "Journal of Geophysical Research: Atmospheres 127, e2021JD036140", "S Ahmed, JL Thomas, K Tuite, J Stutz, F Flocke, JJ Orlando, ...", ""),
    (2021, "Evidence of free tropospheric and long-range transport of microplastic at Pic du Midi Observatory", "Nature Communications 12, 7242", "S Allen, D Allen, F Baladima, VR Phoenix, JL Thomas, G Le Roux, ...", ""),
    (2021, "Fate of Springtime Atmospheric Reactive Mercury: Concentrations and Deposition at Zeppelin, Svalbard", "ACS Earth and Space Chemistry 5, 3234-3246", "S Osterwalder, SM Dunham-Cheatham, B Ferreira Araujo, O Magand, ...", ""),
    (2021, "Implementation and impacts of surface and blowing snow sources of Arctic bromine activation within WRF-Chem 4.1.1", "Journal of Advances in Modeling Earth Systems 13, e2020MS002391", "L Marelle, JL Thomas, S Ahmed, K Tuite, J Stutz, A Dommergue, ...", ""),
    (2021, "Quantifying nitrous acid formation mechanisms using measured vertical profiles during the CalNex 2010 campaign and 1D column modeling", "Journal of Geophysical Research: Atmospheres 126, e2021JD034689", "K Tuite, JL Thomas, PR Veres, JM Roberts, PS Stevens, SM Griffith, ...", ""),
    (2020, "Integrative and comprehensive Understanding on Polar Environments (iCUPE): The concept and initial results", "Atmospheric Chemistry and Physics 20", "T Petäjä, EM Duplissy, K Tabakova, J Schmale, B Altstädter, G Ancellet, ...", ""),
    (2019, "Overview paper: New insights into aerosol and climate in the Arctic", "Atmospheric Chemistry and Physics 19, 2527-2560", "JPD Abbatt, WR Leaitch, AA Aliabadi, AK Bertram, JP Blanchet, ...", ""),
    (2019, "Ice nucleating particles in the marine boundary layer in the Canadian Arctic during summer 2014", "Atmospheric Chemistry and Physics 19, 1027-1039", "VE Irish, SJ Hanna, MD Willis, S China, JL Thomas, JJB Wentzell, ...", ""),
    (2019, "Influence of vertical mixing and nighttime transport on surface ozone variability in the morning in Paris and the surrounding region", "Atmospheric Environment 197, 92-102", "A Klein, F Ravetta, JL Thomas, G Ancellet, P Augustin, R Wilson, ...", ""),
    (2019, "Fostering multidisciplinary research on interactions between chemistry, biology, and physics within the coupled cryosphere-atmosphere system", "Elementa: Science of the Anthropocene 7, 58", "JL Thomas, J Stutz, MM Frey, T Bartels-Rausch, K Altieri, F Baladima, ...", ""),
    (2018, "Polar nighttime chemistry produces intense reactive bromine events", "Geophysical Research Letters 45, 9987-9994", "WR Simpson, U Frieß, JL Thomas, J Lampel, U Platt", ""),
    (2018, "Modeled Response of Greenland Snowmelt to the Presence of Biomass Burning‐Based Absorbing Aerosols in the Atmosphere and Snow", "Journal of Geophysical Research: Atmospheres 123, 6122-6141", "JL Ward, MG Flanner, M Bergin, JE Dibb, CM Polashenski, AJ Soja, ...", ""),
    (2017, "Local Arctic air pollution: Sources and impacts", "Ambio 46, 453-463", "KS Law, A Roiger, JL Thomas, L Marelle, JC Raut, S Dalsøren, ...", ""),
    (2017, "Improvements to the WRF-Chem 3.5.1 model for quasi-hemispheric simulations of aerosols and ozone in the Arctic", "Geoscientific Model Development 10, 3661-3677", "L Marelle, JC Raut, KS Law, LK Berg, JD Fast, RC Easter, M Shrivastava, ...", ""),
    (2017, "Characterizing the seasonal cycle and vertical structure of ozone in Paris, France using four years of ground based LIDAR measurements in the lowermost troposphere", "Atmospheric Environment 167, 603-615", "A Klein, G Ancellet, F Ravetta, JL Thomas, A Pazmino", ""),
    (2017, "Synchronous volcanic eruptions and abrupt climate change ∼17.7 ka plausibly linked by stratospheric ozone depletion", "Proceedings of the National Academy of Sciences 114, 10035-10040", "JR McConnell, A Burke, NW Dunbar, P Köhler, JL Thomas, MM Arienzo, ...", ""),
    (2017, "Cross-polar transport and scavenging of Siberian aerosols containing black carbon during the 2012 ACCESS summer campaign", "Atmospheric Chemistry and Physics 17, 10969-10995", "JC Raut, L Marelle, JD Fast, JL Thomas, B Weinzierl, KS Law, LK Berg, ...", ""),
    (2017, "Quantifying black carbon deposition over the Greenland ice sheet from forest fires in Canada", "Geophysical Research Letters 44, 7965-7974", "JL Thomas, CM Polashenski, AJ Soja, L Marelle, KA Casey, HD Choi, ...", ""),
    (2017, "Boundary layer and free-tropospheric dimethyl sulfide in the Arctic spring and summer", "Atmospheric Chemistry and Physics 17, 8757-8770", "R Ghahremaninezhad, AL Norman, B Croft, RV Martin, JR Pierce, J Burkart, ...", ""),
    (2017, "Evidence for marine biogenic influence on summertime Arctic aerosol", "Geophysical Research Letters 44, 6460-6470", "MD Willis, F Köllner, J Burkart, H Bozem, JL Thomas, J Schneider, ...", ""),
    (2017, "Microlayer source of oxygenated volatile organic compounds in the summertime marine Arctic boundary layer", "Proceedings of the National Academy of Sciences 114, 6203-6208", "EL Mungall, JPD Abbatt, JJB Wentzell, AKY Lee, JL Thomas, M Blais, ...", ""),
    (2017, "Summertime observations of elevated levels of ultrafine particles in the high Arctic marine boundary layer", "Atmospheric Chemistry and Physics 17, 5515-5535", "J Burkart, MD Willis, H Bozem, JL Thomas, K Law, P Hoor, AA Aliabadi, ...", ""),
    (2017, "Air pollution impacts due to petroleum extraction in the Norwegian Sea during the ACCESS aircraft campaign", "Elementa: Science of the Anthropocene 5, 25", "P Tuccella, JL Thomas, KS Law, JC Raut, L Marelle, A Roiger, B Weinzierl, ...", ""),
    (2016, "Analysis of the latitudinal variability of tropospheric ozone in the Arctic using the large number of aircraft and ozonesonde observations in early summer 2008", "Atmospheric Chemistry and Physics 16, 13341-13358", "G Ancellet, N Daskalakis, JC Raut, D Tarasick, J Hair, B Quennehen, ...", ""),
    (2016, "Multi-model evaluation of short-lived pollutant distributions over east Asia during summer 2008", "Atmospheric Chemistry and Physics 16, 10765-10792", "B Quennehen, JC Raut, KS Law, N Daskalakis, G Ancellet, C Clerbaux, ...", ""),
    (2016, "Ship emissions measurement in the Arctic by plume intercepts of the Canadian Coast Guard icebreaker Amundsen from the Polar 6 aircraft platform", "Atmospheric Chemistry and Physics 16, 7899-7916", "AA Aliabadi, JL Thomas, AB Herber, RM Staebler, WR Leaitch, H Schulz, ...", ""),
    (2016, "Growth of nucleation mode particles in the summertime Arctic: a case study", "Atmospheric Chemistry and Physics 16, 7663-7679", "MD Willis, J Burkart, JL Thomas, F Köllner, J Schneider, H Bozem, ...", ""),
    (2016, "Dimethyl sulfide in the summertime Arctic atmosphere: measurements and source sensitivity simulations", "Atmospheric Chemistry and Physics 16, 6665-6680", "EL Mungall, B Croft, M Lizotte, JL Thomas, JG Murphy, M Levasseur, ...", ""),
    (2016, "Analysis of nitrate in the snow and atmosphere at Summit, Greenland: Chemistry and transport", "Journal of Geophysical Research: Atmospheres 121, 5010-5030", "DL Fibiger, JE Dibb, D Chen, JL Thomas, JF Burkhart, LG Huey, ...", ""),
    (2016, "Biogenic, anthropogenic and sea salt sulfate size-segregated aerosols in the Arctic summer", "Atmospheric Chemistry and Physics 16, 5191-5202", "R Ghahremaninezhad, AL Norman, JPD Abbatt, M Levasseur, JL Thomas", ""),
    (2016, "Air quality and radiative impacts of Arctic shipping emissions in the summertime in northern Norway: from the local to the regional scale", "Atmospheric Chemistry and Physics 16, 2359-2379", "L Marelle, JL Thomas, JC Raut, KS Law, JP Jalkanen, L Johansson, ...", ""),
    (2016, "Ammonia in the summertime Arctic marine boundary layer: sources, sinks, and implications", "Atmospheric Chemistry and Physics 16, 1937-1953", "GR Wentworth, JG Murphy, B Croft, RV Martin, JR Pierce, JS Côté, ...", ""),
    (2016, "Arctic offshore hydrocarbons and the European Union: more constraints and less opportunities", "Chapter in: The Changing Arctic and the European Union", "M Łuszczuk, D Justus, J Thomas, C Klok, F Gerber", ""),
    (2016, "Arctic air pollution: Challenges and opportunities for the next decade", "Elementa: Science of the Anthropocene 4, 000104", "SR Arnold, KS Law, CA Brock, JL Thomas, SM Starkweather, ...", ""),
    (2016, "Changes in Arctic maritime transport", "Chapter in: The Changing Arctic and the European Union", "G Sander, J Gille, A Stępień, T Koivurova, J Thomas, JC Gascard, ...", ""),
    (2015, "The POLARCAT Model Intercomparison Project (POLMIP): overview and evaluation with observations", "Atmospheric Chemistry and Physics 15, 6721-6744", "LK Emmons, SR Arnold, SA Monks, V Huijnen, S Tilmes, KS Law, ...", ""),
    (2015, "Biomass burning influence on high-latitude tropospheric ozone and reactive nitrogen in summer 2008: a multi-model analysis based on POLMIP simulations", "Atmospheric Chemistry and Physics 15, 6047-6068", "SR Arnold, LK Emmons, SA Monks, KS Law, DA Ridley, S Turquety, ...", ""),
    (2015, "Transport of anthropogenic and biomass burning aerosols from Europe to the Arctic during spring 2008", "Atmospheric Chemistry and Physics 15, 3831-3850", "L Marelle, JC Raut, JL Thomas, KS Law, B Quennehen, G Ancellet, ...", ""),
    (2015, "Multi-model study of chemical and physical controls on transport of anthropogenic and biomass burning pollution to the Arctic", "Atmospheric Chemistry and Physics 15, 3575-3603", "SA Monks, SR Arnold, LK Emmons, KS Law, S Turquety, BN Duncan, ...", ""),
    (2015, "Quantifying emerging local anthropogenic emissions in the Arctic region: The ACCESS aircraft campaign experiment", "Bulletin of the American Meteorological Society 96, 441-460", "A Roiger, JL Thomas, H Schlager, KS Law, J Kim, A Schäfler, B Weinzierl, ...", ""),
    (2014, "Arctic air pollution: New insights from POLARCAT-IPY", "Bulletin of the American Meteorological Society 95, 1873-1895", "KS Law, A Stohl, PK Quinn, CA Brock, JF Burkhart, JD Paris, G Ancellet, ...", ""),
    (2014, "Summertime tropospheric ozone assessment over the Mediterranean region using the thermal infrared IASI/MetOp sounder and the WRF-Chem model", "Atmospheric Chemistry and Physics 14, 10119-10131", "S Safieddine, A Boynard, PF Coheur, D Hurtmans, G Pfister, ...", ""),
    (2014, "A review of air–ice chemical and physical interactions (AICI): liquids, quasi-liquids, and solids in snow", "Atmospheric Chemistry and Physics 14, 1587-1633", "T Bartels-Rausch, HW Jacobi, TF Kahan, JL Thomas, ES Thomson, ...", ""),
    (2013, "Pollution transport from North America to Greenland during summer 2008", "Atmospheric Chemistry and Physics 13, 3825-3848", "JL Thomas, JC Raut, KS Law, L Marelle, G Ancellet, F Ravetta, JD Fast, ...", ""),
    (2013, "The influence of snow grain size and impurities on the vertical profiles of actinic flux and associated NOx emissions on the Antarctic and Greenland ice sheets", "Atmospheric Chemistry and Physics 13, 3547-3567", "MC Zatko, TC Grenfell, B Alexander, SJ Doherty, JL Thomas, X Yang", ""),
    (2012, "Overview of the 2007 and 2008 campaigns conducted as part of the Greenland Summit Halogen-HOx Experiment (GSHOX)", "Atmospheric Chemistry and Physics 12, 10833-10839", "JL Thomas, JE Dibb, J Stutz, R Von Glasow, S Brooks, LG Huey, B Lefer", ""),
    (2012, "Halogen activation via interactions with environmental ice and snow in the polar lower troposphere and other regions", "Atmospheric Chemistry and Physics 12, 6237-6271", "JPD Abbatt, JL Thomas, K Abrahamsson, C Boxe, A Granfors, AE Jones, ...", ""),
    (2012, "Modeling chemistry in and above snow at Summit, Greenland – Part 2: Impact of snowpack chemistry on the oxidation capacity of the boundary layer", "Atmospheric Chemistry and Physics 12, 6537-6554", "JL Thomas, JE Dibb, LG Huey, J Liao, D Tanner, B Lefer, R von Glasow, ...", ""),
    (2011, "Longpath DOAS observations of surface BrO at Summit, Greenland", "Atmospheric Chemistry and Physics 11, 9899-9910", "J Stutz, JL Thomas, SC Hurlock, M Schneider, R Von Glasow, M Piot, ...", ""),
    (2011, "Observations of hydroxyl and peroxy radicals and the impact of BrO at Summit, Greenland in 2007 and 2008", "Atmospheric Chemistry and Physics 11, 8577-8591", "J Liao, LG Huey, DJ Tanner, N Brough, S Brooks, JE Dibb, J Stutz, ...", ""),
    (2011, "Modeling chemistry in and above snow at Summit, Greenland – Part 1: Model description and results", "Atmospheric Chemistry and Physics 11, 4899-4914", "JL Thomas, J Stutz, B Lefer, LG Huey, K Toyota, JE Dibb, R Von Glasow", ""),
    (2009, "Structure of large nitrate–water clusters at ambient temperatures: simulations with effective fragment potentials and force fields with implications for atmospheric chemistry", "The Journal of Physical Chemistry A 113, 12805-12814", "Y Miller, JL Thomas, DD Kemp, BJ Finlayson-Pitts, MS Gordon, DJ Tobias, ...", ""),
    (2008, "Sensitivity and uncertainty analysis of the mechanism of gas-phase chlorine production from NaCl aerosols in the MAGIC model", "Atmospheric Environment 42, 6934-6941", "P Nissenson, JL Thomas, BJ Finlayson-Pitts, D Dabdub", ""),
    (2008, "Enhanced surface photochemistry in chloride–nitrate ion mixtures", "Physical Chemistry Chemical Physics 10, 5668-5677", "LM Wingen, AC Moskun, SN Johnson, JL Thomas, M Roeselová, ...", ""),
    (2008, "Nitrate ion photochemistry at interfaces: a new mechanism for oxidation of α-pinene", "Physical Chemistry Chemical Physics 10, 3063-3071", "Y Yu, MJ Ezell, A Zelenyuk, D Imre, L Alexander, J Ortega, JL Thomas, ...", ""),
    (2007, "Direct comparisons of experimental and calculated neutron structure factors of pure solvents as a method for force field validation", "The Journal of Physical Chemistry B 111, 12941-12944", "JL Thomas, DJ Tobias, AD MacKerell", ""),
    (2007, "Molecular dynamics simulations of the solution−air interface of aqueous sodium nitrate", "The Journal of Physical Chemistry A 111, 3091-3098", "JL Thomas, M Roeselova, LX Dang, DJ Tobias", ""),
    (2006, "Gas-phase molecular halogen formation from NaCl and NaBr aerosols: When are interface reactions important?", "The Journal of Physical Chemistry A 110, 1859-1867", "JL Thomas, A Jimenez-Aranda, BJ Finlayson-Pitts, D Dabdub", ""),
    (2002, "Proton-coupled electron transfer versus hydrogen atom transfer in benzyl/toluene, methoxyl/methanol, and phenoxyl/phenol self-exchange reactions", "Journal of the American Chemical Society 124, 11142-11147", "JM Mayer, DA Hrovat, JL Thomas, WT Borden", ""),
]

PREPRINT_CONTAINERS = (
    "egusphere", "essoar", "research square", "authorea",
    "eartharxiv", "chemrxiv", "bioarchive", "preprints.org", "preprint",
)

# Copernicus discussion/preprint DOIs look like 10.5194/acp-2016-1023 or
# 10.5194/egusphere-2024-1271; versions of record look like 10.5194/acp-17-10969-2017.
PREPRINT_DOI_RE = re.compile(r"^10\.5194/(egusphere|[a-z]+)-\d{4}-\d+")
# EGU conference abstracts (10.5194/egusphere-egu26-20984) must never be used.
ABSTRACT_DOI_RE = re.compile(r"^10\.5194/egusphere-egu\d{2}-")
OLD_DISCUSSION_DOIS = ("/acpd-", "/gmdd-", "/cpd-")

# Manually verified DOIs for publications the Crossref search fails to rank well.
# Metadata (authors, journal, ...) is fetched by DOI, so only the DOI is needed.
DOI_OVERRIDES = {
    "Overview paper: New insights into aerosol and climate in the Arctic":
        "10.5194/acp-19-2527-2019",
    "Reduced global atmospheric microplastic emissions from size-harmonized observations":
        "10.21203/rs.3.rs-10231003/v1",
}


# Full first names for co-authors whose Crossref AND OpenAlex records only
# carry initials. Keys are (normalised family name, first initial); a fix only
# applies when the Crossref initials are consistent with it. Sources (verified
# 2026-10-30; see HISTORY.md): ORCID personal records, OpenAlex author profiles
# and publisher/university pages. When the build output lists a still-abbreviated
# author, verify their full name and add it here.
MANUAL_NAME_FIXES = {
    ("arnold", "s"): "Steve",          # ORCID
    ("baumann", "r"): "Robert",        # OpenAlex profile, DLR
    ("boxe", "c"): "Christopher S.",   # OpenAlex profile, Howard University
    ("brock", "c"): "Charles",         # ORCID
    ("brough", "n"): "Neil",           # ORCID
    ("browse", "j"): "Jo",             # ORCID (Crossref already full on one paper)
    ("burkhart", "j"): "John",         # ORCID
    ("denier van der gon", "h"): "Hugo",   # confirmed by Jennie (TNO, Utrecht)
    ("dahlkotter", "f"): "Florian",    # DLR publications
    ("dibb", "j"): "Jack E.",          # OpenAlex profile, University of New Hampshire
    ("duncan", "b"): "Bryan",          # ORCID
    ("emmons", "l"): "Louisa",         # ORCID
    ("fast", "j"): "Jerome",          # ORCID
    ("flemming", "j"): "Johannes",     # OpenAlex profile, ECMWF
    ("gerber", "r"): "R. Benny",       # his HUJI group page publishes "R. Benny Gerber" (rule N4)
    ("huey", "l"): "Lewis",            # ORCID ("L. Gregory Huey")
    ("kim", "s"): "Sang-Woo",          # ORCID
    ("klan", "p"): "Petr",             # confirmed by Jennie (Masaryk University)
    ("kuhs", "w"): "Werner",           # ORCID
    ("le roux", "g"): "Gaël",          # confirmed by Jennie (Toulouse)
    ("long", "y"): "Yiwen",            # ORCID
    ("minikin", "a"): "Andreas",       # ORCID
    ("nowak", "j"): "John",            # ORCID
    ("pfister", "g"): "Gabriele",      # ORCID
    ("platt", "u"): "Ulrich",          # Semantic Scholar record, Heidelberg
    ("raut", "j"): "Jean-Christophe",  # ORCID (OpenAlex full on recent papers)
    ("reiter", "a"): "Annika",         # ORCID
    ("ridley", "d"): "David A.",       # Google Scholar profile, formerly Leeds
    ("roiger", "a"): "Anke",           # DLR Institute of Atmospheric Physics
    ("scheibe", "m"): "Monika",        # OpenAlex profile, DLR
    ("schlager", "h"): "Hans",         # OpenAlex profile, DLR
    ("soja", "a"): "Amber",            # ORCID
    ("starkweather", "s"): "Sandra",   # ORCID
    ("stock", "p"): "Paul",            # OpenAlex profile, DLR
    ("stutz", "j"): "Jochen",          # ORCID
    ("toohey", "d"): "Darin",          # ORCID
    ("von glasow", "r"): "Roland",     # confirmed by Jennie (UEE at the time)
    ("von salzen", "k"): "Knut",       # confirmed by Jennie (ECCC, Canada)
    ("warneke", "c"): "Carsten",       # ORCID
    ("weinheimer", "a"): "Andrew",     # ORCID
    ("yoshida", "y"): "Yasuko",        # ORCID
}


# Co-authors whose full first name could not be verified in any source and
# which therefore stay abbreviated on the page on purpose (Jennie's decision,
# 2026-10-30). If a full name becomes known, remove the entry from here and
# add it to MANUAL_NAME_FIXES.
INTENTIONALLY_ABBREVIATED = {
    ("kim", "j"),      # ACCESS campaign, DLR Institute of Atmospheric Physics
    ("piot", "m"),     # GSHOX campaigns, LATMOS
    ("rose", "m"),     # ACCESS campaign, DLR Institute of Atmospheric Physics
}

# Given-name spelling variants to normalise before anything else (keyed by the
# normalised given name).
GIVEN_ALIASES = {
    "gael": "Gaël",                       # Gaël Le Roux; one record omits the accent
    "jean christophe": "Jean-Christophe",   # unhyphenated Crossref variant
    "katharine s": "Kathy S.",             # Kathy S. Law: 3 papers deposit "Katharine S.";
                                          # Jennie confirmed she publishes as Kathy (2026-10-30)
    "kathy": "Kathy S.",                   # Kathy S. Law without her middle initial on 2 papers;
                                          # she is the only Kathy in the list
    "chris m": "Christopher M.",           # Christopher M. Polashenski: OpenAlex profile says
                                          # "Chris"; his Dartmouth faculty page
                                          # (engineering.dartmouth.edu) and Jennie say Christopher
    "gerard m": "Gérard M.",               # Gérard Ancellet: OpenAlex says "Gerard"; theses.fr
                                          # person record and Jennie confirm the accent
    "gerard": "Gérard",                    # deposits without the middle initial keep it that way
}

# Families whose multi-token given name must be kept in full: in Spanish
# naming the second given-name slot is the first surname, not a middle name
# ("Carlos Pérez García-Pando"), and the same applies to the Portuguese
# form "Beatriz Ferreira Araujo".
MIDDLE_KEEP_FAMILIES = {"garcia pando", "araujo"}


PREPRINT_DOI_PREFIXES = (
    "10.31223/",  # EarthArXiv
    "10.22541/",  # ESSOAar
    "10.26434/",  # ChemRxiv
    "10.1101/",   # bioRxiv / medRxiv
    "10.21203/",  # Research Square
    "10.31224/",  # engrXiv / SocArXiv
)


def record_is_preprint(doi, container):
    """Detect preprint/discussion/abstract records by DOI pattern or journal name."""
    doi = (doi or "").lower()
    container = (container or "").lower()
    if "faraday discussions" in container:
        return False
    if PREPRINT_DOI_RE.match(doi):
        return True
    if doi.startswith(PREPRINT_DOI_PREFIXES) or any(d in doi for d in OLD_DISCUSSION_DOIS):
        return True
    return any(p in container for p in PREPRINT_CONTAINERS)


def norm_title(s):
    """Normalize a title into a set of alphanumeric tokens."""
    s = s.lower()
    s = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]+", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return set(s.split())


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)


def openalex_authorships(doi, retries=3):
    """Fetch [(raw_name, display_name), ...] for a DOI from OpenAlex, or None."""
    url = ("https://api.openalex.org/works/doi:"
           + urllib.parse.quote(doi, safe="")
           + "?select=authorships&mailto=" + urllib.parse.quote(MAILTO))
    for attempt in range(retries):
        time.sleep(random.uniform(0.1, 0.3))
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"jenniethomas-site-builder/1.0 ({CONTACT})"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                ships = json.load(r).get("authorships", [])
                return [
                    (sh.get("raw_author_name") or "",
                     (sh.get("author") or {}).get("display_name") or "")
                    for sh in ships
                ]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
                continue
            return None
    return None


def crossref_query(title, with_author=True, rows=8, retries=3):
    params = {
        "query.bibliographic": title,
        "rows": rows,
        "select": "DOI,title,container-title,volume,page,article-number,issued,author",
        "mailto": CONTACT,
    }
    if with_author:
        params["query.author"] = "Thomas"
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        time.sleep(random.uniform(0.2, 0.5))
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"jenniethomas-site-builder/1.0 ({CONTACT})"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)["message"]["items"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return []
        except Exception:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
                continue
            return []
    return []


def best_match(items, tokens, year=None):
    """Return the best matching Crossref item.

    Candidates must overlap >= 70% of the query title tokens and, when a
    reference year is given, be published within 3 years of it. Final versions
    are preferred over discussion/preprint versions.
    """
    if not items:
        return None
    scored = []
    for it in items:
        if ABSTRACT_DOI_RE.match(it.get("DOI") or ""):
            continue  # EGU conference abstract, not a publication
        titles = it.get("title") or [""]
        toks = norm_title(titles[0])
        if not tokens or not toks:
            continue
        score = len(tokens & toks) / len(tokens)
        if score < 0.7:
            continue
        container = (it.get("container-title") or [""])[0]
        is_preprint = record_is_preprint(it.get("DOI"), container)
        issued = (it.get("issued", {}).get("date-parts") or [[None]])[0]
        item_year = issued[0] if issued else None
        if item_year is None:
            continue
        item_year = int(item_year)
        year_penalty = abs(item_year - year) if year is not None else 0
        if year is not None and year_penalty > 3:
            continue
        # Prefer records that carry a journal name (preprints often lack one).
        unnamed = 0 if container.strip() else 1
        scored.append((is_preprint, year_penalty, -score, unnamed, it))
    if not scored:
        return None
    scored.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return scored[0][4]


# --- Author-name expansion -------------------------------------------------
#
# Many Crossref records carry initials only ("J. Stutz", "H.-W. Jacobi").
# The functions below expand such first names using OpenAlex author profiles
# and MANUAL_NAME_FIXES, guarding against wrong-person substitutions by
# requiring the candidate first name to match the Crossref initials. Crossref
# names that are already full are always kept as-is.

UNRESOLVED_AUTHORS = set()  # names still abbreviated after expansion (reported)


def clean_name(s):
    """Normalise the typography of names from external sources."""
    return ((s or "").replace("\u2010", "-").replace("\u2011", "-")
            .replace("\u202f", " ").replace("\xa0", " ").strip())


def norm_name(s):
    """Lowercase, accent-free, punctuation-free form used for matching."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _token_is_initial(tok):
    """True for initial tokens like 'J.', 'J', 'Th.', 'S.R.', 'J.-C.'."""
    parts = tok.split("-")
    if len(parts) > 1:
        return all(p and _token_is_initial(p) for p in parts)
    if re.fullmatch(r"[^\W\d_]\.?", tok):            # "J", "J."
        return True
    if re.fullmatch(r"[^\W\d_]{2}\.", tok):          # "Th."
        return True
    if re.fullmatch(r"(?:[^\W\d_]\.)+", tok):        # "S.R.", "J.L."
        return True
    return False


def given_is_abbreviated(given):
    """True if a given-name string carries only initials ('J. L.', 'H.-W.')."""
    tokens = [t for t in re.split(r"\s+", given or "") if t]
    return bool(tokens) and all(_token_is_initial(t) for t in tokens)


def initial_seq(given):
    """Initial letters implied by an abbreviated given name.

    "J. L." -> ["j", "l"]; "H.-W." -> ["h", "w"]; "Th." -> ["th"].
    """
    seq = []
    for tok in re.split(r"\s+", given or ""):
        if not _token_is_initial(tok):
            continue
        for part in tok.split("-"):
            letters = re.findall(r"[^\W\d_]", part)
            if len(letters) <= 2 and not re.fullmatch(r"(?:[^\W\d_]\.){2,}", part):
                seq.append("".join(letters).lower())      # "Th." -> "th"
            else:
                seq.extend(l.lower() for l in letters)    # "S.R." -> "s", "r"
    return seq


def merge_given(abbrev_given, candidate):
    """Combine abbreviated Crossref initials with a fuller candidate first name.

    The candidate must cover the first Crossref initial, which guards against
    a wrong-person match; Crossref initials missing from the candidate are
    appended ("M. G." + "Mark" -> "Mark G.").
    """
    initials = _merge_initials(abbrev_given)
    if not initials:
        return None
    cand_toks = [norm_name(t) for t in re.split(r"[\s-]+", candidate) if t]
    idx = 0
    for tok in cand_toks:
        if idx < len(initials) and tok.startswith(initials[idx]):
            idx += 1
    if idx == 0:
        return None
    out = clean_name(candidate)
    extra = initials[idx:]
    if extra:
        out += " " + " ".join(e.upper() + "." for e in extra)
    return out


def _merge_initials(given):
    """Initials to preserve when merging: those from initial tokens plus the
    first letter of each full token ("L. Gregory" -> ["l", "g"])."""
    seq = []
    for tok in re.split(r"\s+", given or ""):
        if not tok:
            continue
        if _token_is_initial(tok):
            seq.extend(initial_seq(tok))
        else:
            seq.append(tok[0].lower())
    return seq


def abbrev_middle(given):
    """Abbreviate middle names to initials, keeping first names full.

    "William Robert" -> "William R."; tokens that are already initials are
    kept, and leading initials before the first name stay untouched
    ("R. Benny" stays "R. Benny").
    """
    tokens = [t for t in re.split(r"\s+", given or "") if t]
    if len(tokens) < 2:
        return given
    first_full = None
    for i, t in enumerate(tokens):
        if not _token_is_initial(t):
            first_full = i
            break
    if first_full is None:
        return given                      # only initials, nothing to do
    out = tokens[:first_full + 1]
    for t in tokens[first_full + 1:]:
        out.append(t if _token_is_initial(t) else t[0].upper() + ".")
    return " ".join(out)


def _oa_family(disp):
    toks = norm_name(disp).split()
    return toks[-1] if toks else ""


def _oa_display_for(index, given, family, oa_pairs):
    """Find the OpenAlex display name that corresponds to a Crossref author."""
    if not oa_pairs:
        return None
    exact = norm_name(f"{given} {family}")
    for raw, disp in oa_pairs:
        if norm_name(raw) == exact:
            return disp
    if index < len(oa_pairs) and _oa_family(oa_pairs[index][1]) == norm_name(family):
        return oa_pairs[index][1]
    matches = [d for _, d in oa_pairs if _oa_family(d) == norm_name(family)]
    if len(matches) == 1:
        return matches[0]
    return None


def expand_given(index, given, family, oa_pairs):
    """Expand an abbreviated first name via MANUAL_NAME_FIXES or OpenAlex."""
    tokens = [t for t in re.split(r"\s+", given or "") if t]
    if not tokens or not _token_is_initial(tokens[0]):
        return given                      # first token is a full name already
    initials = _merge_initials(given)
    candidates = []
    manual = MANUAL_NAME_FIXES.get((norm_name(family), initials[0] if initials else ""))
    if manual:
        candidates.append(manual)
    disp = _oa_display_for(index, given, family, oa_pairs)
    if disp:
        disp = clean_name(disp)
        toks = disp.split()
        if len(toks) > 1 and norm_name(toks[-1]) == norm_name(family):
            disp_given = " ".join(toks[:-1])
            if disp_given and not given_is_abbreviated(disp_given):
                candidates.append(disp_given)
    for cand in candidates:
        merged = merge_given(given, cand)
        if merged:
            return merged
    if (given_is_abbreviated(given)
            and (norm_name(family), initials[0] if initials else "")
            not in INTENTIONALLY_ABBREVIATED):
        UNRESOLVED_AUTHORS.add(f"{given} {family}")
    return given


def fmt_authors(cr_authors, oa_pairs):
    """Format the author list, expanding abbreviated first names (see above)."""
    parts = []
    for i, a in enumerate(cr_authors or []):
        family = clean_name(a.get("family") or "")
        given = clean_name(a.get("given") or "")
        if family:
            full_given = expand_given(i, given, family, oa_pairs)
            full_given = GIVEN_ALIASES.get(norm_name(full_given), full_given)
            if norm_name(family) not in MIDDLE_KEEP_FAMILIES:
                full_given = abbrev_middle(full_given)
            name = f"{full_given} {family}".strip()
            is_jt = family.lower() == "thomas" and (
                not full_given or full_given.lower().startswith("j"))
        else:
            name = clean_name(a.get("name") or "")
            is_jt = False
        if not name:
            continue
        name = html.escape(name)
        parts.append(f"<strong>{name}</strong>" if is_jt else name)
    return ", ".join(parts)


def fmt_fallback_authors(raw):
    """Bold Jennie's name inside a curated fallback author string."""
    esc = html.escape(raw)
    pattern = r"(J\.?\s?L\.?\s+Thomas|Jennie\s+L\.?\s+Thomas|J\s+Thomas|Jennie\s+Thomas)"
    return re.sub(pattern, r"<strong>\1</strong>", esc)


def record_from_item(item):
    container = (item.get("container-title") or [""])[0]
    return {
        "doi": item.get("DOI"),
        "container": container,
        "volume": item.get("volume", ""),
        "page": item.get("page") or item.get("article-number", ""),
        "cr_authors": [
            {
                "given": a.get("given") or "",
                "family": a.get("family") or "",
                "name": a.get("name") or "",
            }
            for a in item.get("author") or []
        ],
    }


def fetch_by_doi(doi):
    """Fetch complete metadata for a manually verified DOI."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"jenniethomas-site-builder/1.0 ({CONTACT})"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return record_from_item(json.load(r)["message"])
    except Exception:
        return None


def build():
    UNRESOLVED_AUTHORS.clear()
    doi_overrides = {
        " ".join(sorted(norm_title(t))): d for t, d in DOI_OVERRIDES.items()
    }
    cache = load_json(CACHE)
    oa_cache = load_json(OA_CACHE)

    def oa_for(doi):
        """OpenAlex author list for a DOI (fetched once, then cached)."""
        if not doi:
            return None
        if doi not in oa_cache:
            oa_cache[doi] = openalex_authorships(doi)
        return oa_cache[doi]

    # One-time migration: cached records that predate the raw-author
    # ("cr_authors") cache format are re-fetched through their known DOI
    # (no re-search), so they keep the same DOI but now carry the raw author
    # list plus the OpenAlex names.
    for pub in PUBS:
        key = " ".join(sorted(norm_title(pub[1])))
        cached = cache.get(key)
        if not cached or not cached.get("doi") or "cr_authors" in cached:
            continue
        rec = fetch_by_doi(cached["doi"])
        if rec:
            rec["oa"] = oa_for(cached["doi"])
            cache[key] = rec
        else:
            cache.pop(key, None)

    # Decide which cached entries need to be looked up again:
    #  - misses (None) and manual overrides: always
    #  - conference-abstract matches: always
    #  - curated publications matched to a preprint or to a record with no
    #    journal name
    #  - curated preprints still matched to a preprint: re-check so that the
    #    final version is picked up automatically once the paper is accepted
    for pub in PUBS:
        key = " ".join(sorted(norm_title(pub[1])))
        cached = cache.get(key)
        if cached is None or key in doi_overrides:
            cache.pop(key, None)
            continue
        cached_doi = cached.get("doi") or ""
        if (ABSTRACT_DOI_RE.match(cached_doi)
                or record_is_preprint(cached_doi, cached.get("container"))
                or not (cached.get("container") or "").strip()):
            cache.pop(key, None)
    results = [None] * len(PUBS)
    todo = []

    for i, pub in enumerate(PUBS):
        key = " ".join(sorted(norm_title(pub[1])))
        if key in cache:
            results[i] = cache[key]
        else:
            todo.append((i, key, pub[1], pub[0], pub[4]))

    def attach_oa(rec):
        if rec:
            rec["oa"] = oa_for(rec.get("doi"))
        return rec

    def work(job):
        i, key, title, year, flag = job
        # Search Crossref for the best record. A published (non-preprint)
        # record always wins — even for entries curated as preprints, since
        # the paper may have been accepted since curation.
        item = best_match(crossref_query(title), norm_title(title), year)
        if item is None:
            # Second attempt: broader result set, no author constraint.
            item = best_match(crossref_query(title, with_author=False, rows=20),
                              norm_title(title), year)
        if item is not None:
            container = (item.get("container-title") or [""])[0]
            if not record_is_preprint(item.get("DOI"), container):
                return i, key, attach_oa(record_from_item(item))
        # Only a preprint (or nothing) was found: use the manual DOI if one
        # is recorded, otherwise the preprint match itself.
        manual_doi = doi_overrides.get(key)
        if manual_doi:
            return i, key, attach_oa(fetch_by_doi(manual_doi))
        return i, key, attach_oa(record_from_item(item)) if item else None

    if todo:
        with ThreadPoolExecutor(max_workers=1) as ex:
            for i, key, rec in ex.map(work, todo):
                results[i] = rec
                cache[key] = rec
    save_json(CACHE, cache)
    save_json(OA_CACHE, oa_cache)

    # Assemble records
    records = []
    matched = 0
    for pub, rec in zip(PUBS, results):
        year, title, venue, authors, flag = pub
        usable = False
        cr_preprint = False
        if rec and rec["doi"] and not ABSTRACT_DOI_RE.match(rec["doi"]):
            cr_preprint = record_is_preprint(rec["doi"], rec["container"])
            # A preprint record is only used when the curated entry is itself a
            # preprint; final publications need a journal name.
            has_venue = bool(rec["container"].strip()) or flag == "preprint"
            usable = has_venue and not (cr_preprint and flag != "preprint")
        if usable:
            matched += 1
            title_html = (
                f'<a href="https://doi.org/{rec["doi"]}">{html.escape(title)}</a>'
            )
            venue_parts = [rec["container"], rec["volume"], rec["page"]]
            venue_html = ", ".join(html.escape(p) for p in venue_parts if p)
            if not venue_html:
                venue_html = html.escape(venue)
            authors_html = (fmt_authors(rec.get("cr_authors"), rec.get("oa"))
                            or fmt_fallback_authors(authors))
        else:
            title_html = html.escape(title)
            venue_html = html.escape(venue)
            authors_html = fmt_fallback_authors(authors)
        # The preprints section lists only unpublished work: a curated
        # preprint moves into the year sections once its final version is
        # found on Crossref.
        in_preprints = flag == "preprint" and not (usable and not cr_preprint)
        if in_preprints and str(year) not in venue_html:
            venue_html = f"{venue_html}, {year}" if venue_html else str(year)
        records.append({
            "year": year,
            "title": title_html,
            "authors": authors_html,
            "venue": venue_html,
            "preprint": in_preprints,
        })

    # Render: preprints section first, then published work grouped by year
    def render_items(recs):
        return [
            f'<li class="pub">\n'
            f'  <div class="pub-title">{r["title"]}</div>\n'
            f'  <div class="pub-authors">{r["authors"]}</div>\n'
            f'  <div class="pub-venue"><em>{r["venue"]}</em></div>\n'
            f"</li>"
            for r in recs
        ]

    preprint_records = sorted(
        [r for r in records if r["preprint"]], key=lambda r: -r["year"]
    )
    main_records = [r for r in records if not r["preprint"]]
    years = sorted({r["year"] for r in main_records}, reverse=True)

    sections = []
    if preprint_records:
        sections.append(
            '<section class="pub-year" id="preprints">\n'
            '<h2>Preprints &amp; under review</h2>\n'
            '<ol class="pub-list">\n' + "\n".join(render_items(preprint_records)) + "\n</ol>\n</section>"
        )
    for y in years:
        pubs = [r for r in main_records if r["year"] == y]
        sections.append(
            f'<section class="pub-year" id="y{y}">\n'
            f'<h2>{y}</h2>\n'
            f'<ol class="pub-list">\n' + "\n".join(render_items(pubs)) + "\n</ol>\n</section>"
        )

    body = "\n".join(sections)
    page = PAGE_TEMPLATE.replace("{{BODY}}", body)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {OUT}")
    print(f"  {len(records)} publications, {matched} with Crossref DOIs, {len(records) - matched} using curated fallback data.")
    unmatched = [p[1] for p, r in zip(PUBS, results) if not (r and r["doi"])]
    if unmatched:
        print("  No DOI found for:")
        for t in unmatched:
            print(f"    - {t}")
    if UNRESOLVED_AUTHORS:
        print(f"  {len(UNRESOLVED_AUTHORS)} author name(s) still show only initials"
              " (verify the full name and add it to MANUAL_NAME_FIXES):")
        for n in sorted(UNRESOLVED_AUTHORS):
            print(f"    - {n}")


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Publications | Jennie L. Thomas</title>
<meta name="description" content="Publications of Jennie L. Thomas, CNRS Senior Researcher at the Institut des Géosciences de l'Environnement (IGE), Université Grenoble Alpes.">
<link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<header class="site-header">
  <div class="container nav">
    <a class="brand" href="index.html">Jennie L. Thomas<span>, PhD</span></a>
    <nav class="site-nav">
      <a href="index.html">Home</a>
      <a class="active" href="publications.html">Publications</a>
      <a href="models.html">Models</a>
      <a href="projects.html">Projects</a>
    </nav>
  </div>
</header>
<main>
<div class="page-hero">
  <div class="container">
    <h1>Publications</h1>
    <p class="pub-scholar">Citation counts and the complete record are available on <a href="https://scholar.google.com/citations?user=FMPvz8gAAAAJ&amp;hl=en">Google Scholar</a>.</p>
    <div class="pub-filter">
      <input type="search" id="pub-search" placeholder="Filter by title, author or journal&hellip;" aria-label="Filter publications">
      <span id="pub-filter-count" class="filter-count"></span>
    </div>
  </div>
</div>
<div class="container pub-container">
{{BODY}}
</div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <p class="footer-name">Jennie L. Thomas, PhD</p>
      <p>CNRS Senior Researcher<br>
      Institut des Géosciences de l'Environnement (IGE)<br>
      Université Grenoble Alpes<br>
      CS 40700, 38058 Grenoble Cedex 9, France</p>
      <p class="email">Jennie.Thomas <span class="email-at">[at]</span> univ-grenoble-alpes.fr</p>
    </div>
    <div>
      <p class="footer-heading">Links</p>
      <ul class="footer-links">
        <li><a href="https://scholar.google.com/citations?user=FMPvz8gAAAAJ&amp;hl=en">Google Scholar</a></li>
        <li><a href="https://www.ige-grenoble.fr/">IGE</a></li>
        <li><a href="https://ige-opera.github.io/">OPERA group</a></li>
      </ul>
    </div>
    <div>
      <p class="footer-heading">Credits</p>
      <p>Banner photo: <a href="https://commons.wikimedia.org/wiki/File:Arctic_Ice_2.JPG">Pink floyd88 a</a>, <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a>, via Wikimedia Commons.<br>
      Project logos: <a href="https://certainty-aci.eu">CERTAINTY</a> and <a href="https://www.crices-h2020.eu">CRiceS</a>, from their project websites, used to identify the projects.</p>
    </div>
  </div>
  <div class="container footer-bottom">
    <p>&copy; 2026 Jennie L. Thomas &middot; <a href="https://github.com/jenniethomas/jenniethomas.github.io">Site source on GitHub</a></p>
  </div>
</footer>
<script>
(function () {
  var input = document.getElementById('pub-search');
  if (!input) return;
  var pubs = Array.prototype.slice.call(document.querySelectorAll('.pub'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.pub-year'));
  var count = document.getElementById('pub-filter-count');
  function update() {
    var q = input.value.trim().toLowerCase();
    var visible = 0;
    pubs.forEach(function (p) {
      var show = !q || p.textContent.toLowerCase().indexOf(q) !== -1;
      p.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    sections.forEach(function (s) {
      var any = s.querySelectorAll('.pub:not([style*="none"])').length > 0;
      s.style.display = any ? '' : 'none';
    });
    if (count) count.textContent = q ? visible + ' of ' + pubs.length + ' publications' : '';
  }
  input.addEventListener('input', update);
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()

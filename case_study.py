import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format
pd.set_option('display.max_rows', 200)

# The answers for each question are in the bottom part of this code.
data_population = pd.read_csv("data/population/API_SP.POP.TOTL_DS2_en_csv_v2_382278.csv", skiprows=[0,2])
data_gdp = pd.read_csv("data/gdp/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_383060.csv", skiprows=[0,2])
meta_gdp_country = pd.read_csv("data/gdp/Metadata_Country_API_NY.GDP.MKTP.CD_DS2_en_csv_v2_383060.csv")

# Q1: Retrieve GDP and Population data for Bangladesh in year 1975.
gdp_bangladesh = data_gdp[data_gdp["Country Name"] == "Bangladesh"]["1975"].values[0]
pop_bangladesh = data_population[data_population["Country Name"] == "Bangladesh"]["1975"].values[0]

# Q2: Filter all countries starting with the letter "B" and retrieve their GDPs for year 1999.
b_countries = [country for country in data_gdp["Country Name"] if country[0] == "B"]
gdp_b_countries = [data_gdp[data_gdp["Country Name"] == country]["1999"].values[0] for country in b_countries]

# Q3: Retrieve all GDP and Population year columns for Iran excluding years with null values and return the years they have in common.
gdp_iran = data_gdp[data_gdp["Country Name"] == "Iran, Islamic Rep."].iloc[:, 4:-1].notnull()
gdp_iran_complete = [col for col, val in gdp_iran.items() if val.values[0] == True]
pop_iran = data_population[data_population["Country Name"] == "Iran, Islamic Rep."].iloc[:, 4:-1].notnull()
pop_iran_complete = [col for col, val in gdp_iran.items() if val.values[0] == True]
iran_complete = sorted(list(set(gdp_iran_complete).intersection(set(pop_iran_complete))))

# Q4: Compute the percentage of growth from 1984 to 1985 and return the country with the largest growth.
data_population["YoY"] = ((data_population["1985"] - data_population["1984"]) / data_population["1984"]) * 100
highest_yoy = data_population.nlargest(1, ["YoY"])["Country Name"].values[0]

# Q5: Compute the percentage of growth from 2007 to 2012, get the top three, and return the third value.
data_population["5 Year Growth"] = ((data_population["2012"] - data_population["2007"]) / data_population["2007"]) * 100
third_highest_yoy = data_population.nlargest(3, ["5 Year Growth"])["Country Name"].values[2]

# Q6: Merge GDP data and GDP region metadata and filter them by region and year 2000.
merged_gdp = meta_gdp_country.set_index("Country Code").join(data_gdp.set_index("Country Code"))
latin_caribbean = merged_gdp[merged_gdp["Region"] == "Latin America & Caribbean"]["2000"]
south_asia = merged_gdp[merged_gdp["Region"] == "South Asia"]["2000"]
subsaharan_africa = merged_gdp[merged_gdp["Region"] == "Sub-Saharan Africa"]["2000"]
europe_central_asia = merged_gdp[merged_gdp["Region"] == "Europe & Central Asia"]["2000"]
mideast_north_africa = merged_gdp[merged_gdp["Region"] == "Middle East & North Africa"]["2000"]
east_asia_pacific = merged_gdp[merged_gdp["Region"] == "East Asia & Pacific"]["2000"]
north_america = merged_gdp[merged_gdp["Region"] == "North America"]["2000"]

# Q7: Merge GDP data plus GDP region metadata with Population data.
merged_pop_gdp = data_population.merge(merged_gdp, left_on="Country Name", right_on="Country Name", suffixes=("_pop", "_gdp"))
merged_north_america = merged_pop_gdp[merged_pop_gdp["Region"] == "North America"].copy()

# Calculate the GDP Per Capita for all North American countries from years 1965 onwards.
for year in range(1960, 2020):
    try:
        gdp_per_capita = merged_north_america[str(year) + "_gdp"] / merged_north_america[str(year) + "_pop"]   
        merged_north_america["GDP Per Capita " + str(year)] = gdp_per_capita
    except KeyError:
        pass

# Retrieves columns GDP Per Capita from years 1960 to 1964 [1960, 1961, 1962, 1963, 1964] = 5 Years, 1965 to 1969, and so on.
for year in range(1960, 2020):
    try:
        gdp_cols = ["GDP Per Capita " + str(year) for year in range(year, year + 5)]
        merged_north_america["5 Year RA GDP " + str(year + 4)] = round(np.nanmean(merged_north_america[gdp_cols]), 2)
    except KeyError:
        pass

# Retrieves all 5 year rolling average of GDP per capita in North America.
all_gdp_cols = [col for col in merged_north_america.columns if "5 Year RA GDP" in col]
north_america = merged_north_america[all_gdp_cols]

# Q8: Retrieves all Income Group values for 2016 and computes the min, max, and 60th percentile for each.
high_income = merged_gdp[merged_gdp["IncomeGroup"] == "High income"]
low_income = merged_gdp[merged_gdp["IncomeGroup"] == "Low income"]
lowmid_income = merged_gdp[merged_gdp["IncomeGroup"] == "Lower middle income"]
upmid_income = merged_gdp[merged_gdp["IncomeGroup"] == "Upper middle income"]

high_income_min = high_income.nsmallest(1, ["2016"])["2016"].values[0]
high_income_max = high_income.nlargest(1, ["2016"])["2016"].values[0]
high_income_60th = high_income["2016"].quantile(0.6)

low_income_min = low_income.nsmallest(1, ["2016"])["2016"].values[0]
low_income_max = low_income.nlargest(1, ["2016"])["2016"].values[0]
low_income_60th = low_income["2016"].quantile(0.6)

lowmid_income_min = lowmid_income.nsmallest(1, ["2016"])["2016"].values[0]
lowmid_income_max = lowmid_income.nlargest(1, ["2016"])["2016"].values[0]
lowmid_income_60th = lowmid_income["2016"].quantile(0.6)

upmid_income_min = upmid_income.nsmallest(1, ["2016"])["2016"].values[0]
upmid_income_max = upmid_income.nlargest(1, ["2016"])["2016"].values[0]
upmid_income_60th = upmid_income["2016"].quantile(0.6)

gdp_income_groups = pd.DataFrame({"Income Group": ["High Income", "Low Income", "Lower Middle Income", "Upper Middle Income"], \
                                  "Minimum": [high_income_min, low_income_min, lowmid_income_min, upmid_income_min], \
                                  "Maximum": [high_income_max, low_income_max, lowmid_income_max, upmid_income_max], \
                                  "60th Percentile": [high_income_60th, low_income_60th, lowmid_income_60th, upmid_income_60th]})

print("1. What was the GDP per capita of Bangladesh in 1975?\n", round(gdp_bangladesh / pop_bangladesh, 2))
print("\n2. What is the average GDP of all countries that start with the letter B in 1999?\n", round(np.nanmean(gdp_b_countries), 2))
print("\n3. What years do we have complete data (GDP and Population) for Iran?\n", ", ".join(iran_complete))
print("\n4. Which country had the highest YoY population growth in 1985?\n", highest_yoy)
print("\n5. Which county had the 3rd highest 5 year population growth in 2012?\n", third_highest_yoy)
print("\n6. What was the average GDP per capita of each region (for reference, the regions are below) in 2000?")
print("\ta. Latin America & Caribbean - ", round(np.nanmean(latin_caribbean), 2))
print("\tb. South Asia - ", round(np.nanmean(south_asia), 2))
print("\tc. Sub-Saharan Africa - ", round(np.nanmean(subsaharan_africa), 2))
print("\td. Europe & Central Asia - ", round(np.nanmean(europe_central_asia), 2))
print("\te. Middle East & North Africa - ", round(np.nanmean(mideast_north_africa), 2))
print("\tf. East Asia & Pacific - ", round(np.nanmean(east_asia_pacific), 2))
print("\tg. North America - ", round(np.nanmean(north_america), 2))
print("\n7. Plot the 5 year rolling average of GDP per capita in North America from 1965 to the current year.", north_america.iloc[0]) 
print("\n8. What is the minimum, maximum and 60th percentile GDP of each of the income groups (for reference, the income groups are below) in 2016?\n") 
print(gdp_income_groups)

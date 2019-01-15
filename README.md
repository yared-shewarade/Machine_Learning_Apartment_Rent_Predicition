# Rent Predictor

This project is trying to figure out whether your apartment rent is reasonable based on 4000+ data from CoStar.

Data Collection:
    - Aparmtents in Austin, TX, with more than 50 units
    - This data set excludes student housing, military, senior housing and affordable housing
    
The variables includes:
    - Address
    - Bed
    - Bath
    - SF
    - Concession %
    - Built_year
    - Walk_in_Closet
    - Hardwood/Vinyl Floor
    - Washer/Dryer
    - Population
    - Median_Household_Income
    - Walk_Score
    - Transit_Score
    - Miles_From_Domain
    _ Miles_From_Downtown

Machine Learning models:
    - Linear Regression
    - Polynomial Regression
    - Random Forest
    - Neural Network
    - K Neareast Neighbour
We picked up the Random Forest model because it has the highest R squared value.

Data Sources:
    - Costar: https://www.costar.com/
    - Distance Calculator: https://www.mapdevelopers.com/distance_from_to.php
    - Walk Score: https://www.walkscore.com/
    - Population: https://www.freemaptools.com/find-population.htm
    - Median_Household Income: http://www.energyjustice.net/justice/index.php

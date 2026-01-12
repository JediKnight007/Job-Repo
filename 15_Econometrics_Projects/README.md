# Econometrics Analysis Projects (Stata)

## Project Overview
This collection contains multiple econometrics analysis projects performed in Stata, demonstrating statistical modeling, causal inference, and empirical research methods. The projects analyze real-world datasets including birthweight determinants, labor market outcomes (CPS data), and growth economics.

## Projects Included
1. **Birthweight Analysis** (`Birthweight.smcl`)
2. **Current Population Survey Analysis** (`CPS.smcl`, `CPS6.pdf`)
3. **Economic Growth Analysis** (`GrowthLog.smcl`)

## Technical Skills Demonstrated

### Econometrics
- **Regression Analysis**: OLS, Fixed Effects, Random Effects
- **Causal Inference**: Treatment effects, instrumental variables
- **Panel Data Methods**: Within-between estimators
- **Hypothesis Testing**: t-tests, F-tests, joint tests
- **Model Specification**: Variable selection, functional forms

### Statistical Methods
- **Descriptive Statistics**: Summary statistics, correlations
- **Inferential Statistics**: Confidence intervals, p-values
- **Diagnostics**: Heteroskedasticity, multicollinearity, normality
- **Robust Standard Errors**: Addressing heteroskedasticity
- **Model Comparison**: R², adjusted R², AIC, BIC

### Data Analysis
- **Data Cleaning**: Missing values, outliers, transformations
- **Variable Engineering**: Interactions, polynomials, logs
- **Visualization**: Scatter plots, residual plots, histograms
- **Interpretation**: Economic and statistical significance

## Project Structures

### 1. Birthweight Analysis (`Birthweight.smcl`)

**Research Question:** What factors determine infant birthweight?

**Variables:**
- **Dependent**: Birthweight (grams or pounds)
- **Independent**: 
  - Mother's age, education, race
  - Smoking behavior
  - Prenatal care
  - Previous births
  - Father's characteristics

**Methods:**
- OLS regression
- Log-linear models
- Interaction terms
- Heteroskedasticity-robust standard errors

**Key Findings:**
- Smoking has significant negative effect on birthweight
- Education positively associated with birthweight
- Prenatal care improves outcomes
- Non-linear age effects

**Policy Implications:**
- Smoking cessation programs for pregnant women
- Importance of prenatal care access
- Targeted interventions for at-risk populations

### 2. Current Population Survey Analysis (`CPS.smcl`, `CPS6.pdf`)

**Research Question:** What determines wages and labor market outcomes?

**Dataset:** CPS (Current Population Survey)
- Monthly survey of ~60,000 households
- Key labor force statistics
- Demographics and earnings

**Variables:**
- **Wage**: Hourly wage or annual earnings
- **Education**: Years of schooling, degrees
- **Experience**: Actual or potential experience
- **Demographics**: Age, gender, race
- **Location**: State, metropolitan area
- **Industry/Occupation**: Job characteristics

**Methods:**
- Mincer wage equation
- Returns to education
- Gender wage gap analysis
- Oaxaca-Blinder decomposition (possible)

**Typical Results:**
- Education premium: ~8-12% per year
- Experience returns: concave (diminishing)
- Gender gap: controlling for observables
- Regional wage differences

**Economic Interpretations:**
- Human capital theory
- Discrimination vs. productivity differences
- Labor market segmentation
- Skill-biased technological change

### 3. Economic Growth Analysis (`GrowthLog.smcl`)

**Research Question:** What drives economic growth across countries?

**Typical Variables:**
- **GDP growth rate**: Annual or long-term average
- **Initial GDP**: Level effect or convergence
- **Investment**: Physical capital accumulation
- **Human capital**: Education levels
- **Population growth**: Labor force expansion
- **Institutions**: Rule of law, property rights
- **Trade openness**: Exports + imports / GDP

**Methods:**
- Growth regressions (Solow model extensions)
- Panel data methods
- Convergence analysis (β-convergence)
- Instrument variables (geography, history)

**Key Concepts:**
- Conditional convergence
- Total Factor Productivity (TFP)
- Steady-state growth
- Growth accounting

**Typical Findings:**
- Negative relationship between initial GDP and growth (convergence)
- Investment positively affects growth
- Human capital crucial for long-run growth
- Institutions matter for sustained growth

## Technical Implementation

### Stata Commands Used

**Data Management:**
```stata
* Load data
use "birthweight.dta", clear

* Summary statistics
summarize birthweight age education smoking

* Describe variables
describe

* Generate new variables
gen log_wage = log(wage)
gen experience_sq = experience^2

* Recode categorical variables
recode race (1=1) (2=2) (3/6=3), gen(race_cat)
```

**Regression Analysis:**
```stata
* Basic OLS
reg birthweight age education smoking

* With robust standard errors
reg birthweight age education smoking, robust

* Multiple models
reg birthweight age education
est store model1
reg birthweight age education smoking
est store model2
reg birthweight age education smoking prenatal
est store model3

* Compare models
esttab model1 model2 model3, se r2

* Test joint significance
test smoking prenatal

* Predicted values and residuals
predict yhat
predict resid, residuals
```

**Panel Data:**
```stata
* Set panel structure
xtset id year

* Fixed effects
xtreg wage education experience, fe

* Random effects
xtreg wage education experience, re

* Hausman test
hausman fe re
```

**Diagnostics:**
```stata
* Heteroskedasticity test
estat hettest

* Normality of residuals
histogram resid, normal

* VIF for multicollinearity
vif

* Outliers
dfbeta
```

**Visualization:**
```stata
* Scatter plot with fit line
scatter birthweight age || lfit birthweight age

* Box plots by group
graph box wage, over(education)

* Histogram
histogram wage, normal

* Residual plots
rvfplot
```

## Technical Environment
- **Software**: Stata (version 14+)
- **File Format**: .smcl (Stata Markup and Control Language)
- **Data Formats**: .dta (Stata datasets)
- **Output**: .pdf (reports), .smcl (logs)

## Skills & Technologies
- **Stata Programming**: Advanced command syntax, do-files
- **Econometric Theory**: Understanding of estimators and inference
- **Statistical Software**: Proficiency with Stata ecosystem
- **Research Design**: Formulating testable hypotheses
- **Academic Writing**: Interpreting and presenting results
- **Data Visualization**: Creating publication-quality graphs

## Econometric Concepts

### 1. Ordinary Least Squares (OLS)
```
Y = β₀ + β₁X₁ + β₂X₂ + ... + βₖXₖ + ε

Assumptions:
- Linearity
- No perfect multicollinearity
- Zero conditional mean: E[ε|X] = 0
- Homoskedasticity: Var(ε|X) = σ²
- No autocorrelation
- Normality (for inference)
```

### 2. Omitted Variable Bias
```
Bias(β̂₁) = β₂ * Cov(X₁, X₂) / Var(X₁)

where:
- X₂ is omitted variable
- β₂ is true effect of X₂
```

### 3. R-squared
```
R² = 1 - (SSR / SST)

where:
- SSR = Sum of Squared Residuals
- SST = Total Sum of Squares
```

### 4. Hypothesis Testing
```
t-statistic = (β̂ - β₀) / SE(β̂)

F-statistic = (SSR_restricted - SSR_unrestricted) / q
              ------------------------------------------
              SSR_unrestricted / (n - k - 1)
```

## Applications & Use Cases

### Labor Economics
- Wage determination
- Returns to education
- Gender/racial wage gaps
- Unemployment analysis
- Labor supply decisions

### Health Economics
- Determinants of health outcomes
- Healthcare utilization
- Insurance effects
- Policy evaluation

### Development Economics
- Growth determinants
- Poverty analysis
- Foreign aid effectiveness
- Institutional quality

### Public Policy
- Program evaluation
- Cost-benefit analysis
- Impact assessments
- Causal inference

## Data Sources

### Common Datasets:
- **CPS**: Current Population Survey (labor force)
- **PSID**: Panel Study of Income Dynamics
- **NLSY**: National Longitudinal Survey of Youth
- **Penn World Tables**: Cross-country growth
- **World Bank**: Development indicators
- **IPUMS**: Census microdata
- **NBER**: Various economic datasets

## Learning Outcomes
These projects demonstrate:
- Mastery of econometric methods
- Stata programming proficiency
- Ability to conduct empirical research
- Understanding of causal inference
- Data analysis and interpretation skills
- Academic research standards

## Real-World Applications

### Academic Research
- Publishing in economics journals
- PhD dissertation chapters
- Working papers

### Policy Analysis
- Government agencies (CBO, GAO, Fed)
- Think tanks (NBER, Brookings)
- International organizations (World Bank, IMF)

### Industry
- Economic consulting firms
- Financial institutions (forecasting)
- Tech companies (A/B testing, causal inference)
- Healthcare analytics

### Career Paths
- Economic research analyst
- Data scientist (with economics focus)
- Policy analyst
- Quantitative researcher
- Academic economist
- Econometrician

## Advanced Topics (Possibly Covered)

### Causal Inference Methods:
- **Instrumental Variables (IV)**: Addressing endogeneity
- **Difference-in-Differences (DiD)**: Policy evaluation
- **Regression Discontinuity (RD)**: Treatment effects at cutoffs
- **Propensity Score Matching**: Observational studies
- **Synthetic Control**: Comparative case studies

### Time Series:
- **ARIMA**: Autoregressive models
- **VAR**: Vector autoregressions
- **Cointegration**: Long-run relationships
- **GARCH**: Volatility modeling

### Panel Data:
- **Fixed Effects**: Control for time-invariant heterogeneity
- **Random Effects**: Efficient under assumptions
- **Dynamic Panels**: Lagged dependent variables
- **GMM**: Generalized Method of Moments

## Interpretation Guidelines

### Statistical Significance:
- *** p < 0.01 (highly significant)
- ** p < 0.05 (significant)
- * p < 0.10 (marginally significant)

### Economic Significance:
- Magnitude of effect (not just p-value)
- Practical importance
- Cost-benefit considerations

### Causality vs. Correlation:
- Association ≠ causation
- Need identifying assumptions
- Robustness checks crucial

## Quality Indicators
Good econometric analysis includes:
- Clear research question
- Appropriate methodology
- Robust standard errors
- Multiple specifications
- Diagnostic tests
- Sensitivity analysis
- Thoughtful interpretation

## Common Pitfalls Avoided
- **Omitted variable bias**: Include relevant controls
- **Reverse causality**: Use IV or experiments
- **Measurement error**: Acknowledge limitations
- **Sample selection**: Heckman correction
- **Overfitting**: Adjusted R², cross-validation
- **Publication bias**: Report all results

## Further Resources

### Textbooks:
- Wooldridge, "Introductory Econometrics"
- Stock & Watson, "Introduction to Econometrics"
- Angrist & Pischke, "Mostly Harmless Econometrics"
- Greene, "Econometric Analysis"

### Software:
- Stata documentation and manuals
- UCLA Stata resources
- Princeton Stata tutorial
- Stata Journal articles


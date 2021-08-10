# Jordan_Belf

This is all the files for the hegde fund algorithims under development for use by Alec Mamo, Mason Quant and Mark McCoy

This code is written for Python 3.8
Packages you need to install via pip:
backtrader - base library for strategy and backtesting
Ibpy2 - Broker API
matplotlib (version 3.2.2) - Used for plotting in backtesting
numpy - Used for calculations
statistics - Used for calculations 
pandas - Dataframe structure for backtesting 
yfinance - Dataframe data collection when backtesting


install packages using the requirement.txt 
$pip install -r requirements.txt
Make sure you are in the right directory as well, if you saved the requirements.txt to a folder like downloads
Then cd to downloads before running this code through this command
$cd Downloads

***



# Coding Standards
1. Camel case for local variables `string mamosHair = "nappy";`
2. Constants are all uppercase `int CONSTANT = 100`
3. `if`, `else if`, `else` statements have `{}` following them unless there is one line of code following. Ex:
```
if (condition)
    printf("Hi");
else{
    printf("else");
    call_function();
}
```
4. Make meaningful variable names
5. Comment throughout code why you made things the way they are

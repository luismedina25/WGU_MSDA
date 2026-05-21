# Model to predict airport departure delays

# Much of this model is taken from the work of Fabien Daniel:
# https://www.kaggle.com/code/fabiendaniel/predicting-flight-delays-tutorial/notebook.  
# The difference here is that we are modeling delays for all arrival airports and all airlines given a single departure airport.

# We also incorporate MLflow tracking using the Python API.

# Input parameters for this script include:
# * num_alpha_increments:  The number of different Ridge regression alpha penalty values to try, spaced by 0.2 apart
  
# Dependencies:
# * cleaned_data.csv is the input data file, structured appropriately.  The structure of this data file must be:

# YEAR (integer),MONTH (integer),DAY (integer),DAY_OF_WEEK (integer),ORG_AIRPORT (character), DEST_AIRPORT (character),
# SCHEDULED_DEPARTURE (integer),DEPARTURE_TIME(integer),DEPARTURE_DELAY (integer),SCHEDULED_ARRIVAL(integer),ARRIVAL_TIME (integer),
# ARRIVAL_DELAY (integer)

# Outputs:
# * log file named "polynomial_regression.txt" containing information about the model training process
# * MLFlow experiment named with current date containing model training runs, one for each value of the Ridge regression penalty


## ----imports--------------------------------------------------------------------------
library(tidyverse)
library(caret)
library(stringr)
library(anytime)
library(lubridate)
library(mlflow)
library(logger)
library(mltools)
library(glmnet)
library(reticulate)
library(CatEncoders)
library(data.table)
library(jsonlite)
library(ggplot2)
library(ggExtra)

## ----activate mlflow------------------------------------------------------------------

# Uncomment 3 lines below for testing if not using MLProject file 
use_condaenv(condaenv="pipeliner",conda="auto")
system2(command="mlflow", args="server", wait=FALSE)
Sys.sleep(10)

## ----arg parsing----------------------------------------------------------------------
options(echo=TRUE) # if you want see commands in output file
args <- commandArgs(trailingOnly = TRUE)

## ----logthis--------------------------------------------------------------------------

log_threshold(DEBUG)

log_appender(appender_file(
  "polynomial_regression.txt",
  append = TRUE,
  max_lines = Inf,
  max_bytes = Inf,
  max_files = 1L
))

logger <- layout_glue_generator(
  format <- "[{format(time, \"%Y-%m-%d %H:%M:%S\")}] {level} {msg}")

log_layout(logger)
log_formatter(formatter_paste)
log_info("Flight Departure Delays Polynomial Regression Model Log")

## ----import dataset-------------------------------------------------------------------

num_lambda_increments <- as.numeric(args[1])
## Uncomment line below and comment line above if testing not from command line
# num_lambda_increments <- 20
df <- read.csv("cleaned_data_R.csv")
df[, c(7:12)] <- sapply(df[, c(7:12)], as.character)

## ----aggregate stats------------------------------------------------------------------
get_stats <- function(data) {
  aggs <- c(
    "min"=data.min(),
    "max"=data.max(),
    "count"=data.count(),
    "mean"=data.mean()
  )
}

## ----grab month year------------------------------------------------------------------
grab_month_year <-function(data) {
  months <- unique(data$MONTH)
  years <- unique(data$YEAR)
  if (length(months) > 1) {
    stop("Multiple months found in data set, only one acceptable")
  }
  else {
    monthnum <- first(months)
  }
  if (length(years) > 1) {
    stop("Multiple years found in data set, only one acceptable")
  }
  else {
    yearnum <- first(years)
  }
  monthyear <- c(monthnum,yearnum)
}

## ----define hour format---------------------------------------------------------------
format_hour <- function(string) {
  if (is.null(string)) {
    ftime <- NULL
  } else {
    if (any(string != "2400")) {
      string <- str_pad(string,4,pad="0")
      hrs <- strtoi(substring(string,1,2), base=10L)
      minutes <- as.double(substring(string,3,4),base=10L)
      ftime <- hms::hms(hours=hrs, minutes=minutes)
    } else {string <- "0"}
  }
 return <- ftime
}

## ----combine date hour----------------------------------------------------------------
combine_date_hour <- function(x) {
  if (is.null(x[0]) | is.null(x[1])) {
    print("Caught")
    return <- NA_integer_
  } else {
    return <- as.POSIXct(paste(x[[1]], x[[2]]), tz="",format="%Y-%m-%d %H:%M:%S")
  }
}

## ----flight_time----------------------------------------------------------------------
check_date_time <- function(df) {
  if (is.null(df[2])) {
    print("Caught null")
    return <- NaN
  }
  else if (df[2]==2400) {
    newdt <- c(as.Date(df[1] + 1))
    newtime <- c(hms(0,0,0))
    #print(newtime)
    combine_these <- data.frame(newdt,newtime)
    #print(combine_these)
    return <- combine_date_hour(combine_these)
  }
  else {

    df[2] <- format_hour(df[2])
    #print(df[2])
    return <- combine_date_hour(df)
  }
}

## ----create flight time---------------------------------------------------------------
create_flight_time <- function(dfin, column) {

  temp <- data.frame(dfin$DATE,dfin[column])
  temp$new <- by(temp,seq_len(nrow(temp)),check_date_time)
  temp$new <- anytime(temp$new)
  de_column <- temp[['new']]
  return <- as.character(de_column)
}

## -------------------------------------------------------------------------------------
create_seconds <- function(atime) {
  
  if (class(atime)=="character") {
    atime <- as.POSIXct(atime,tz="",format="%H:%M:%S")
  }
  num_seconds <- hour(atime)*3600 + minute(atime)*60 + second(atime)
  return <- num_seconds
}

## ----create training df---------------------------------------------------------------
create_df <- function(df) {
  # select only certain columns for the training data frame
  df2 <- df[c("SCHEDULED_DEPARTURE","SCHEDULED_ARRIVAL","DEST_AIRPORT","DEPARTURE_DELAY","DAY_OF_WEEK")]
  # omit NAs
  df2 <- na.omit(df2)
  # delete departure delays greater than 60 minutes
  subset(df2, DEPARTURE_DELAY<60)
  # force numeric values to that data type
  df2 <- type.convert(df2,as.is=TRUE)
  # formatting times
  df2$SCHEDULED_DEPARTURE <- ymd_hms(df2$SCHEDULED_DEPARTURE)
  # Uncomment line above and comment line below to run in RScript rather than 
  # RStudio - these two approaches pass datetimes differently
  #df2$SCHEDULED_DEPARTURE <- as.POSIXct(df2$SCHEDULED_DEPARTURE, tz="",format="%Y-%M-%D %H:%M:%S")
  df2$hour_depart <- hour(df2$SCHEDULED_DEPARTURE)*3600 + minute(df2$SCHEDULED_DEPARTURE)*60 + second(df2$SCHEDULED_DEPARTURE)
  df2$hour_arrive <- apply(df2[c('SCHEDULED_ARRIVAL')],1,create_seconds)
  df2 <- df2[c("hour_depart","hour_arrive","DEST_AIRPORT","DEPARTURE_DELAY","DAY_OF_WEEK")]
  # group by hour_depart, hour_arrive, DEST_AIRPORT and take mean of other columns
  df3 <- aggregate(df2[,4:5],list(df2$hour_depart,df2$hour_arrive,df2$DEST_AIRPORT),mean)
  colnames(df3) <- c("hour_depart", "hour_arrive","DEST_AIRPORT","DEPARTURE_DELAY","DAY_OF_WEEK")
  return <- df3
}

## ----splitdata------------------------------------------------------------------------
split_data <- function(df) {
  temp <- as.Date(df$SCHEDULED_DEPARTURE)
}

## ----set up date----------------------------------------------------------------------
tformat <- "%Y-%m-%d"
df$DATE <- as.POSIXct(paste(df$YEAR,df$MONTH,df$DAY,sep="-"), tz="", tformat)

## ----setup1---------------------------------------------------------------------------
nowdate <- Sys.Date()
# The next two lines configure the mlflow API to point to the mlflow server and
# port.
mlflow_set_tracking_uri("http://127.0.0.1:5000")
options("mlflow.port" = 5000)
experimentname <- paste("Airport Departure Delays, experiment run on ",format(nowdate, "%m-%d-%Y"))
# creates new experiment if there is not one yet today, otherwise sets the
# experiment for the existing one today
experiment <- mlflow_set_experiment(experiment_name = experimentname)
# extract month and year from data set
month_n_year <- grab_month_year(df)
month_num <- month_n_year[1]
year_num <- month_n_year[2]
log_info("Month and year of data: {month_num} {year_num}")
# format flight times 
df$SCHEDULED_DEPARTURE <- create_flight_time(df,"SCHEDULED_DEPARTURE")
df$DEPARTURE_TIME <- format_hour(df$DEPARTURE_TIME)
df$SCHEDULED_ARRIVAL <- format_hour(df$SCHEDULED_ARRIVAL)
df$ARRIVAL_TIME <- format_hour(df$ARRIVAL_TIME)

## ----datasplit------------------------------------------------------------------------
df_train <- df %>% filter(as.Date(SCHEDULED_DEPARTURE) < as.Date(paste(year_num,month_num,"23",sep="-"),"%Y-%m-%d"))
df_test <- df %>% filter(as.Date(SCHEDULED_DEPARTURE) >= as.Date(paste(year_num,month_num,"23",sep="-"),"%Y-%m-%d"))

## ----create_train_set-----------------------------------------------------------------
df3 <- create_df(df_train)

## ----label_airports-------------------------------------------------------------------

# create label encoder for destination airports
integer_encoded <- LabelEncoder.fit(df3$DEST_AIRPORT)
label_airports <- attr(integer_encoded, which="mapping")

## ----one_hot--------------------------------------------------------------------------
# create a one-hot encoder for destination airports
onehot_encode <- function(df) {
  onehot <- as.factor(df$DEST_AIRPORT)
  onehot_encoded <- OneHotEncoder.fit(as.data.table(onehot))
  newdata <- transform(onehot_encoded, as.data.table(onehot),sparse=FALSE)
  log_info("Airport one-hot encoding successful")
  return <- newdata
}

## ----create_arrays--------------------------------------------------------------------

h_depart <- array(unlist(df3$hour_depart))
h_arrive <- array(unlist(df3$hour_arrive))
X <- cbind(onehot_encode(df3), h_depart, h_arrive)
Y = data.frame(as.numeric(df3$DEPARTURE_DELAY))


## ----train test split-----------------------------------------------------------------
# split data at 70% train, 30% test
sample <- sample(c(TRUE, FALSE), nrow(X), replace=TRUE, prob=c(0.7,0.3))
X_train  <- X[sample, ]
X_test   <- X[!sample, ]
Y_train  <- data.frame(Y[sample, ])
Y_test   <- data.frame(Y[!sample, ])

## ----mflow_run------------------------------------------------------------------------

#mlflow_set_tag("Name",runname)
score_min <- 10000
# glmnet calls the redge penalty coefficient lambda, not alpha like scikit-learn
lambda_max <- num_lambda_increments * 2
count <- 1
lambdas <- seq(0,lambda_max, by=2)
lambdas <- lambdas / 10
# fit the training data using a ridge regressor with provided range of lambdas
X_m <- as.matrix(X)
X_train_m <- as.matrix(X_train)
Y_train_m <- as.matrix(Y_train)
X_test_m <- as.matrix(X_test)
ridgereg <- glmnet(X_train_m, Y_train_m, alpha = 0, lambda  = lambdas)
for (lambda in seq(0,lambda_max, by=2)) {
  runname <- paste("Run started at: ",format(Sys.time(), "%H:%m"))
  run_num <- paste("Training run number: ",as.character(count))
  # perform delay predictions with the model fit to the validation data with 
  # the given lambda
  ridge_pred <- predict(ridgereg,X_test_m,s=lambda/10)
  # calculate RMSE for the prediction with the given lambda
  score <- rmse(ridge_pred,Y_test)
  print(score)
  with(mlflow_start_run(experiment_id = experiment, nested=TRUE), {
    #mlflow_set_tag("Name",run_num)
    mlflow_set_tag("Run time",runname)
    mlflow_log_param(paste("lambda ",as.character(count)),lambda/10)
    mlflow_log_metric(paste("Training Mean Squared Error ", as.character(count)),score)
    mlflow_log_metric(paste("Training Average Delay ",as.character(count)),sqrt(score))
    
  })
  if(score < score_min) {
    score_min <- score
    lambda_min <- lambda
  }
  count <- count + 1
  log_info("n=1, alpha={lambda/10}, MSE = {score}")
}
  # predict using optimal lambda
final_train_pred <- predict(ridgereg,X_m,s=lambda_min)
  # calculate RMSE for all training data (test+validate) with optimal lambda
best_score <- rmse(final_train_pred,Y)

with(mlflow_start_run(experiment_id=experiment, nested=TRUE), {
  mlflow_log_metric("Validation Mean Squared Error",best_score)
  mlflow_log_metric("Validation Average Delay", sqrt(best_score))
  log_info("Training Data Final MSE = {best_score}")
})

log_info("Model training loop completed with {count-1} iterations")

## ----create_test_dataframe------------------------------------------------------------

df3 <- create_df(df_test)

## ----export_json----------------------------------------------------------------------

label_airpots <- label_airports[,c(2,1)]
exportJSON <- toJSON(label_airports,dataframe="values")
write(exportJSON, "airport_encodings.json")
log_info("Export of airport one-hot encoding successful")

## ----predict_test_data----------------------------------------------------------------

h_depart <- array(unlist(df3$hour_depart))
h_arrive <- array(unlist(df3$hour_arrive))
X_test <- cbind(onehot_encode(df3), h_depart, h_arrive)
Y_test <- data.frame(as.numeric(df3$DEPARTURE_DELAY))
X_test_m <- as.matrix(X_test)
Y_test_m <- as.matrix(Y_test)
result <- predict(ridgereg,X_test_m,s=lambda_min)
testscore <- rmse(result,Y_test)
log_info("Test Data Mean Square Error = {testscore}")
log_info("Predictions using test data successful")
log_info("Test data average departure delay = {sqrt(score)}")
print(sqrt(testscore))

## ----export_model---------------------------------------------------------------------

saveRDS(ridgereg, file="finalized_model.rda")
log_info("Final model export successful")

## ----create_final_plot----------------------------------------------------------------

plotdata <- data.frame(result,Y_test)
colnames(plotdata) <- c("predictions", "actual")
#exact_line <- data.frame(seq(-10,25,by=1),seq(-10,25,by=1))
p1 <- ggplot(plotdata, aes(actual, predictions)) + xlab("Mean delays (min)") + ylab("Predicted delay (min)") + geom_point() + geom_smooth(method="lm") + geom_abline(slope=1,intercept=0, colour='red', linetype='dashed')
                                              
p2 <- ggMarginal(p1,type="histogram", fill="lightblue")
ggsave("model_performance_R.jpg", plot=p2)

## ----redefine_uri---------------------------------------------------------------------

# need to redefine mlflow tracking URI to save additional runs
mlflow_set_tracking_uri("http://127.0.0.1:5000")

# TO DO: create an MLFlow run within the current experiment that logs the following as artifacts, parameters, 
# or metrics, as appropriate, within the experiment: 
# 1.  The informational log files generated from the import_data and clean_data scripts
# 2.  the input parameters (alpha and order) to the final regression against the test data
# 3.  the performance plot
# 4.  the model performance metrics (mean squared error and the average delay in minutes)


with(mlflow_start_run(experiment_id = experiment, nested=TRUE), {
  # YOUR CODE GOES HERE
})
CREATE TABLE CHURN (
RowNumber INT NOT NULL,
CustomerId INT NOT NULL,
Surname VARCHAR(20) NULL,
CreditScore INT NULL,
Geography VARCHAR(20) NULL,
Gender VARCHAR(20) NULL,
Age INT NULL,
Tenure INT NULL,
Balance DECIMAL(10,2) NULL,
NumOfProducts INT NULL,
HasCrCard INT NULL,
IsActiveMember INT NULL,
EstimatedSalary DECIMAL(10,2) NULL,
Exited INT NULL,
PRIMARY KEY(RowNumber)
);
.separator ','
.mode "csv"
.import "somedata" Data



axc
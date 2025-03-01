# Import All the Necessary Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load the training data
traindf = pd.read_csv('train.csv')

# Display the column names to identify the correct feature and target columns
print("Column Names:\n", traindf.columns)

# Extract numeric columns and check correlation with SalePrice
numeric_df = traindf.select_dtypes(include='number')
correlation_matrix = numeric_df.corr()
print(correlation_matrix['SalePrice'].sort_values(ascending=False))

# Select relevant features based on correlation
req_tr = ["GarageArea", "OverallQual", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GrLivArea", "BsmtFullBath", "BsmtHalfBath", "FullBath", "HalfBath", "TotRmsAbvGrd", "SalePrice"]
selected_tr = traindf[req_tr]

# Create new features TotalBath and TotalSF
selected_tr['TotalBath'] = (selected_tr['BsmtFullBath'].fillna(0) + 
                            selected_tr['BsmtHalfBath'].fillna(0) + 
                            selected_tr['FullBath'].fillna(0) + 
                            selected_tr['HalfBath'].fillna(0))

selected_tr['TotalSF'] = (selected_tr['TotalBsmtSF'].fillna(0) + 
                          selected_tr['1stFlrSF'].fillna(0) + 
                          selected_tr['2ndFlrSF'].fillna(0) + 
                          selected_tr['LowQualFinSF'].fillna(0) + 
                          selected_tr['GrLivArea'].fillna(0))

# Select final features for training
train_df = selected_tr[['TotRmsAbvGrd', 'TotalBath', 'GarageArea', 'TotalSF', 'OverallQual', 'SalePrice']]
print(train_df.head())

# Split the data into training and testing sets
train_set, test_set = train_test_split(train_df, test_size=0.2, random_state=42)
print(f"Rows in train set: {len(train_set)}\nRows in test set: {len(test_set)}\n")

# Prepare the data for training
housing = train_set.drop("SalePrice", axis=1)
housing_labels = train_set["SalePrice"].copy()

# Create a pipeline for data preprocessing
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

my_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy="median")),
    ('std_scaler', StandardScaler())
])

# Transform the training data
X_train = my_pipeline.fit_transform(housing)
Y_train = housing_labels

# Visualize the pairplot
sns.pairplot(train_df)
plt.tight_layout()
plt.show()

# Visualize the heatmap
corr_matrix = train_df.corr()
sns.heatmap(corr_matrix, annot=True)
plt.show()

# Load the test data
testdf = pd.read_csv('test.csv')
req_tst = ["GarageArea", "OverallQual", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GrLivArea", "BsmtFullBath", "BsmtHalfBath", "FullBath", "HalfBath", "TotRmsAbvGrd"]
selected_tst = testdf[req_tst]

# Create new features TotalBath and TotalSF in test data
selected_tst['TotalBath'] = (selected_tst['BsmtFullBath'].fillna(0) + 
                             selected_tst['BsmtHalfBath'].fillna(0) + 
                             selected_tst['FullBath'].fillna(0) + 
                             selected_tst['HalfBath'].fillna(0))

selected_tst['TotalSF'] = (selected_tst['TotalBsmtSF'].fillna(0) + 
                           selected_tst['1stFlrSF'].fillna(0) + 
                           selected_tst['2ndFlrSF'].fillna(0) + 
                           selected_tst['LowQualFinSF'].fillna(0) + 
                           selected_tst['GrLivArea'].fillna(0))

test_df_unproc = selected_tst[['TotRmsAbvGrd', 'TotalBath', 'GarageArea', 'TotalSF', 'OverallQual']]
test_df = test_df_unproc.fillna(test_df_unproc.mean())
x_test = my_pipeline.transform(test_df.values)

# Train the model using RandomForestRegressor
model = RandomForestRegressor()
model.fit(X_train, Y_train)

# Make predictions on the training set
y_train_pred = model.predict(X_train)

# Display the first few predictions
print("First few predictions on training set:", y_train_pred[:5])

# Display actual values for comparison
print("Actual values:", list(housing_labels[:5]))

# Evaluate the model
train_mse = mean_squared_error(Y_train, y_train_pred)
train_rmse = np.sqrt(train_mse)
print(f"Training MSE: {train_mse:.2f}, Training RMSE: {train_rmse:.2f}")

# Perform cross-validation
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X_train, Y_train, scoring="neg_mean_squared_error", cv=10)
rmse_scores = np.sqrt(-scores)

# Print cross-validation scores
def print_scores(scores):
    print("Scores:", scores)
    print("Mean:", scores.mean())
    print("Standard Deviation:", scores.std())

print_scores(rmse_scores)

# Make predictions on the test set
y_pred = model.predict(x_test)
print("Predicted prices for the test set:", y_pred)

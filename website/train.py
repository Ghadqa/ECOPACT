import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


df = pd.read_csv("dataset.csv",delimiter=';')
df


# In[3]:


import pandas as pd
import random

df['Date'] = pd.to_datetime(df['Date'])

# Définition des intervalles pour chaque mois
intervals = {
  'Dec': (0.1,0.2),
    'Jan': (0.3,0.4),
    'Feb': (0.2,0.5),
    'Mar': (0.53,0.71),
    'Apr': (0.52,0.75),
    'May': (0.75,0.95),
    'Jun': (1.30, 2.35),
    'Jul': (2.35,3.37),
    'Aug': (3.37, 4.40),
    'Sep': (0.88,2.38 ),
    'Oct': (0.78,1.25),
    'Nov': (0.18, 0.35)
}

# Génération de valeurs aléatoires selon les intervalles définis
for month, interval in intervals.items():
    month_indices = df['Date'].dt.strftime('%b') == month
    df.loc[month_indices, 'NH4'] = [random.uniform(interval[0], interval[1]) for _ in range(sum(month_indices))]


# In[4]:


def remplir_colonne_code(df):
    noms_colonnes_code_1 = ['NH4', 'Ammonium','ammonium']
    noms_colonnes_code_2 = ['Phosphate', 'PxOy','phosphate']
   
    df['code'] = df.apply(lambda row: 
                          1 if any(nom_colonne in row.index and pd.notna(row[nom_colonne]) for nom_colonne in noms_colonnes_code_1) 
                          else 2 if any(nom_colonne in row.index and pd.notna(row[nom_colonne]) for nom_colonne in noms_colonnes_code_2)
                          else 0, axis=1)


# In[5]:


remplir_colonne_code(df)
df


# In[6]:


def filtrer_et_renommer(dataframe, colonnes_voulues):
    

    dataframe_filtre = dataframe[colonnes_voulues]

    dataframe_filtre.columns = ['ID_Station', 'DATE', 'Taux']

    return dataframe_filtre


# In[7]:


resultat = filtrer_et_renommer(df,['ID_Station', 'Date', 'NH4'])
resultat


# In[8]:


df_copy = resultat.copy()
print(df_copy)


# In[9]:


df_copy['DATE'] = pd.to_datetime(df_copy['DATE'])

df_copy['Annee'] = df_copy['DATE'].dt.year
df_copy


# In[10]:


df_copy['DATE'] = pd.to_datetime(df_copy['DATE'])

df_copy['Annee'] = df_copy['DATE'].dt.year
df_copy['Mois'] =df_copy['DATE'].dt.month

df_copy


# In[11]:


df_copy.drop(columns=['ID_Station'], inplace=True)


# In[12]:


df_copy


# In[13]:


df_copy['DATE'] = pd.to_datetime(df_copy['DATE'])
df_unique = df_copy.drop_duplicates(subset='DATE', keep='first')


# In[14]:


df_unique


# In[15]:


df_unique = df_unique.sort_values(by='DATE')


# In[16]:


df_unique.columns


# In[17]:


df_unique


# In[19]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA


# In[20]:


train_size = int(len(df_unique) * 0.8)
test_size = int(len(df_unique) * 0.2)
train_data = df_unique[:train_size]
test_data = df_unique[train_size:train_size+test_size]


# In[21]:


train_data


# In[22]:


test_data


# In[23]:


train_data_sorted = train_data.sort_values(by='DATE')
test_data_sorted=test_data.sort_values(by='DATE')


# In[24]:


train_data_sorted


# In[25]:


test_data_sorted


# In[26]:


train_data_sorted['DATE'] = pd.to_datetime(train_data_sorted['DATE'])

# Indexer le DataFrame par la colonne de dates
train_data_sorted = train_data_sorted.set_index('DATE')


# In[27]:


import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


# In[28]:


model = ARIMA(train_data_sorted['Taux'], order=(0,1,2))
model_fit = model.fit()

# Affichage du résumé du modèle
print(model_fit.summary())


# In[29]:


test_data_sorted['DATE'] = pd.to_datetime(test_data_sorted['DATE'])

# Indexer le DataFrame par la colonne de dates
test_data_sorted = test_data_sorted.set_index('DATE')


# In[31]:


model = ARIMA(test_data_sorted['Taux'], order=(0,1,2))
model_fit = model.fit()

# Affichage du résumé du modèle
print(model_fit.summary())


# In[32]:


test_data_sorted['forecast(0,1,2)'] = model_fit.predict(start=test_data_sorted.index[0], end=test_data_sorted.index[-1])


# In[33]:


test_data_sorted


# In[35]:


predicted_values=test_data_sorted['forecast(0,1,2)']
real_values=test_data_sorted['Taux']


# In[36]:


correlation_coefficient = np.corrcoef(predicted_values, real_values)[0, 1]
from sklearn.metrics import mean_absolute_error
bias = np.mean(real_values - predicted_values)
mae = mean_absolute_error(real_values, predicted_values)
from sklearn.metrics import mean_squared_error
mse = mean_squared_error(real_values, predicted_values)
rmse = np.sqrt(mse)
print("Erreur quadratique moyenne (RMSE) :", rmse)
print("Erreur moyenne absolue (MAE) :", mae)
print("Biais de modèle (Mean Absolute Error) :", bias)
print("Coefficient de corrélation entre les valeurs prédites et observées :", correlation_coefficient)



import pickle
filename = 'arima_model.pckl'
# Sauvegarde du modèle
pickle.dump(model,open (filename,'wb'))
#loaded_model=pickle.load(open(filename,'rb'))

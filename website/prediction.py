import datetime
import pandas as pd
import pickle


class Predictions:
    def __init__(self, model_path="website/arima_model.pckl") -> None:
        with open(model_path, "rb") as fin:
            try:
                self.model = pickle.load(fin)
            except OSError:
                print("Wrong path or model not available")
                exit(-1)
        

   

    """def predict(self, user_data,steps=1, dynamic=False):
        
        Predicts gold prices for next date
        date_format = yyyy.mm.dd
        
        

        # Calculate next date
        

        # Preprocess date
      
        tr=self.model.fit()
        # Predict using the model
        pred = tr.predict(start=user_data.index[0], end=user_data.index[-1],dynamic=dynamic)

        return pred
"""""""""
    def predict(self, user_data, steps=1,dynamic=False):
         # Chargez le modèle avant de faire des prédictions
        # Prédire en utilisant le modèle
        tr=self.model.fit()
        # Predict using the model
        pred = tr.predict(start=user_data.index[0], end=user_data.index[-1],dynamic=dynamic)
        return pred
    def plot(self, pred):
        self.model.plot(pred)


"""if __name__ == "__main__":
    pr = Predictions()s
    new_data_path = "/Desktop/ECOPACPYTHON_PFA/dataset.csv"
    new_data = pd.read_csv(new_data_path)
    pred = pr.predict(new_data)
    if pred is not None:
        print(pred)
"""

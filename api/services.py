from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import AccessToken
from admin.models import Admin
from typing import Union, Optional, List
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
from joblib import load, dump
from os import remove
from shutil import rmtree
from os.path import exists
from uuid import uuid4 
import numpy as np
from enum import Enum
from transformers import (
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
    T5Tokenizer,
    T5ForConditionalGeneration
)
from datasets import Dataset
from .celery import language_model_train_response_task

class OAuth2CustomAuthentication(OAuth2Authentication):
    def authenticate(self, request):
        authentication = super().authenticate(request)
        if authentication is not None:
            _, access_token = authentication
            data = AccessToken.objects.select_related('application').filter(token=access_token).values('application__user_id').first()
            if data:
                user = Admin.objects.filter(pk=data.get('application__user_id')).first()
                if user:
                    authentication = user, access_token
                    return authentication
                return None
            return None
        
        return authentication
    
class RegressionTypes(Enum):
    LINEAR = 'linear'
    RANDOM = 'random'
    GRADIENT = 'gradient'
    SVR = 'svr'
    MLP = 'mlp'
    
def calculate_model_predict(**kwargs) -> Union[list, str]:
    try:
        email = kwargs.get('email')
        data = kwargs.get('data', [])

        if not email or not data:
            raise ValueError('Email or data is missing')

        if any(not item for item in data):
            raise ValueError('One of the items in \'data\' is empty')

        try:
            income_data = [list(map(float, item[:])) for item in data]
        except ValueError as e:
            raise ValueError(f'Data conversion error: {e}')
        
        user = Admin.objects.filter(email=email).only('calculate_model').first()
        calculate_model = user.calculate_model
        if not calculate_model or not exists(calculate_model):
            raise FileExistsError(f'\'{email}\' calculate model is absent')

        model = load(calculate_model)
        predictions = model.predict(income_data)

        for index, item in enumerate(data):
            item.append(round(predictions[index]))
            data[index] = item 

        return data

    except (ValueError, FileExistsError, Exception) as e:
        return str(e)

def calculate_model_fit(**kwargs) -> Optional[str]:
    try:
        email = kwargs.get('email')
        data = kwargs.get('data', [])
        model_type = kwargs.get('model_type', 'LINEAR')

        if not email or not data:
            raise ValueError('Email or data is missing')

        if any(not item for item in data):
            raise ValueError('One of the items in \'data\' is empty')

        try:
            income_data = [list(map(float, item[:-1])) for item in data]
            outcome_data = [float(item[-1]) for item in data]
        except ValueError as e:
            raise ValueError(f'Data conversion error: {e}')
        
        if not income_data or not outcome_data:
            raise ValueError('\'data\' content is incorrect')

        if model_type == 'LINEAR':
            model = LinearRegression() # для простой линейной зависимости
        elif model_type == 'RANDOM':
            model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1) # для сложной нелинейной зависимости
        elif model_type == 'GRADIENT':
            model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42) # для сложной нелинейной зависимости с ограниченнми данными
        elif model_type == 'SVR':
            model = SVR(kernel='rbf', C=1.0, epsilon=0.1) #  для небольших наборов данных с высоким уровнем шума
        elif model_type == 'MLP':
            model = MLPRegressor(hidden_layer_sizes=(100,), max_iter=500, activation='relu', solver='adam', random_state=42) # для сложных задач, где имеется сложная нелинейная зависимость между признаками и есть достаточное количество примеров
        else:
            raise ValueError('Unsupported regression type')

        X_train, X_test, y_train, y_test = train_test_split(income_data, outcome_data, test_size=0.2, random_state=42)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        filename = f'models/{uuid4()}.joblib'
        dump(model, filename)

        user = Admin.objects.filter(email=email).first()
        if not user:
            raise ValueError('User not found')

        if user.calculate_model and exists(user.calculate_model):
            remove(user.calculate_model)

        user.calculate_model = filename
        user.save()

        return (True, f'The model has been successfully trained. Model performance: mse - {mse}, r2 - {r2}')

    except (ValueError, Exception) as e:
        return (False, str(e))

def data_clustering(**kwargs) -> Union[list, str]:
    try:
        data = kwargs.get('data', [])
        n_clusters = kwargs.get('n_clusters', 2)
        if not data:
            raise ValueError('\'data\' can\'t be empty')

        features = []
        indexes = []
        for index, item in enumerate(data):
            feature = [item[key] for key in item if isinstance(item[key], (int, float))]
            if feature:
                features.append(feature)
                indexes.append(index)

        if not features:
            raise ValueError('All items in \'data\' haven\'t int or float data type for clustering')

        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        clusters = kmeans.fit_predict(features)
        centers = kmeans.cluster_centers_

        if centers.shape[1] == 1:
            sorted_indices = np.argsort(centers.flatten())[::-1]
        else:
            sorted_indices = np.argsort(np.mean(centers, axis=1))[::-1]

        new_labels = np.zeros_like(clusters)
        for new_label, old_label in enumerate(sorted_indices):
            new_labels[clusters == old_label] = new_label

        for i, cluster in enumerate(new_labels):
            data[indexes[i]]['cluster'] = int(cluster)

        return data

    except Exception as e:
        return str(e)
    
def language_model_train(email: str, data: List[dict]) -> Optional[str]:
    try:
        user = Admin.objects.filter(email=email).only('lm_model').first()
        if user.lm_model:
            lm_model_dir = user.lm_model
            if exists(lm_model_dir):
                rmtree(lm_model_dir)
            user.lm_model = None
            user.save()
        
        id = uuid4()
        model = T5ForConditionalGeneration.from_pretrained('t5-base').to('cpu')
        tokenizer = T5Tokenizer.from_pretrained('t5-base', legacy=False)

        inputs = [item['income'] for item in data]
        targets = [item['outcome'] for item in data]

        encodings = tokenizer(inputs, truncation=True, padding=True)
        target_encodings = tokenizer(targets, truncation=True, padding=True)

        train_dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': target_encodings['input_ids']
        })

        args = TrainingArguments(
            output_dir=f'models/{id}/settings',
            num_train_epochs=4,
            per_device_train_batch_size=4,
            save_steps=1000,
            save_total_limit=2,
            logging_dir=f'models/{id}/logs',
            logging_steps=100,
            evaluation_strategy='no',
            report_to='none',
            use_cpu=True
        )

        data_collator = DataCollatorForSeq2Seq(
            tokenizer=tokenizer,
            model=model
        )

        trainer = Trainer(
            model=model,
            args=args,
            data_collator=data_collator,
            train_dataset=train_dataset
        )

        trainer.train()

        base_dir = f'models/{id}'
        model.save_pretrained(f'{base_dir}/model')
        tokenizer.save_pretrained(f'{base_dir}/model')

        user.lm_model = base_dir
        user.save()

        return None
    
    except Exception as e:
        language_model_train_response_task.apply_async(
            (email, str(e), ),
            queue='low_priority'
        )

        return str(e)
    
def language_model_generate(email: str, income: str) -> tuple:
    try:
        user = Admin.objects.filter(email=email).only('lm_model').first()
        lm_model_dir = user.lm_model
        if (lm_model_dir and not exists(lm_model_dir)) or not lm_model_dir:
            raise FileExistsError('Your model doesn\'t exist. Create new model.')
        
        model = T5ForConditionalGeneration.from_pretrained(f'{lm_model_dir}/model')
        tokenizer = T5Tokenizer.from_pretrained(f'{lm_model_dir}/model')

        tokenizer_string = tokenizer(income, padding=True, truncation=True, return_tensors='pt').to(model.device)
        generated, *_ = model.generate(tokenizer_string['input_ids'])
        outcome = tokenizer.decode(generated, skip_special_tokens=True)
        return (True, outcome)

    except (FileExistsError, Exception, ) as e:
        return (False, str(e))
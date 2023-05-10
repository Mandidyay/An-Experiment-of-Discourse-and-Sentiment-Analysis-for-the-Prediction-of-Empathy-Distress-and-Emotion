# -*- coding: UTF-8 -*-

import pandas as pd
from sklearn.preprocessing import QuantileTransformer
from sklearn.preprocessing import OneHotEncoder


def process_article(file="../data/articles_adobe_AMT.csv"):
    article_raw = pd.read_csv(file)
    articles = article_raw[["article_id", "text"]]

    text_combined = []
    print('Adding [SEP] to original articles...')
    for i in articles['text']:
        text_combined.append(' [SEP] ' + i)

    articles['text'] = text_combined

    return articles


def read_train(file='../data/messages_train_ready_for_WS.tsv'):
    print('Reading training dataset...')
    train_raw = pd.read_table(file, delimiter='\t')
    df = train_raw.iloc[:, [2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]]
    return df


def read_dev(text_file='../data/messages_dev_features_ready_for_WS_2022.tsv',
             label_file='../data/goldstandard_dev_2022.tsv'):
    print('Reading dev essays...')
    raw_texts = pd.read_table(text_file, delimiter='\t')
    print('Reading dev labels...')
    raw_labels = pd.read_table(
        label_file, delimiter='\t', header=None,
        names=["empathy","distress", "emotion", "personality_conscientiousness",
                 "personality_openess", "personality_extraversion", "personality_agreeableness",
                 "personality_stability", "iri_perspective_taking", "iri_personal_distress",
                 "iri_fantasy", "iri_empathatic_concern"])

    print('Concatenate dev essays and labels...')
    df = pd.concat([raw_texts['article_id'],
                    raw_labels.iloc[:,[0,1]],
                    raw_texts['essay'],
                    raw_labels['emotion'],
                    raw_texts.iloc[:, [4, 5, 6, 7, 8]],
                    raw_labels.iloc[:,3:8]], axis=1)

    return df


def concat_change_dtype(train, dev):
    whole = pd.concat([train, dev], axis=0)
    whole['emotion'].replace(['sadness', 'neutral', 'fear', 'anger', 'disgust', 'surprise', 'joy'],
                             [0, 1, 2, 3, 4, 5, 6], inplace=True)

    return whole


def combine_articles_to_essays(articles, essays_whole_info):
    combined_texts = []
    print('Combine original article to essays...')
    for i in range(len(essays_whole_info['article_id'].values)):
        for j in articles['article_id'].values:
            if essays_whole_info['article_id'].values[i] == j:
                combined = essays_whole_info['essay'].values[i] + \
                    articles['text'][articles.index[articles['article_id']==j].tolist()[0]]
                combined_texts.append(combined)
    essays_whole_info['essay'] = combined_texts
    return essays_whole_info


def normalise_numeric(numeric_df):
    qt = QuantileTransformer(output_distribution='normal')
    return qt.fit_transform(numeric_df.values)


def encode_categorical(cate_df):
    encoder = OneHotEncoder()
    return encoder.fit_transform(cate_df.values).toarray()

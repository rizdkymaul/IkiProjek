import numpy as np
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import matplotlib.pyplot as plt
import matplotlib
import os


def prosesData(minSup, minConf, file, startDate, endDate):
    support = float(minSup)
    confidence = float(minConf)
    #Data Preparation
    df = pd.read_excel('./dataset/'+file)

    #Filter tanggal
    mask = (df['Tanggal'] >= startDate) & (df['Tanggal'] <= endDate)
    data = df.loc[mask]

    #Menghapus kolom yang tidak terpakai
    data = data.drop(['Tanggal', 'Receipt Number', 'Served By', 'Customer Phone', 'Payment Method', 'Event Type', 'Time'], axis=1)

    #Menghapus produk yang kurang dari 2 produk yang dibeli
    data['Produk'] = data['Produk'].apply(lambda x: x if isinstance(x, str) and len(x.split(',')) > 1 else None)
    data = data.dropna(subset=['Produk'])


    records = []
    for i in range(data.shape[0]):
        records.append([str(data.values[i,j]).split(',') for j in range(data.shape[1])])

    trx = [[] for trx in range(len(records))]
    for i in range(len(records)):
        for j in records[i][0]:
            trx[i].append(j)
    
    te = TransactionEncoder()
    trx_encoded = te.fit_transform(trx)
    df_encoded = pd.DataFrame(trx_encoded, columns=te.columns_)
    frequent_itemsets = apriori(df_encoded, min_support=support, use_colnames=True)
    #min_threshold sama dengan nilai minimum confidence
    rules = association_rules(frequent_itemsets, min_threshold=confidence) 

    association_results = []
    for idx, rule in rules.iterrows():
        items = ', '.join(rule['antecedents']) + " -> " + ', '.join(rule['consequents'])
        support = round(rule['support'] * 100, 2)
        confidence = round(rule['confidence'] * 100, 2)
        lift = round(rule['lift'], 2)
        association_results.append((items, support, confidence, lift))

    pd.set_option('max_colwidth', 1000)
    Result = pd.DataFrame(columns=['Rule', 'Support', 'Confidence', 'Lift'])

    for result in association_results:
        items = result[0]
        support = result[1]
        confidence = result[2]
        lift = result[3]
        Result = pd.concat([Result, pd.DataFrame({
            'Rule': [items],
            'Support': [str(support) + '%'],
            'Confidence': [str(confidence) + '%'],
            'Lift': [lift]
        })], ignore_index=True)
        Result.sort_values(by='Confidence', ascending=False, inplace=True)
        Result.reset_index(drop=True, inplace=True)
        
    Result.index += 1
                
    if Result.empty:
        return False

    return Result.to_html()


def terjual_penjualan(file, startDate, endDate):
    
    #Data Preparation
    df = pd.read_excel('./dataset/'+file)

    #Filter tanggal
    mask = (df['Tanggal'] >= startDate) & (df['Tanggal'] <= endDate)
    data = df.loc[mask]

    #Menghapus kolom yang tidak terpakai
    data = data.drop(['Tanggal', 'Receipt Number', 'Served By', 'Customer Phone', 'Payment Method', 'Event Type', 'Time'], axis=1)

    #Menghapus produk yang kurang dari 2 produk yang dibeli
    data['Produk'] = data['Produk'].apply(lambda x: x if isinstance(x, str) and len(x.split(',')) > 1 else None)
    data = data.dropna(subset=['Produk'])

    jumlah_row = data.shape[0]

    records = []
    for i in range(data.shape[0]):
        records.append([str(data.values[i,j]).split(',') for j in range(data.shape[1])])

    trx = [[] for trx in range(len(records))]
    for i in range(len(records)):
        for j in records[i][0]:
            trx[i].append(j)
    
    te = TransactionEncoder()
    trx_encoded = te.fit_transform(trx)
    df_encoded = pd.DataFrame(trx_encoded, columns=te.columns_)
    encoder_result = pd.DataFrame(df_encoded.astype(int), columns=te.columns_)

    jumlah_kolom = encoder_result.shape[1]
    jumlah_baris = encoder_result.shape[0]
    
    result = [jumlah_kolom, jumlah_baris]

    return result

def lift5(file, minSup, minConf, liftFilter):
    support = float(minSup)
    confidence = float(minConf)
    liftFilters = float(liftFilter)
    #DATA PREPARATION
    #Import dataset 
    df = pd.read_excel('./dataset/'+file)
    #Menghapus kolom yang tidak terpakai
    data = df.drop(['Tanggal', 'Receipt Number', 'Served By', 'Customer Phone', 'Payment Method', 'Event Type', 'Time'], axis=1)
    #Menghapus produk yang kurang dari 2 produk yang dibeli konsumen
    data['Produk'] = data['Produk'].apply(lambda x: x if isinstance(x, str) and len(x.split(',')) > 1 else None)
    data = data.dropna(subset=['Produk'])
    # Membuat list dalam list dari transaksi penjualan barang
    records = []
    for i in range(data.shape[0]):
        records.append([str(data.values[i,j]).split(',') for j in range(data.shape[1])])

    trx = [[] for trx in range(len(records))]
    for i in range(len(records)):
        for j in records[i][0]:
            trx[i].append(j)
    # Menggunakan fungsi apriori untuk membuat asosiasi (encoding)
    te = TransactionEncoder()
    trx_encoded = te.fit_transform(trx)
    df_encoded = pd.DataFrame(trx_encoded, columns=te.columns_)
    
    #pemodelan algoritma apriori
    #memasukan nilai minimum support
    frequent_itemsets = apriori(df_encoded, min_support=support, use_colnames=True)
    #min_threshold digunakan untuk menentukan nilai minimum confidence
    rules = association_rules(frequent_itemsets, min_threshold=confidence)
    # Membuat list hasil dari algoritma apriori
    association_results = []
    for idx, rule in rules.iterrows():
        items = ', '.join(rule['antecedents']) + " -> " + ', '.join(rule['consequents'])
        support = round(rule['support'] * 100, 2)
        confidence = round(rule['confidence'] * 100, 2)
        lift = round(rule['lift'], 2)
        association_results.append((items, support, confidence, lift))
    # 3. Menyaring hasil association_results berdasarkan nilai minimum lift
    association_results_lift_filtered = [result for result in association_results if result[3] > liftFilters]

    # Membuat DataFrame baru untuk tabel hasil lift
    pd.set_option('max_colwidth', 1000)
    Result_lift_filtered = pd.DataFrame(columns=['Rule', 'Support', 'Confidence', 'Lift'])

    for result in association_results_lift_filtered:
        items = result[0]
        support = result[1]
        confidence = result[2]
        lift = result[3]
        Result_lift_filtered = pd.concat([Result_lift_filtered, pd.DataFrame({
            'Rule': [items],
            'Support': [str(support) + '%'],
            'Confidence': [str(confidence) + '%'],
            'Lift': [lift]
        })], ignore_index=True)
    
    Result_lift_filtered.sort_values(by='Confidence', ascending=False, inplace=True)
    Result_lift_filtered.reset_index(drop=True, inplace=True)
    Result_lift_filtered.index += 1


    # Tampilkan tabel hasil dengan lift > 5
    return Result_lift_filtered.to_html()

def plotPenjualan(file):
    matplotlib.use('agg')
    #DATA PREPARATION
    #Import dataset 
    df = pd.read_excel('./dataset/'+file)
    #Menghapus kolom yang tidak terpakai
    data = df.drop(['Tanggal', 'Receipt Number', 'Served By', 'Customer Phone', 'Payment Method', 'Event Type', 'Time'], axis=1)
    #Menghapus produk yang kurang dari 2 produk yang dibeli konsumen
    data['Produk'] = data['Produk'].apply(lambda x: x if isinstance(x, str) and len(x.split(',')) > 1 else None)
    data = data.dropna(subset=['Produk'])
    # Membuat list dalam list dari transaksi penjualan barang
    records = []
    for i in range(data.shape[0]):
        records.append([str(data.values[i,j]).split(',') for j in range(data.shape[1])])

    trx = [[] for trx in range(len(records))]
    for i in range(len(records)):
        for j in records[i][0]:
            trx[i].append(j)
    # Menggunakan fungsi apriori untuk membuat asosiasi (encoding)
    te = TransactionEncoder()
    trx_encoded = te.fit_transform(trx)
    df_encoded = pd.DataFrame(trx_encoded, columns=te.columns_)
    produk_counts = df_encoded.sum().sort_values(ascending=False)

    # Menampilkan top 10 produk terlaris
    top_10_produk_terlaris = produk_counts.head(10)
    list_data = top_10_produk_terlaris.reset_index().values.tolist()

    return list_data

def checkStartDate(file, startDate):
    #Data Preparation
    df = pd.read_excel('./dataset/'+file)
    mask = (df['Tanggal'] >= startDate)
    data = df.loc[mask]
    if data.empty:
        return 'lebih'
    
    mask = (df['Tanggal'] <= startDate)
    data = df.loc[mask]
    if data.empty:
        return 'kurang'

    return True

def checkEndDate(file, endDate):
    #Data Preparation
    df = pd.read_excel('./dataset/'+file)

    mask = (df['Tanggal'] <= endDate)
    data = df.loc[mask]
    if data.empty:
        return 'kurang'

    mask = (df['Tanggal'] >= endDate)
    data = df.loc[mask]
    if data.empty:
        return 'lebih'
    return True


# -*- coding: utf-8 -*-
"""Ave_price .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DAdbOgE_ML9aX8u_0bBzngd5YCGsCEar
"""
import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def calculate_avg_price_yps_wood(model_data, months):
    total_value = model_data['VALUE'].sum()
    total_units = model_data['UNITS'].sum()
    avg_price = (total_value / total_units) * 1000 if total_units else 0  # 平均単価を1000倍して計算
    return avg_price

def download_excel_yps_wood(data):
    output_file_path = "Wood平均単価.xlsx"
    data.to_excel(output_file_path, index=False)  # Excelファイルに保存
    with open(output_file_path, "rb") as file:
        excel_data = file.read()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{output_file_path}">ダウンロード結果</a>'
    return href

def calculate_avg_price_yps_iron(model_data, months):
    total_value = model_data['VALUE'].sum()
    total_units = model_data['UNITS'].sum()
    avg_price = total_value / total_units * 1000
    return avg_price

def download_excel_yps_iron(data):
    output_file_path = "Iron平均単価.xlsx"
    data.to_excel(output_file_path, index=False)
    with open(output_file_path, "rb") as file:
        excel_data = file.read()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{output_file_path}">ダウンロード結果</a>'
    return href

def calculate_avg_price_gfk(model_data, months):
    start_index = 0
    end_index = min(months, len(model_data))  # 最初のnつのみ選択
    model_data_filtered = model_data.iloc[start_index:end_index]
    total_value = model_data_filtered['Sales Value KRW'].sum()
    total_units = model_data_filtered['Sales Units'].sum()
    avg_price = total_value / total_units if total_units else 0
    return avg_price

def download_excel_gfk(data, months):
    file_name = f"Gfk平均単価_{months}ヵ月.xlsx"
    output_file_path = f"/tmp/{file_name}"
    data.to_excel(output_file_path, index=False)
    with open(output_file_path, "rb") as file:
        excel_data = file.read()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">クリックしてダウンロード</a>'
    return href

def calculate_avg_price_gdt(group, months):
    end_date = group['Y+M'].min() + pd.DateOffset(months=months)
    group = group[group['Y+M'] <= end_date]
    total_sales = group['Unit Sales'].sum()
    total_value = group['Value'].sum()
    average_price = total_value / total_sales
    return pd.Series({'Unit Sales': total_sales, 'Value': total_value, 'Average Price': average_price})

def download_excel_gdt(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Off', index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="USAaverage_price.xlsx">クリックしてダウンロード</a>'
    return href

def main():
    st.title('平均RU単価計算')

    option = st.sidebar.selectbox(
        'データセットを選択してください',
        ('YPS_Wood', 'YPS_Iron', 'Gfk', 'GDT')
    )

    if option == 'YPS_Wood':
        st.subheader('YPS Wood 平均単価計算')
        st.write('**1. Excelファイルをアップロードしてください。**')
        uploaded_file = st.file_uploader("Excelファイルを選択してください", type=['xlsx'])

        if uploaded_file is not None:
            # '2012-' シートを読み込む
            df = pd.read_excel(uploaded_file, sheet_name='2012-')
            months = st.slider("計算する期間を選択してください（月数）", 1, 24, 5)

            if st.button('平均単価を計算'):
                df_sorted = df.sort_values(by=['DATE', 'MODEL'])
                df_filtered = df_sorted.groupby('MODEL').apply(lambda x: x.head(months)).reset_index(drop=True)
                df_summed = df_filtered.groupby('MODEL').apply(calculate_avg_price_yps_wood, months=months).reset_index(name='Ave_Price')
                df_filtered['9'] = df_filtered['9'].astype(str).replace({'1': 'CUSTOM', '2': 'NORMAL', '3': 'OTHERS'})
                df_output = df_filtered[['DATE', 'BRAND', 'SUB BRAND', 'MODEL', '性別', 'シャフト', 'ﾀｲﾌﾟ', '9']].drop_duplicates('MODEL')
                df_output = pd.merge(df_output, df_summed, on='MODEL', how='left')
                st.markdown(download_excel_yps_wood(df_output), unsafe_allow_html=True)

    elif option == 'YPS_Iron':
        st.subheader('YPS Iron 平均単価計算')
        st.write('**1. Excelファイルをアップロードしてください。**')
        uploaded_file = st.file_uploader("Excelファイルを選択してください", type=['xlsx'])

        if uploaded_file is not None:
            # '2019-' シートを読み込む
            df = pd.read_excel(uploaded_file, sheet_name='2019-')
            months = st.slider("計算する期間を選択してください（月数）", 1, 24, 5)

            if st.button('平均単価を計算'):
                df_sorted = df.sort_values(by=['DATE', 'MODEL'])
                df_filtered = df_sorted.groupby('MODEL').apply(lambda x: x.head(months)).reset_index(drop=True)
                df_summed = df_filtered.groupby('MODEL').agg({'UNITS': 'sum', 'VALUE': 'sum'}).reset_index()
                df_summed['Ave_Price'] = df_summed['VALUE'] / df_summed['UNITS'] * 1000
                df_filtered[['2', '4', '7']] = df_filtered[['2', '4', '7']].astype(str)
                df_output = df_filtered[['DATE', 'BRAND', 'SUB BRAND', 'MODEL', '2', '4', '7']].drop_duplicates('MODEL')
                df_output = pd.merge(df_output, df_summed[['MODEL', 'Ave_Price']], on='MODEL', how='left')
                output_file_path = "Iron平均単価.xlsx"
                df_output.to_excel(output_file_path, index=False)
                st.write('**計算結果のダウンロード**')
                st.markdown(download_excel_yps_iron(df_output), unsafe_allow_html=True)

    elif option == 'Gfk':
        st.subheader('Gfk 平均単価計算')
        st.write('**1. Excelファイルをアップロードしてください。**')
        uploaded_file = st.file_uploader("Excelファイルを選択してください", type=['xlsx'])

        if uploaded_file is not None:
            # 8regions_database シートを読み込む
            data = pd.read_excel(uploaded_file, sheet_name='8regions_database')
            months = st.slider("計算する期間を選択してください（月数）", 1, 24, 5)

            if st.button('平均単価を計算'):
                result = data.groupby(['TYPE', 'BRAND', 'MODEL', 'USER TYPE', 'SHAFT MATERIAL', 'SHAFT FLEX']).apply(
                    calculate_avg_price_gfk, months=months).reset_index(name='Ave_price')  
                st.markdown(download_excel_gfk(result, months), unsafe_allow_html=True)

    elif option == 'GDT':
        st.subheader('GDT 平均単価計算')
        st.write('**1. Excelファイルをアップロードしてください。**')
        uploaded_file = st.file_uploader("Excelファイルを選択してください", type=['xlsx'])

        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            df_selected = df[['Year', 'Month', 'On/Off', 'Product Type', 'Brand', 'Model', 'Unit Sales', 'Value']]
            df_selected['Y+M'] = df_selected['Year'].astype(str) + '-' + df_selected['Month'].astype(str).str.zfill(2)
            df_selected['Y+M'] = pd.to_datetime(df_selected['Y+M'], format='%Y-%m')
            months = st.slider("計算する期間を選択してください（月数）", 1, 24, 5)

            if st.button('集計する'):
                df_off = df_selected[df_selected['On/Off'] == 'off']
                df_on = df_selected[df_selected['On/Off'] == 'on']
                df_off_summed = df_off.groupby(['Model', 'On/Off', 'Product Type', 'Brand']).apply(
                    calculate_avg_price_gdt, months=months).reset_index()
                df_on_summed = df_on.groupby(['Model', 'On/Off', 'Product Type', 'Brand']).apply(
                    calculate_avg_price_gdt, months=months).reset_index()
                df_off_summed = df_off_summed[['On/Off', 'Product Type', 'Brand', 'Model', 'Unit Sales', 'Value', 'Average Price']]
                df_on_summed = df_on_summed[['On/Off', 'Product Type', 'Brand', 'Model', 'Unit Sales', 'Value', 'Average Price']]
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_off_summed.to_excel(writer, sheet_name='Off', index=False)
                    df_on_summed.to_excel(writer, sheet_name='On', index=False)
                b64 = base64.b64encode(output.getvalue()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="USAaverage_price.xlsx">クリックしてダウンロード</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

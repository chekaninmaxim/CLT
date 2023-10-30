import time

import pandas as pd
import numpy as np
import matplotlib
from pyhive import hive
import streamlit as st


def visualize(hive_table_name, conn):
    db_name = hive_table_name.split(".")[0]
    main_container = st.container()
    with main_container:
        st.markdown(
            "Таблиця test1.batch_mean_and_size містить середні значення мікробатчів, які обробляв спарк."
            "Мікробатчі були сформовані з повідомлень з кафки, що були просто рандомними числами. "
            "Отже середнє по батчу - це теж випадкова величина."
            "І згідно центральної граничної теореми - ця випадкова величина повинна мати нормальний розподіл")
        st.markdown("Дочекайтеся поки кафка продюсер надішле більше данних в чергу."
                    "Чим більше данних буде надіслано та оброблено. Тим більше цей розподіл буде схожий на Гаусовий")
        st.subheader("Що саме відбувається?")
        st.markdown("Генератор рандомних чисел кожну секунду генерує нове число від 0 до 10000 та відправляє"
                    "його в чергу в кафку. Кожні 5 секунд спарк джоба дістає останні повідомлення з"
                    "Кафки рахує середнє значення в новому мікробатчі та кладе данні в хайв таблицю."
                    "І вже цей веб додаток дістає данні з хайв таблиці та будує цю гістограму кожні 5 секунд")
        histogram = st.text("Дочекайтесь поки підніметься хайв. Створіть базу данних {}".format(db_name))
        for i in range(10000):
            try:
                data = load_data(hive_table_name, conn)
                histogram.bar_chart(data, x="batch_mean", y="count")
                time.sleep(5)
            except Exception:
                histogram.markdown(
                    """Дочекайтесь поки підніметься хайв."
                    "Створіть базу данних test1. Почекайте поки там з'являться данні {}"""
                    .format('.' * (i % 5)))
                time.sleep(1)


def load_data(table_name: str, conn):
    df = pd.read_sql("Select * from {}".format(table_name), conn)
    columns_dict = {
        "batch_mean_and_size.batch_mean": "batch_mean",
        "batch_mean_and_size.batch_size": "batch_size",
        "batch_mean_and_size.batch_id": "batch_id",
        "batch_mean_and_size.processing_timestamp": "timestamp"
    }
    df = df.rename(columns=columns_dict)
    df = df.dropna()
    hist_values = np.histogram(df["batch_mean"], bins=100, range=(0, 10000))
    hist_df = pd.DataFrame(np.vstack((hist_values[0], hist_values[1][1:])).T, columns=["count", "batch_mean"])
    return hist_df


def main():
    # Local run variant.
    # HIVE_HOST = "localhost"
    # HIVE_PORT = "10000"
    # In Docker run:
    HIVE_HOST = "hive-server"
    HIVE_PORT = "10000"

    HIVE_USERNAME = "hive"

    conn = None
    connection_error_message = "Не вдалось з'єднатись з базою данних. Дочекайтесь, поки підніметься hive server"
    text = st.text(connection_error_message)
    while not conn:
        try:
            conn = hive.Connection(host=HIVE_HOST, port=HIVE_PORT, username=HIVE_USERNAME)
            text.title('Візуальна перевірка центральної граничної теореми')
        except Exception:
            text.text(connection_error_message)

        time.sleep(5)

    hive_table_name = "test1.batch_mean_and_size"
    visualize(hive_table_name, conn)


if __name__ == '__main__':
    main()


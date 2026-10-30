from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from sqlmodel import Session, select
from app.database.db import engine, init_db
from app.database.models import Category, Car, Client, Rental

st.set_page_config(page_title='AutoRent — лабораторные 1 и 2', layout='wide')
st.title('AutoRent')
st.caption('АРМ компании по аренде автомобилей · Лабораторные работы 1 и 2')
init_db()
with Session(engine) as session:
    models = [Category, Car, Client, Rental]
    names = ['Категории', 'Автомобили', 'Клиенты', 'Аренды']
    records = [session.exec(select(model)).all() for model in models]
    for col, name, rows in zip(st.columns(4), names, records):
        col.metric(name, len(rows))
    tabs = st.tabs(names + ['Связи таблиц', 'ER-диаграмма'])
    for tab, rows in zip(tabs, records):
        with tab:
            st.dataframe([row.model_dump() for row in rows], width='stretch')
    with tabs[4]:
        st.write('Эти значения получены через ORM-связи Rental → Car → Category и Rental → Client.')
        st.dataframe([{'Договор':r.id, 'Клиент':r.client.full_name,
            'Автомобиль':f'{r.car.brand} {r.car.model}', 'Категория':r.car.category.name,
            'Начало':r.start_date, 'Возврат':r.end_date, 'Тариф ₸':r.daily_rate,
            'Сумма ₸':r.total} for r in records[3]], width='stretch')
    with tabs[5]:
        st.image(str(Path(__file__).resolve().parents[1] / 'docs/er-diagram.png'))
st.info('Демонстрационная база. Для заполнения: python seed.py. Для проверки: python verify.py.')

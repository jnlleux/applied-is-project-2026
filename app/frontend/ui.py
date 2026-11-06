import os
from datetime import date, timedelta
import requests
import streamlit as st

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="AutoRent", page_icon="🚗", layout="wide")
st.title("🚗 AutoRent — аренда автомобилей")
st.sidebar.caption("Лабораторные работы 3–7 • FastAPI + Streamlit")

def api(method, path, **kwargs):
    try:
        response = requests.request(method, BASE_URL + path, timeout=10, **kwargs)
        if not response.ok:
            st.error(f"Ошибка {response.status_code}: {response.json().get('detail', response.text)}")
            return None
        return response.json() if response.content else True
    except (requests.RequestException, ValueError):
        st.error("Сервер недоступен. Проверьте запуск FastAPI и повторите действие.")
        return None

if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))
section = st.sidebar.radio("Раздел", ["Автомобили", "Категории", "Клиенты", "Аренда"])
paths = {"Автомобили":"cars", "Категории":"categories", "Клиенты":"clients", "Аренда":"rentals"}
path = "/" + paths[section]
search = st.text_input("Поиск") if section != "Аренда" else ""
params = {"search": search}
if section != "Клиенты":
    a,b = st.columns(2)
    params["min_price"] = a.number_input("Тариф от, ₸", min_value=0, step=1000)
    if b.checkbox("Ограничить максимальный тариф"):
        params["max_price"] = b.number_input("Тариф до, ₸", min_value=0, value=100000)
rows = api("GET", path, params=params)
if rows is None: st.stop()
if section == "Аренда":
    for row in rows:
        row["total"] = (date.fromisoformat(row["end_date"]) - date.fromisoformat(row["start_date"])).days * row["daily_rate"]
st.dataframe(rows, width="stretch")
mode = st.radio("Действие", ["Добавить", "Изменить", "Удалить"], horizontal=True)
selected = {}
if mode != "Добавить":
    if not rows:
        st.info("Нет записей для выбранного действия"); st.stop()
    selected = st.selectbox("Запись", rows, format_func=lambda x: str(x))
with st.form("edit"):
    payload = {}
    if mode != "Удалить":
        fields = {"cars":["brand", "model", "plate", "category_id"], "categories":["name", "daily_rate"],
                  "clients":["full_name", "license_number"], "rentals":["car_id", "client_id", "start_date", "end_date", "daily_rate"]}
        labels = {"brand":"Марка", "model":"Модель", "plate":"Госномер", "name":"Название", "daily_rate":"Тариф в сутки, ₸", "full_name":"ФИО", "license_number":"Водительское удостоверение", "category_id":"Категория", "car_id":"Автомобиль", "client_id":"Клиент", "start_date":"Начало", "end_date":"Окончание"}
        for field in fields[paths[section]]:
            if field.endswith("_id"):
                target = {"category_id":"categories", "car_id":"cars", "client_id":"clients"}[field]
                options = api("GET", "/"+target) or []
                ids = [x["id"] for x in options]
                value = st.selectbox(labels[field], ids, index=ids.index(selected[field]) if selected.get(field) in ids else 0,
                    format_func=lambda x: str(next(r for r in options if r["id"]==x)))
                payload[field] = value
            elif field.endswith("date"):
                default = date.fromisoformat(selected[field]) if selected else date.today()+timedelta(days=int(field=="end_date"))
                payload[field] = st.date_input(labels[field], default).isoformat()
            elif field == "daily_rate":
                payload[field] = st.number_input(labels[field], min_value=1, value=selected.get(field,15000))
            else:
                payload[field] = st.text_input(labels[field], selected.get(field,""))
    confirmed = st.checkbox("Подтверждаю удаление") if mode == "Удалить" else True
    if st.form_submit_button("Выполнить") and confirmed:
        method = {"Добавить":"POST", "Изменить":"PATCH", "Удалить":"DELETE"}[mode]
        result = api(method, path + ("/"+str(selected["id"]) if selected else ""), **({"json":payload} if method != "DELETE" else {}))
        if result is not None:
            st.session_state["notice"] = "Изменения сохранены"; st.rerun()

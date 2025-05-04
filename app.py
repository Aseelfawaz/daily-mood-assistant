import streamlit as st
from transformers import pipeline
import requests
import pandas as pd
from datetime import datetime
import os
import altair as alt

# إعداد صفحة Streamlit
st.set_page_config(page_title="Daily Mood Assistant")
st.title("🌤️ Daily Mood Assistant")
st.markdown("اكتب شعورك وسنقترح لك أنشطة، ونعرض لك آية قرآنية تلامس حالتك 💖")

# نموذج تحليل المشاعر
classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# الآيات حسب الشعور
ayah_api_ids = {
    "سلبي": "12:18",
    "محايد": "13:28",
    "إيجابي": "14:34"
}

# الأنشطة المقترحة حسب الشعور
activities = {
    "سلبي": ["🧘‍♀️ خذ وقت لنفسك وجرب تمارين التنفس", "☕ اجلس في مكان هادئ مع فنجان قهوة", "📓 عبّر عن مشاعرك في دفتر"],
    "محايد": ["📚 اقرأ كتاب", "🚶‍♀️ نزهة خفيفة", "🧹 نظف غرفتك"],
    "إيجابي": ["💬 شارك طاقتك", "💪 مارس رياضة", "🧠 تعلم شيء جديد"]
}

# دالة لجلب الآية
def get_ayah(ayah_id):
    url = f"http://api.alquran.cloud/v1/ayah/{ayah_id}/ar"
    response = requests.get(url)
    return response.json()["data"]["text"] if response.status_code == 200 else "📖 (تعذر جلب الآية)"

# دالة لتخزين الشعور
def save_mood(mood):
    df = pd.DataFrame([{"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "mood": mood}])
    df.to_csv("mood_log.csv", mode='a', header=not os.path.exists("mood_log.csv"), index=False)

# إدخال المستخدم
user_input = st.text_input("🧠 اكتب شعورك بكلمة أو جملة:")

# التبويبات
tab1, tab2 = st.tabs(["🧠 التحليل والأنشطة", "📊 سجل حالتي النفسية"])

# التبويب الأول
with tab1:
    if user_input:
        with st.spinner("🔍 جاري تحليل مشاعرك..."):
            result = classifier(user_input)
            label = result[0]['label']
            score = result[0]['score']

            if "1" in label or "2" in label:
                mood = "سلبي"
            elif "3" in label:
                mood = "محايد"
            else:
                mood = "إيجابي"

            st.success(f"💡 التحليل: {label} | الثقة: {score:.2f}")
            st.write(f"🌈 شعورك تم تصنيفه على أنه: **{mood}**")
            save_mood(mood)

            # عرض الآية
            ayah_text = get_ayah(ayah_api_ids[mood])
            st.markdown(f"📖 قال تعالى:\n> **{ayah_text}**")

            # الأنشطة
            st.subheader("🎯 اقتراحات لأنشطتك اليوم:")
            for activity in activities[mood]:
                st.write(f"✅ {activity}")

# التبويب الثاني: مخطط زمني
with tab2:
    with st.expander("📈 المخطط الزمني لتغير حالتك النفسية"):
        try:
            df = pd.read_csv("mood_log.csv")
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["mood"] = df["mood"].str.strip()

            chart = alt.Chart(df).mark_circle(size=100).encode(
                x='timestamp:T',
                y=alt.value(0),
                color='mood:N',
                tooltip=['timestamp:T', 'mood:N']
            ).properties(
                title="⏱️ تسلسل مشاعرك بمرور الوقت",
                width=700,
                height=150
            )

            st.altair_chart(chart, use_container_width=True)

        except FileNotFoundError:
            st.info("لا توجد بيانات محفوظة حتى الآن.")

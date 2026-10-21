import json
import os
import streamlit as st

st.set_page_config(
    page_title="نظام إدارة مصاريف البيت العائلي", page_icon="🏡", layout="centered"
)

USERS_FILE = "users_db.json"


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def get_user_data_file(username):
    return f"expense_data_{username}.json"


def load_data(username):
    data_file = get_user_data_file(username)
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "income": 0.0,
        "budget_limit": 0.0,
        "fixed_expenses": [],
        "expenses": [],
    }


def save_data(username, data):
    data_file = get_user_data_file(username)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


users_db = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🏡 نظام مصاريف العائلة الذكي")
    st.write("أهلاً بكِ! الرجاء تسجيل الدخول أو إنشاء حساب جديد:")

    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])

    with tab1:
        st.subheader("تسجيل الدخول للحساب")
        login_user = st.text_input(
            "اسم المستخدم", key="login_user"
        ).strip()
        login_pass = st.text_input(
            "كلمة المرور", type="password", key="login_pass"
        )

        if st.button("دخول"):
            if (
                login_user in users_db
                and users_db[login_user] == login_pass
            ):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

    with tab2:
        st.subheader("إنشاء حساب جديد لأفراد العائلة")
        new_user = st.text_input(
            "اختر اسم مستخدم (بالإنجليزي أو بالعربي)", key="new_user"
        ).strip()
        new_pass = st.text_input(
            "اختر كلمة مرور", type="password", key="new_pass"
        )

        if st.button("إنشاء الحساب"):
            if not new_user or not new_pass:
                st.warning("الرجاء إدخال اسم المستخدم وكلمة المرور.")
            elif new_user in users_db:
                st.error(
                    "اسم المستخدم هذا موجود مسبقاً، جرب اسمًا آخر أو سجل دخولك."
                )
            else:
                users_db[new_user] = new_pass
                save_users(users_db)
                st.success(
                    "تم إنشاء الحساب بنجاح! يمكنك الانتقال لتبويب تسجيل الدخول والدخول الآن."
                )

    st.stop()

current_user = st.session_state.username
st.sidebar.write(f"👤 المستخدم الحالي: **{current_user}**")
if st.sidebar.button("تسجيل خروج"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

data = load_data(current_user)

st.title(f"🏡 نظام إدارة مصاريف البيت (حساب: {current_user})")

st.subheader("⚙️ إعدادات بداية الشهر")
income = st.number_input(
    "راتب أو معاش الشفة لهذا الشهر (₪):",
    value=float(data["income"]),
    step=100.0,
)
budget_limit = st.number_input(
    "الحد الأقصى المسموح صرفه (ميزانية الشهر المستهدفة) (₪):",
    value=float(data["budget_limit"]),
    step=100.0,
)

if st.button("حفظ الإعدادات"):
    data["income"] = income
    data["budget_limit"] = budget_limit
    save_data(current_user, data)
    st.success("تم حفظ البيانات بنجاح!")

st.subheader("➕ إضافة مصروف جديد")
with st.form("expense_form"):
    desc = st.text_input("وصف المصروف (مثلاً: سوبرماركت، بنزين)")
    amount = st.number_input("المبلغ (₪):", min_value=0.0, step=10.0)
    category = st.selectbox(
        "التصنيف:", ["أكل وغذاء", "فواتير ومواصلات", "تسوّق", "أخرى"]
    )
    submitted = st.form_submit_button("إضافة المصروف")

    if submitted and desc:
        data["expenses"].append(
            {"desc": desc, "amount": amount, "category": category}
        )
        save_data(current_user, data)
        st.success(f"تم إضافة المصروف ({desc}) بنجاح!")

st.subheader("📊 ملخص الحساب")
total_spent = sum(item["amount"] for item in data["expenses"])
remaining = data["income"] - total_spent

col1, col2, col3 = st.columns(3)
col1.metric("إجمالي الدخل", f"{data['income']} ₪")
col2.metric("إجمالي المصاريف", f"{total_spent} ₪")
col3.metric("المتبقي", f"{remaining} ₪")

if data["budget_limit"] > 0 and total_spent > data["budget_limit"]:
    st.warning(
        "⚠️ تنبيه: لقد تجاوزت الحد الأقصى المسموح صرفه لهذا الشهر (الميزانية المستهدفة)!"
    )

if data["expenses"]:
    st.subheader("📋 قائمة المصاريف المسجلة")
    st.dataframe(data["expenses"])

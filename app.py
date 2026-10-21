import json
import os
import streamlit as st

DATA_FILE = "expense_data_v2.json"


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {
      "income": 0.0,
      "budget_limit": 0.0,  # الحد الأقصى المسموح صرفه
      "fixed_expenses": [],  # المصاريف الثابتة المتكررة (مثل الإيجار)
      "expenses": [],  # المصاريف اليومية أو المتغيرة
  }


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


st.set_page_config(
    page_title="مدير مصاريف البيت ", page_icon="💡", layout="wide"
)

data = load_data()

st.title(" نظام إدارة مصاريف البيت ")
st.markdown("---")

# إذا لم يتم إعداد الراتب والميزانية بعد
if data["income"] == 0:
  st.subheader("⚙️ إعدادات بداية الشهر")
  with st.form("setup_form"):
    income_input = st.number_input("راتب أو معاش الشقة لهذا الشهر (₪):", min_value=0.0, step=100.0)
    limit_input = st.number_input("الحد الأقصى المسموح صرفه (ميزانية الشهر المستهدفة) (₪):", min_value=0.0, step=100.0)
    
    submit_setup = st.form_submit_button("حفظ وحفظ البدء")
    if submit_setup:
      if income_input > 0:
        data["income"] = income_input
        data["budget_limit"] = limit_input if limit_input > 0 else income_input
        save_data(data)
        st.success("تم الحفظ بنجاح! يرجى تحديث الصفحة.")
        st.rerun()
      else:
        st.warning("الرجاء إدخال راتب صحيح.")
else:
  # الشريط الجانبي للتنقل
  st.sidebar.header("🎛️ القائمة الرئيسية")
  menu = st.sidebar.selectbox(
      "اختر الصفحة",
      [
          "📊 لوحة التحكم والملخص",
          "⚡ المصاريف الثابتة (التلقائية)",
          "💸 إضافة مصروف جديد",
          "⚙️ إعدادات الشهر الجديد",
      ],
  )

  # حساب إجمالي المصاريف الثابتة والمتغيرة
  total_fixed = sum(item["amount"] for item in data["fixed_expenses"])
  total_variable = sum(item["amount"] for item in data["expenses"])
  total_exp = total_fixed + total_variable
  remaining = data["income"] - total_exp

  # 1. لوحة التحكم والملخص
  if menu == "📊 لوحة التحكم والملخص":
    st.subheader("📈 نظرة عامة على وضعك المالي")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("الراتب الأساسي", f"{data['income']} ₪")
    col2.metric("المصاريف الثابتة", f"{total_fixed} ₪")
    col3.metric("المصاريف المتغيرة", f"{total_variable} ₪")
    col4.metric("المتبقي الفعلي", f"{remaining} ₪")

    # نظام التنبيهات المبكرة والاستباقية
    budget_limit = data.get("budget_limit", data["income"])
    spending_ratio = total_exp / budget_limit if budget_limit > 0 else 0

    st.markdown("### 🚨 حالة الميزانية والتنبيهات:")
    if total_exp > budget_limit:
      st.error(
          f"⚠️ **تنبيه خطر جداً!** لقد تجاوزت الحد الأقصى لميزانيتك المحددة ({budget_limit} ₪)!"
      )
    elif spending_ratio >= 0.8:
      st.warning(
          f"⚠️ **تنبيه استباقي:** لقد صرفت {int(spending_ratio * 100)}% من ميزانيتك! اقتربت من الحد المسموح، خفف مصاريفك للأيام القادمة."
      )
    else:
      st.success(" الوضع ممتاز! ميزانيتك تحت السيطرة والأمور سليمّة.")

    # حساب المعدل الأسبوعي واليومي المقترح
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
      st.info(f"📅 **المعدل الأسبوعي للمصاريف الحالية:** {total_exp / 4:.2f} ₪ بالأسبوع تقريباً.")
    with col_b:
      st.info(f"💡 **المتبقي المسموح صرفه لكل أسبوع (باقي الشهر):** {max(0, (budget_limit - total_exp) / 4):.2f} ₪.")

    # الرسم البياني المتقدم
    st.markdown("---")
    st.subheader("📊 توزيع المصاريف بالرسم البياني")
    chart_data = {"التصنيف": ["ثابتة (إيجار/فواتير)", "متغيرة (سوبرماركت وغيرها)", "المتبقي"], "المبلغ": [total_fixed, total_variable, max(0, remaining)]}
    st.bar_chart(chart_data, x="التصنيف", y="المبلغ")

  # 2. المصاريف الثابتة (التلقائية)
  elif menu == "⚡ المصاريف الثابتة (التلقائية)":
    st.subheader("🏠 المصاريف الثابتة (التي لا داعي لكتابتها كل شهر)")
    st.write("هنا تضع الأشياء الثابتة مثل الإيجار الشهري، اشتراك الإنترنت، أو الكهرباء التقريبية لكي تُحسب تلقائياً.")

    with st.form("fixed_form"):
      f_name = st.text_input("اسم المصروف الثابت (مثال: إيجار الشقة، إنترنت)")
      f_amount = st.number_input("المبلغ الشهري الثابت (₪)", min_value=0.0, step=50.0)
      submit_f = st.form_submit_button("إضافة للمصاريف الثابتة")

      if submit_f:
        if f_name and f_amount > 0:
          data["fixed_expenses"].append({"name": f_name, "amount": f_amount})
          save_data(data)
          st.success(f"تمت إضافة '{f_name}' للمصاريف الثابتة بنجاح!")
          st.rerun()
        else:
          st.warning("الرجاء إدخال البيانات بشكل صحيح.")

    st.markdown("### قائمة المصاريف الثابتة الحالية:")
    if not data["fixed_expenses"]:
      st.info("لا توجد مصاريف ثابتة مسجلة بعد.")
    else:
      for idx, item in enumerate(data["fixed_expenses"]):
        col1, col2 = st.columns([4, 1])
        col1.write(f"🔹 **{item['name']}**: {item['amount']} ₪ (تُحسب تلقائياً كل شهر)")
        if col2.button("حذف", key=f"del_fixed_{idx}"):
          data["fixed_expenses"].pop(idx)
          save_data(data)
          st.rerun()

  # 3. إضافة مصروف جديد
  elif menu == "💸 إضافة مصروف جديد":
    st.subheader("🛒 تسجيل مصروف متفرغ جديد (سوبرماركت، مطعم، طوارئ...)")
    with st.form("expense_form"):
      name = st.text_input("اسم المصروف (مثال: سوبرماركت أسبوعي)")
      amount = st.number_input("المبلغ المدفوع (₪)", min_value=0.0, step=10.0)
      submit = st.form_submit_button("إتمام الخصم وإضافة المصروف")

      if submit:
        if name and amount > 0:
          data["expenses"].append({"name": name, "amount": amount})
          save_data(data)
          st.success(f"تمت إضافة مصروف '{name}' بقيمة {amount} ₪ بنجاح وخصمه من الراتب!")
        else:
          st.error("الرجاء إدخال اسم المصروف والمبلغ بشكل صحيح.")

    st.markdown("### سجل المصاريف المتغيرة لهذا الشهر:")
    if not data["expenses"]:
      st.info("لا توجد مصاريف متغيرة مسجلة حتى الآن.")
    else:
      for idx, item in enumerate(data["expenses"]):
        col1, col2 = st.columns([4, 1])
        col1.write(f"🔹 **{item['name']}**: {item['amount']} ₪")
        if col2.button("حذف", key=f"del_exp_{idx}"):
          data["expenses"].pop(idx)
          save_data(data)
          st.rerun()

  # 4. إعدادات الشهر الجديد
  elif menu == "⚙️ إعدادات الشهر الجديد":
    st.warning("⚠️ إعادة تصفير الحساب ستقوم بمسح المصاريف المتغيرة والبدء لشهر جديد.")
    if st.button("تصفير الحساب وبداية شهر جديد"):
      data["income"] = 0.0
      data["budget_limit"] = 0.0
      data["expenses"] = []
      # نترك المصاريف الثابتة لأن الإيجار غالباً يبقى نفسه لكي نريح المستخدم!
      save_data(data)
      st.success("تم تصفير المصاريف الشهرية بنجاح! يرجى إعادة إدخال الراتب للشهر الجديد.")
      st.rerun()
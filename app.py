import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

LEAKCHECK_API_KEY = os.getenv("LEAKCHECK_API_KEY")

ARABIC_MESSAGE = """
<div class="arabic-message">
    <h1>⚠️ تم العثور على بريدك الإلكتروني في تسريبات بيانات!</h1>
    <p>إليك 3 خطوات لتحسين أمانك الإلكتروني:</p>
    <ol>
        <li>
            <strong>الخطوة 1:</strong> استخدم مدير كلمات المرور مثل 
            <a href="https://bitwarden.com" target="_blank">Bitwarden</a>
            لإنشاء كلمات مرور قوية وتخزينها لكل موقع.
        </li>
        <li>
            <strong>الخطوة 2:</strong> فعّل التحقق بخطوتين (2FA) لحساباتك، واحتفظ بالرموز داخل Bitwarden أو تطبيق مصادقة.
            <br>🎥 
            <a href="https://www.youtube.com/watch?v=FDGBXUl3uac" target="_blank">
                اضغط هنا لتعلّم كيفية تفعيل التحقق بخطوتين
            </a>
        </li>
        <li>
            <strong>الخطوة 3:</strong> اشترك في تنبيهات اختراقات البيانات لتبقى على اطلاع، وغيّر كلمات المرور المسربة فوراً.
        </li>
    </ol>
    <p>ابقَ آمناً وكن يقظاً! 🔐</p>
</div>
"""




def format_breaches(breaches):
    formatted = []
    for b in breaches:
        name = b.get("name", "غير معروف")
        date = b.get("date", "")
        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m")
                formatted_date = dt.strftime("%B %Y").replace("May", "مايو").replace("January", "يناير").replace("February", "فبراير").replace("March", "مارس").replace("April", "أبريل").replace("June", "يونيو").replace("July", "يوليو").replace("August", "أغسطس").replace("September", "سبتمبر").replace("October", "أكتوبر").replace("November", "نوفمبر").replace("December", "ديسمبر")
                formatted.append(f"📁 <strong>{name}</strong> — تم التسريب في: {formatted_date}")
            except:
                formatted.append(f"📁 <strong>{name}</strong> — تم التسريب في: {date}")
        else:
            formatted.append(f"🔎 <strong>{name}</strong> — مصدر غير معروف (تاريخ غير متوفر)")
    return formatted

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        email = request.form["email"]
        url = "https://leakcheck.io/api/public"
        params = {
            "key": LEAKCHECK_API_KEY,
            "check": email
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    breaches = data.get("sources", [])
                    formatted = format_breaches(breaches)
                    result = {"email": email, "formatted_breaches": formatted, "arabic_msg": ARABIC_MESSAGE}
                else:
                    result = {"email": email, "formatted_breaches": []}
            else:
                error = f"خطأ في التحقق (رمز {response.status_code})"
        except Exception as e:
            error = f"خطأ أثناء الاتصال بالخدمة: {e}"
    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=False)

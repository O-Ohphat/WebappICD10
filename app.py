import streamlit as st
import pandas as pd
import openai
import json

openai.api_key = st.secrets["OPENAI_API_KEY"]

model = "gpt-4-turbo"

prompt_template = '''
คุณคือผู้เชี่ยวชาญด้านการแพทย์และรหัสโรคในประเทศไทย ให้ใช้แนวทางของกระทรวงสาธารณสุข (ICD-10-TM และ ICD-9-CM TM) เท่านั้น

คำสั่งของคุณ:
1. อ่าน Progress Note ด้านล่าง แล้วแยกวินิจฉัยโรคออกมา (Dx)
2. ระบุชื่อโรคภาษาไทย และ ICD-10-TM ที่ตรงกับแต่ละ Dx
3. แยกหมวดหมู่:
   - Principal Dx (เลือกเพียง 1 โรค)
   - Comorbidity (โรคเดิม)
   - Complication (ภาวะที่เกิดใน รพ.)
   - Operation / Non-operation / Special investigation
4. ให้ข้อมูลออกมาเป็น JSON array

### Progress Note:
{note}
'''

def analyze_note(note):
    prompt = prompt_template.format(note=note)
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "คุณคือผู้เชี่ยวชาญด้านรหัสโรคในประเทศไทย"},
            {"role": "user", "content": prompt}
        ]
    )
    content = response["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except:
        return []

st.title("ICD-10-TM Autocoder 🇹🇭")
st.markdown("อัปโหลดไฟล์ Excel ที่มี Progress Note แล้วระบบจะจัดกลุ่มโรคให้ตามแบบไทย")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📄 ตัวอย่างข้อมูล:", df.head())

    if "Progress Note" in df.columns:
        all_results = []
        for note in df["Progress Note"].dropna():
            result = analyze_note(note)
            for entry in result:
                entry["Note"] = note[:50]
                all_results.append(entry)

        df_out = pd.DataFrame(all_results)
        st.success("✅ วิเคราะห์เสร็จแล้ว")
        st.dataframe(df_out)

        st.download_button(
            label="📥 ดาวน์โหลดผลลัพธ์เป็น Excel",
            data=df_out.to_excel(index=False),
            file_name="icd10_result.xlsx"
        )
    else:
        st.warning("⚠️ ไม่พบ column 'Progress Note' ในไฟล์ที่อัปโหลด")

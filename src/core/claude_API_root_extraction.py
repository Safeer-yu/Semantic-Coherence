import anthropic
import csv
import time
from dotenv import load_dotenv
import os

load_dotenv()  

api_key = os.getenv("calude_api_key")



API_KEY    = api_key
INPUT      = "missing_words.txt"
OUTPUT     = "roots_for_missing_words.csv"
BATCH      = 200
model = "claude-sonnet-4-6"

client = anthropic.Anthropic(api_key=API_KEY)

SYSTEM = """
أنت خبير في الصرف العربي. لكل كلمة أعطني الجذر وملاحظة.

قواعد الجذر:
- اكتب حروف الجذر متصلة (مثل: كتب، سءل، ءخذ)
- استخدم ء بدلاً من أ أو إ أو آ في الجذر

قواعد الملاحظة:
- إذا كانت الكلمة دخيلة أو أجنبية: اترك الجذر فارغاً واكتب في الملاحظة "دخيل"
- إذا كانت حرفاً أو أداة: اترك الجذر فارغاً واكتب نوعها في الملاحظة
- إذا كانت عامية: اكتب الجذر واكتب في الملاحظة "عامية"
- إذا كانت اسم علم: اترك الجذر فارغاً واكتب في الملاحظة "اسم علم"
- إذا كانت الكلمة واضحة الخطأ إملائياً ولا يمكن تحديد جذرها: اترك الجذر فارغاً واكتب في الملاحظة "خطأ"
- إذا كانت كلمتين أو أكثر مدموجتين معاً بدون مسافة مثل (دكتوريوسف، شهررمضان، مجموعةمتصدر):
  اترك الجذر فارغاً واكتب في الملاحظة "مدموجة"

أعد النتيجة سطراً لكل كلمة بهذا الشكل فقط، بدون أي مقدمة أو نص إضافي:
كلمة|جذر|ملاحظة

مثال:
كتب|كتب|
استأذن|ءذن|
بك||حرف جر
ديبلوماسي||دخيل
دكتوريوسف||مدموجة
شهررمضان||مدموجة"""

words = open(INPUT, encoding="utf-8").read().splitlines()
words = [w.strip() for w in words if w.strip()]
print(f"Loaded {len(words)} words")

# utf-8-sig writes BOM so Excel displays Arabic correctly
with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f).writerow(["word", "root", "note"])

done = 0
for i in range(0, len(words), BATCH):
    batch = words[i:i+BATCH]
    print(f"Batch {i//BATCH + 1} | words {i+1}–{i+len(batch)} / {len(words)}")

    try:
        r = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM,
            messages=[{"role": "user", "content": "\n".join(batch)}]
        )
        lines = r.content[0].text.strip().splitlines()

        with open(OUTPUT, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            for line in lines:
                parts = line.split("|")
                if len(parts) == 3:
                    writer.writerow(parts)
                # silently skip preamble/extra lines

        done += len(batch)
        print(f"  OK — {done} words done")

    except Exception as e:
        print(f"  Error: {e}")

    time.sleep(0.5)

print(f"\nDone! {done} words saved to {OUTPUT}")
from app.services.pdf import get_pdf_analysis
import time as tm
st = tm.time()
rag = get_pdf_analysis("D:\mini\Sample-filled-in-MR.pdf")
answer = rag.ask("")

print(answer)
et = tm.time()
print(et-st)
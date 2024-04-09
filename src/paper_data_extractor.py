from py_pdf_parser.loaders import load_file
from py_pdf_parser.visualise import visualise
from py_pdf_parser.tables import extract_table

doc = load_file("papers/test_paper.pdf")

visualise(doc)

tab = extract_table(doc.elements.filter_by_font("table_header"), as_text=True)

print(tab)
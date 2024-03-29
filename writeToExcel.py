import pandas as pd

excel_header = ["Router hostname", "IP address"]
data = [['hostname1', '1.1.1.1'], ['hostname2', '2.2.2.2']]

df = pd.DataFrame(data, columns = excel_header)
writer = pd.ExcelWriter('writePractice.xlsx', engine = 'xlsxwriter')
df.to_excel(writer, sheet_name = "router_list")
writer.close()
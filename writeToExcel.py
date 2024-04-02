# import pandas as pd

# excel_header = ["Router hostname", "IP address"]
# data = [['hostname1', '1.1.1.1'], ['hostname2', '2.2.2.2']]

# df = pd.DataFrame(data, columns = excel_header)
# writer = pd.ExcelWriter('writePractice.xlsx', engine = 'xlsxwriter')
# df.to_excel(writer, sheet_name = "router_list")
# writer.close()



stripped_price = []
meterage = []

stringList = ['180m (197yds)/100g (3.5oz)', '88m (96yds)/50g (1.8oz)', '880m (962yds)/500g (17.6oz)', '200m (219yds)/100g (3.5oz)', '166m (182yds)/100g (3.5oz)']
prices = ['£7.00', '£8.49', '£8.49', '£7.49', '£9.49']

for meters in stringList:
    index_m = meters.index("m")
    newLength = float(meters[:index_m])
    meterage.append(newLength)

print(meterage)

for old in prices:
    newPrice = float(old[1:])
    stripped_price.append(newPrice)

print(stripped_price)
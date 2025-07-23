import datetime
import pandas as pd


# def export_excel_from_driver_order_history(queryset):
#     data = []
#     for o in queryset:
#         shipping_start_date = o.driver_shipping_start_date
#         if shipping_start_date:
#             shipping_start_date = shipping_start_date.strftime("%Y-%m-%d")
#         else:
#             shipping_start_date = ""
#         data.append({
#             "id":o.id,
#             "Holati": o.get_status_display(),
#             "Mahsulot": list(o.order_products.values_list("product__name", flat=True)),
#             "Ism": o.customer_name,
#             "Tel": o.customer_phone,
#             "Tumani": o.customer_district.name,

#             "soni": o.order_products_total_ordered_amount,
#             "narxi": o.order_products_total_price,
#             "Yul_kira": o.driver_fee,
#             "bonus": o.driver_bonus_amount_won,
#             "buyurtma_kelgan_sana": o.created_at.strftime("%Y-%m-%d_%H-%M-%S"),
#             "haydovchi_ogan_sana": shipping_start_date,
#             "topshirish_sanasi": o.delivered_date.strftime("%Y-%m-%d"),
#             "sana": datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")

#         })

#     df = pd.DataFrame(data)
#     writer = pd.ExcelWriter(f'static/excel/Haydovchi_{queryset.first().driver.first_name.replace(",", "")}_buyurtma_tarihi_excel_{datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx')
#     df.to_excel(writer, index=False)
#     # worksheet = writer.sheets['Sheet1']
#     # for col in worksheet.columns:
#     #     max_length = 0
#     #     column = col[0].column_letter
#     #     for cell in col:
#     #         try:
#     #             if len(str(cell.value)) > max_length:
#     #                 max_length = len(str(cell.value))
#     #         except:
#     #             pass
#     #     adjusted_width = (max_length + 2)
#     #     worksheet.column_dimensions[column].width = adjusted_width
#     writer.save()


import xlsxwriter

def export_excel_from_driver_order_history_old(queryset):
    first = queryset.first()
    writer = pd.ExcelWriter(f'static/excel/Haydovchi_{first.driver.first_name.replace(",", "")}_buyurtma_tarihi_excel_{datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx', engine='xlsxwriter')
    data = []
    count = 0
    workbook = writer.book
    worksheet = workbook.add_worksheet('Sheet1')
    title_format = workbook.add_format({'bold': True, 'font_size': 12,
                                        'align': 'center',
                                        'valign': 'vcenter',
                                        'border': 1,
                                        'border_color': 'black',
                                        'text_wrap': True,
                                        'left': 1,
                                        'right': 1,
                                        'top': 1,
                                        'bottom': 1,
                                        'bg_color': '#F2F2F2'
                                        })
    worksheet.merge_range('A1:L1', f'Haydovchi - {first.driver.first_name} {first.driver.last_name}, Sana {datetime.datetime.today().strftime("%Y-%m-%d %H:%M")} - Buturtma soni : {queryset.count()} ta', title_format)
    for o in queryset:
        shipping_start_date = o.driver_shipping_start_date
        if shipping_start_date:
            shipping_start_date = shipping_start_date.strftime("%Y-%m-%d")
        else:
            shipping_start_date = ""
        data.append({
            "id":o.id,
            "Holati": o.get_status_display(),
            "Ism": o.customer_name,
            "Tel": o.customer_phone,
            "Tumani": o.customer_district.name,
            "soni": o.order_products_total_ordered_amount,
            "narxi": o.order_products_total_price,
            "Yul_kira": o.driver_fee,
            "bonus": o.driver_bonus_amount_won,
            
            "buyurtma_kelgan_sana": o.created_at.strftime("%Y-%m-%d_%H-%M-%S"),
            "haydovchi_ogan_sana": shipping_start_date,
            "topshirish_sanasi": o.delivered_date.strftime("%Y-%m-%d"),
            
            
        })
        if len(data) == 500: # eğer liste 500 elemana ulaştıysa
            df = pd.DataFrame(data) # listeyi bir DataFrame'e dönüştürün
            count_now = (count*500) + 1
            # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            data = [] # listeyi boşaltın
            count += 1 # sayacı artırın
    if data: # eğer liste boş değilse (son parça)
        df = pd.DataFrame(data)
        count_now = (count * 500) + 1
        # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:J', 20)
    writer.close() # dosyayı kaydedin
    
    
    

def export_excel_from_driver_order_history(queryset):
    first = queryset.first()
    writer = pd.ExcelWriter(f'static/excel/Haydovchi_{first.driver.first_name.replace(",", "")}_buyurtma_tarihi_excel_{datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx', engine='xlsxwriter')
    data = []
    count = 0
    for o in queryset:
        shipping_start_date = o.driver_shipping_start_date
        if shipping_start_date:
            shipping_start_date = shipping_start_date.strftime("%Y-%m-%d")
        else:
            shipping_start_date = ""
        data.append({
            "id":o.id,
            "Holati": o.get_status_display(),
            "Ism": o.customer_name,
            "Tumani": o.customer_district.name,
            "Mahsulot": list(o.order_products.values_list("product__name", flat=True)),
            "Tel": o.customer_phone,
            "narxi": o.order_products_total_price,
            "soni": o.order_products_total_ordered_amount,
            "Yul_kira": o.driver_fee,
            "bonus": o.driver_bonus_amount_won,
                   "buyurtma_kelgan_sana": o.created_at.strftime("%Y-%m-%d_%H-%M-%S"),
            "haydovchi_ogan_sana": shipping_start_date,
            "uzgartirish_sanasi": o.updated_at.strftime("%Y-%m-%d_%H-%M-%S"),
            
        })
        if len(data) == 500: # eğer liste 500 elemana ulaştıysa
            df = pd.DataFrame(data) # listeyi bir DataFrame'e dönüştürün
            count_now = (count*500) + 1
            # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            data = [] # listeyi boşaltın
            count += 1 # sayacı artırın
    if data: # eğer liste boş değilse (son parça)
        df = pd.DataFrame(data)
        count_now = (count * 500) + 1
        # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin


    workbook = writer.book
    # worksheet = workbook.add_worksheet('Sheet1')
    # worksheet = workbook.add_or_get_worksheet('Sheet1')
    worksheet = workbook.get_worksheet_by_name('Sheet1')
    if worksheet is None:
        worksheet = workbook.add_worksheet('Sheet1')
    title_format = workbook.add_format({'bold': True, 'font_size': 12,
                                        'align': 'center',
                                        'valign': 'vcenter',
                                        'border': 1,
                                        'border_color': 'black',
                                        'text_wrap': True,
                                        'left': 1,
                                        'right': 1,
                                        'top': 1,
                                        'bottom': 1,
                                        'bg_color': '#F2F2F2'
                                        })
    worksheet.merge_range('A1:M1', f'Haydovchi - {first.driver.first_name} {first.driver.last_name}, Sana {datetime.datetime.today().strftime("%Y-%m-%d %H:%M")} - Buturtma soni : {queryset.count()} ta', title_format)


    # workbook = writer.book
    # worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:M', 20)
    writer.close() # dosyayı kaydedin
    
    
    

def export_excel_from_driver_send_product_order_details(queryset):
    first = queryset.first()
    file_path = f'static/excel/Haydovchi_{first.driver.first_name.replace(",", "")} mahsuloti yuborilgan buyurtmalar {datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx'
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    data = []
    count = 0
    for o in queryset:
        data.append({
            "id":o.id,
            "Holati": o.get_status_display(),
            "Ism": o.customer_name,
            "Tumani": o.customer_district.name,
            "Mahsulot": list(o.order_products.values_list("product__name", flat=True)),
            "Tel": o.customer_phone,
            "narxi": o.total_product_price,
            "soni": o.total_product_quantity,
            "Yul_kira": o.driver_fee,
            "bonus": o.driver_bonus_amount_won,
            "buyurtma_kelgan_sana": o.created_at.strftime("%Y-%m-%d_%H-%M-%S"),
            "topshirish_sanasi": o.delivered_date.strftime("%Y-%m-%d"),

        })
        if len(data) == 500: # eğer liste 500 elemana ulaştıysa
            df = pd.DataFrame(data) # listeyi bir DataFrame'e dönüştürün
            count_now = (count*500) + 1
            # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            data = [] # listeyi boşaltın
            count += 1 # sayacı artırın
    if data: # eğer liste boş değilse (son parça)
        df = pd.DataFrame(data)
        count_now = (count * 500) + 1
        # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin

    workbook = writer.book
    worksheet = workbook.get_worksheet_by_name('Sheet1')
    if worksheet is None:
        worksheet = workbook.add_worksheet('Sheet1')
    title_format = workbook.add_format({'bold': True, 'font_size': 12,
                                        'align': 'center',
                                        'valign': 'vcenter',
                                        'border': 1,
                                        'border_color': 'black',
                                        'text_wrap': True,
                                        'left': 1,
                                        'right': 1,
                                        'top': 1,
                                        'bottom': 1,
                                        'bg_color': '#F2F2F2'
                                        })
    worksheet.merge_range('A1:I1', f'Haydovchi - {first.driver.first_name} {first.driver.last_name}, Sana {datetime.datetime.today().strftime("%Y-%m-%d %H:%M")} - Buturtma soni : {queryset.count()} ta', title_format)
    worksheet.set_column('A:L', 20)
    writer.close() # dosyayı kaydedin
    return file_path
    
    
    

def export_excel_from_warehouse_residue(warehouse_name, leave_product_input_price, leave_product_count, queryset):
    file_path = f'static/excel/{warehouse_name} qoldig\'i sana : {datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx'
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    data = []
    count = 0
    for o in queryset:
        data.append({
            "Mahsulot":o.product.name,
            "Rangi": o.product_variable.color.name if o.product_variable.color else '-',
            "Razmeri": o.product_variable.measure_item.name if o.product_variable.measure_item else '-',
            "Ombordagi_soni": o.amount,
            "Kirim_narxlari": [f"{i['leave_amount']} ta {i['input_price']} dan," for i in o.get_input_price_list.values("leave_amount", "input_price")],
            "Jami_kirim_narxda": o.total_input_price_uzs,
        })
        if len(data) == 500: # eğer liste 500 elemana ulaştıysa
            df = pd.DataFrame(data) # listeyi bir DataFrame'e dönüştürün
            count_now = (count*500) + 1
            # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
            data = [] # listeyi boşaltın
            count += 1 # sayacı artırın
    if data: # eğer liste boş değilse (son parça)
        df = pd.DataFrame(data)
        count_now = (count * 500) + 1
        # df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count*500) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=count_now) # DataFrame'i Excel dosyasına yazdırın, başlangıç satırını belirleyin

    workbook = writer.book
    worksheet = workbook.get_worksheet_by_name('Sheet1')
    if worksheet is None:
        worksheet = workbook.add_worksheet('Sheet1')
    title_format = workbook.add_format({'bold': True, 'font_size': 12,
                                        'align': 'center',
                                        'valign': 'vcenter',
                                        'border': 1,
                                        'border_color': 'black',
                                        'text_wrap': True,
                                        'left': 1,
                                        'right': 1,
                                        'top': 1,
                                        'bottom': 1,
                                        'bg_color': '#F2F2F2'
                                        })
    worksheet.merge_range('A1:G1', f'Ombor - {warehouse_name}, Jami mahsulotlar kirim narxda : {leave_product_input_price}, Jami qoldiq mahsulotlar soni {leave_product_count}, Sana {datetime.datetime.today().strftime("%Y-%m-%d %H:%M")}', title_format)
    worksheet.set_column('A:G', 20)
    writer.close() # dosyayı kaydedin
    return file_path
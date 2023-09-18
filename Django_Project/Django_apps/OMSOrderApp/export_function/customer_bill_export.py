from Database.mssql_handler import *


def customer_bill_export_function():
    #  if needed, add [platform_barcode] as 平台代码 into the query
    base_sql = """
        select 
        [cbl_add_time] as 发生时间
        ,cbl_ft.[customer_code] as 客户代码
        ,[cbl_refer_code] as 参考号
        ,[product_barcode] as 产品SKU
        ,[op_quantity] as 产品数量
        ,[product_origin_weight] as 产品单重
        ,cbl_ft.[ft_name_cn] as 费用类型
        ,[cbl_type] as 流水类型
        ,[cbl_transaction_value] as 结算金额
        ,[currency_code] as 结算币种
        ,[cbl_current_value] as 账户余额
        ,[cbl_note] as 备注
        from 
        (
            SELECT
                    [customer_code]
                    ,[cbl_type] 
                    ,[cbl_transaction_value]
                    ,[currency_code]
                    ,[cbl_note]
                    ,cbl.[ft_code]
                    ,ft.[ft_name_cn]
                    ,[cbl_current_value]
                    ,[application_code]
                    ,[cbl_refer_code]
                    ,[cbl_add_time]
                    ,[transaction_number]
            FROM [ECANGWMS].[dbo].[customer_balance_log] cbl
    
            left join (
                SELECT [ft_code] ,[ft_name_cn]
                FROM [ECANGWMS].[dbo].[fee_type]
            )ft on cbl.[ft_code] = ft.[ft_code]
        )cbl_ft
    
        left join 
        (
            SELECT 
                [order_code]
                ,[product_barcode]
                ,[platform_barcode]
                ,[op_quantity]
                ,[product_origin_weight]
            FROM [ECANGWMS].[dbo].[order_product]
        ) op 
        on cbl_ft.cbl_refer_code = op.[order_code]
    
        where cbl_ft.customer_code = 'XCH' and cbl_ft.cbl_add_time > '2022-01-01' and cbl_ft.cbl_add_time < '2022-02-01' 
        order by cbl_ft.cbl_add_time desc
    """
    try:
        with MssqlHandler(ip_address="192.168.167.197", database_name="ECANGWMS") as db:
            result_df = db.read_sql_by_sqlalchemy(base_sql)
            # print(result_df)
            result_df.loc[result_df['流水类型'] == 2, '流水类型'] = "扣款"
            result_df.loc[result_df['流水类型'] == 3, '流水类型'] = "入款"
            # with pd.ExcelWriter('test_export.xlsx') as writer:
            result_df.to_excel("static/InventoryApp/bill_files/test_export.xlsx", sheet_name="Bill", index=False)
    except Exception as e:
        print(e)



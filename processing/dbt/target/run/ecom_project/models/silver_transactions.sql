
  
    
    

    create  table
      "warehouse"."main"."silver_transactions__dbt_tmp"
  
    as (
      select * 
from read_parquet(
    'C:/Users/Arjun Raj M/Documents/ecom-data-platform/data/parquet/*.parquet',
    union_by_name=True
)
    );
  
  
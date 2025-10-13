-- Question Source: https://datalemur.com/questions/total-utilization-time

with table1 as (
select
server_id, status_time as stop_time, session_status, 
LAG(status_time) OVER(PARTITION BY server_id ORDER BY status_time) AS start_time
from server_utilization
order by 1,2
), 

table2 as (
select server_id, start_time, stop_time, TIMESTAMPDIFF(SECOND,start_time, stop_time) as runtime
from table1 where session_status = 'stop'
)

select ROUND(sum(runtime)/86400,0) total_uptime_days from table2
-- Question Source: https://datalemur.com/questions/sql-second-highest-salary
-- EASY

--My solution
WITH rankedsalary AS (
SELECT salary, RANK() OVER(ORDER BY salary DESC) AS rank
FROM employee
)
SELECT DISTINCT salary AS second_highest_salary FROM rankedsalary 
WHERE rank = 2;

--Alternate Solution
SELECT MAX(salary) AS second_highest_salary
FROM employee
WHERE salary < (
    SELECT MAX(salary)
    FROM employee
);

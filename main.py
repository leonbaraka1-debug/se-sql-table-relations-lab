# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# STEP 1: Employees in the Boston office
df_boston = pd.read_sql("""
    SELECT e.firstName, e.jobTitle
    FROM employees AS e
    JOIN offices AS o
        ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
    ORDER BY e.firstName;
""", conn)

# STEP 2: Offices with zero employees
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM offices AS o
    LEFT JOIN employees AS e
        ON o.officeCode = e.officeCode
    WHERE e.employeeNumber IS NULL;
""", conn)

# STEP 3: All employees with their office city/state (if they have one)
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o
        ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""", conn)

# STEP 4: Customers who have not placed an order
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, c.phone,
        c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""", conn)

# STEP 5: Payments sorted by amount (amount is stored as text, so CAST it)
df_payment = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName,
        p.amount, p.paymentDate
    FROM customers AS c
    JOIN payments AS p
        ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)

# STEP 6: Employees whose customers average a credit limit over 90k
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName,
        COUNT(c.customerNumber) AS n_customers
    FROM employees AS e
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY n_customers DESC;
""", conn)

# STEP 7: Top-selling products
df_product_sold = pd.read_sql("""
    SELECT p.productName,
        COUNT(od.orderNumber) AS numorders,
        SUM(od.quantityOrdered) AS totalunits
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC;
""", conn)

# STEP 8: Market reach: distinct customers per product
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode,
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    JOIN orders AS o
        ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC;
""", conn)

# STEP 9: Customers per office
df_customers = pd.read_sql("""
    SELECT COUNT(c.customerNumber) AS n_customers,
        o.officeCode, o.city
    FROM offices AS o
    JOIN employees AS e
        ON o.officeCode = e.officeCode
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city;
""", conn)

# STEP 10: Employees who sold products ordered by fewer than 20 customers
df_under_20 = pd.read_sql("""
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName,
        o.city, o.officeCode
    FROM employees AS e
    JOIN offices AS o
        ON e.officeCode = o.officeCode
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders AS ord
        ON c.customerNumber = ord.customerNumber
    JOIN orderdetails AS od
        ON ord.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od2.productCode
        FROM orderdetails AS od2
        JOIN orders AS o2
            ON od2.orderNumber = o2.orderNumber
        GROUP BY od2.productCode
        HAVING COUNT(DISTINCT o2.customerNumber) < 20
    )
    ORDER BY e.lastName;
""", conn)

# STEP 11: Close the connection
conn.close()
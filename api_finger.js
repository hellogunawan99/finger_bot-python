const express = require('express');
const mysql = require('mysql2');

const app = express();
const PORT = process.env.PORT || 3000;

// MySQL connection
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'root',
  database: 'db_finger'
});

// Connect to MySQL
connection.connect((err) => {
  if (err) {
    console.error('Error connecting to MySQL: ' + err.stack);
    return;
  }
  console.log('Connected to MySQL as id ' + connection.threadId);
});

// Middleware to parse JSON request body
app.use(express.json());

// Route to get all employees
app.get('/api/employees', (req, res) => {
  const sql = 'SELECT * FROM employees';
  connection.query(sql, (error, results) => {
    if (error) {
      console.error('Error querying MySQL: ' + error.stack);
      res.status(500).json({ error: 'Internal Server Error' });
      return;
    }
    res.json(results);
  });
});

// Route to create a new employee
app.post('/api/employees', (req, res) => {
  const { name, department } = req.body;
  const sql = 'INSERT INTO employees (name, department) VALUES (?, ?)';
  const values = [name, department];
  connection.query(sql, values, (error, result) => {
    if (error) {
      console.error('Error inserting into MySQL: ' + error.stack);
      res.status(500).json({ error: 'Internal Server Error' });
      return;
    }
    res.status(201).json({ id: result.insertId, name, department });
  });
});

// Route to get all finger-in and finger-out events for an employee
app.get('/api/employees/:employeeId/finger-records', (req, res) => {
  const employeeId = req.params.employeeId;
  const sql = 'SELECT * FROM finger_records WHERE employee_id = ?';
  connection.query(sql, [employeeId], (error, results) => {
    if (error) {
      console.error('Error querying MySQL: ' + error.stack);
      res.status(500).json({ error: 'Internal Server Error' });
      return;
    }
    res.json(results);
  });
});
// Route to get all finger-in and finger-out events for a specific department
app.get('/api/employees/department/:departmentName/finger-records', (req, res) => {
  const departmentName = req.params.departmentName;
  const sql = `
    SELECT fr.*, e.name AS employee_name, e.department
    FROM finger_records fr
    INNER JOIN employees e ON fr.employee_id = e.id
    WHERE e.department LIKE ?
  `;
  connection.query(sql, [`%${departmentName}%`], (error, results) => {
    if (error) {
      console.error('Error querying MySQL: ' + error.stack);
      res.status(500).json({ error: 'Internal Server Error' });
      return;
    }
    res.json(results);
  });
});


  

// Route to create a new finger-in or finger-out event for an employee
app.post('/api/employees/:employeeId/finger-records', (req, res) => {
  const employeeId = req.params.employeeId;
  const { event_type } = req.body;
  const sql = 'INSERT INTO finger_records (employee_id, event_type, event_time) VALUES (?, ?, NOW())';
  const values = [employeeId, event_type];
  connection.query(sql, values, (error, result) => {
    if (error) {
      console.error('Error inserting into MySQL: ' + error.stack);
      res.status(500).json({ error: 'Internal Server Error' });
      return;
    }
    res.status(201).json({ id: result.insertId, employee_id: employeeId, event_type });
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

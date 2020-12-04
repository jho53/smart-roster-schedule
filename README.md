## Background

### **Company Profile**
Smart Roster is a startup company created by a group of women (nurses) that want to solve the problem of inefficient scheduling in hospitals. This particular project will be trialed in the NICU at BC Women's Hospital.

### **Project Description**
The project aim is to develop a web-based application that will match scheduled nurses with a patient assignment, considering variables such as skill set, patient need, and consistency of assignments. The goal would be to reduce time spent creating patient assignments, decrease the number of unintentional errors, and decrease the number of nurses assigned to a patient during their stay. This program would need to be user friendly for a variety of computer literacy levels, have the ability to update in real-time, consider irregular schedules, and meet health authority privacy requirements.

> *Further information about project background can be found in the Project Outline Word document*


## Technology Stack + Dependencies
- MySQL 8.0.1
- Python 3.8
  - mysql-connector 
  - Flask
  - Jinja
- JavaScript 
  - jQuery
  - Datatables API
  - Bootstrap
- CSS
  - Bootstrap
  - SASS

### **Installation**
#### MySQL
Follow the instructions in this [link](https://dev.mysql.com/downloads/mysql/) to install the MySQL Community Server. <br>
Once the server is correctly set up, import all `.sql` files from the `SQL Import Files` folder. If set up correctly, there should be a `smartroster` database, with `nurses`, `patients`, `reference_page` and `users` tables. 

#### Python Dependencies
If on Windows, run `dependencies.bat` to install the dependencies required for Python. For Linux and MacOS users, please refer to `main.py` to determine the dependencies required.

#### *Accessing the Application*
The root account credentials are `charge_nurse` and `Password1`.

### Known Bugs/Stretch Goals
- Stretch Goals (Things we didn't have time to get to)
  - Database update functionality with future shift templates
  - Edit Patient/Nurse button and modal in current Patient/Nurse assignment page
  - Option to have 2 nurses assigned to 1 patient
  - Machine Learning Algorithm to avoid local optima
  - Containerize application with Docker for easy deployment
  - Database Replication in local network (to support multiple computers)
  - Using Previous Nurse/Patient Assignment table to store and retrieve the data (currently storing ID in a list)
- Known Bugs
  - Past Assignment Sheets does not correctly load `base.html` content
  - Assignment algorithm does not consider edge cases, currently only suited for assignments with a reasonable patient and nurse ratio
  - Past patients column does not update after finalizing a current shift

<br>

## Authors
**Term 4s**
- Jimmy Ho
- Eugene Joy
- Zachery Johnston

**Term 3s**
- Jaguar Perlas
- Miguel Capaz
- Nick Janus
- Nathan Broyles
